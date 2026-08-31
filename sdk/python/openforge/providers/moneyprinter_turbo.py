"""OpenForge adapter for the MoneyPrinterTurbo HTTP API."""

from __future__ import annotations

import json
import math
import os
from collections.abc import Mapping
from hashlib import sha256
from threading import Lock
from typing import Any, Protocol
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import HTTPRedirectHandler, Request, build_opener

from openforge.models import (
    Artifact,
    CancellationResult,
    CostEstimate,
    JobNotReadyError,
    JobRequest,
    JobResult,
    JobState,
    JobStatus,
    ProviderDescriptor,
    ProviderError,
    Receipt,
    ValidationError,
    validate_identifier,
)

MAX_RESPONSE_BYTES = 1024 * 1024
_UPSTREAM_STATES = {
    -1: JobState.FAILED,
    1: JobState.SUCCEEDED,
    4: JobState.RUNNING,
}
_ALLOWED_ASPECT_RATIOS = {"16:9", "9:16", "1:1"}


class ProviderResponseError(ProviderError):
    """Raised when MoneyPrinterTurbo returns an invalid or failed response."""


class JsonTransport(Protocol):
    """Small injectable JSON transport used by the adapter."""

    def request(
        self,
        method: str,
        path: str,
        *,
        payload: Mapping[str, Any] | None = None,
        headers: Mapping[str, str] | None = None,
    ) -> Mapping[str, Any]:
        """Send one JSON request and return a decoded object."""


class _RejectRedirects(HTTPRedirectHandler):
    def redirect_request(
        self,
        req: Request,
        fp: Any,
        code: int,
        msg: str,
        headers: Any,
        newurl: str,
    ) -> None:
        return None


class JsonHttpTransport:
    """Bounded JSON-over-HTTP transport with redirects disabled."""

    def __init__(
        self,
        *,
        base_url: str = "http://127.0.0.1:8080",
        api_key: str | None = None,
        timeout_seconds: float = 30.0,
        max_response_bytes: int = MAX_RESPONSE_BYTES,
    ) -> None:
        self.base_url = _normalize_base_url(base_url)
        if not math.isfinite(timeout_seconds) or not 0 < timeout_seconds <= 300:
            raise ValueError("timeout_seconds must be between 0 and 300")
        if not 1 <= max_response_bytes <= 10 * MAX_RESPONSE_BYTES:
            raise ValueError("max_response_bytes is outside the allowed range")
        self.timeout_seconds = timeout_seconds
        self.max_response_bytes = max_response_bytes
        self._default_headers: dict[str, str] = {"accept": "application/json"}
        if api_key:
            self._default_headers["x-api-key"] = api_key
        self._opener = build_opener(_RejectRedirects())

    def __repr__(self) -> str:
        return (
            f"JsonHttpTransport(base_url={self.base_url!r}, "
            f"timeout_seconds={self.timeout_seconds!r}, api_key=<redacted>)"
        )

    def request(
        self,
        method: str,
        path: str,
        *,
        payload: Mapping[str, Any] | None = None,
        headers: Mapping[str, str] | None = None,
    ) -> Mapping[str, Any]:
        if method not in {"GET", "POST"}:
            raise ValueError("HTTP method is not allowed")
        if not path.startswith("/") or ".." in path or "\\" in path or "://" in path:
            raise ValueError("provider request path is invalid")
        request_headers = dict(self._default_headers)
        request_headers.update(headers or {})
        body = None
        if payload is not None:
            body = json.dumps(payload, separators=(",", ":")).encode("utf-8")
            request_headers["content-type"] = "application/json"
        request = Request(
            f"{self.base_url}{path}",
            data=body,
            headers=request_headers,
            method=method,
        )
        try:
            with self._opener.open(request, timeout=self.timeout_seconds) as response:
                raw = response.read(self.max_response_bytes + 1)
        except HTTPError as exc:
            raise ProviderResponseError(f"MoneyPrinterTurbo returned HTTP {exc.code}") from exc
        except (TimeoutError, URLError, OSError) as exc:
            raise ProviderResponseError("MoneyPrinterTurbo is unavailable") from exc
        if len(raw) > self.max_response_bytes:
            raise ProviderResponseError("MoneyPrinterTurbo response exceeded the size limit")
        try:
            decoded = json.loads(raw)
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise ProviderResponseError("MoneyPrinterTurbo returned invalid JSON") from exc
        if not isinstance(decoded, Mapping):
            raise ProviderResponseError("MoneyPrinterTurbo response must be a JSON object")
        return decoded


class MoneyPrinterTurboProvider:
    """Normalize MoneyPrinterTurbo v1 task APIs to OpenForge Provider v0.1."""

    _descriptor = ProviderDescriptor(
        id="community.moneyprinter-turbo",
        name="MoneyPrinterTurbo",
        version="0.1.0",
        capabilities=("video.generate",),
    )

    def __init__(
        self,
        *,
        base_url: str = "http://127.0.0.1:8080",
        api_key: str | None = None,
        transport: JsonTransport | None = None,
    ) -> None:
        self.base_url = _normalize_base_url(base_url)
        resolved_api_key = (
            api_key if api_key is not None else os.getenv("MONEYPRINTER_TURBO_API_KEY")
        )
        self.transport = transport or JsonHttpTransport(
            base_url=self.base_url,
            api_key=resolved_api_key,
        )
        self._idempotency_lock = Lock()
        self._idempotency: dict[str, tuple[str, JobStatus]] = {}

    @property
    def descriptor(self) -> ProviderDescriptor:
        return self._descriptor

    def estimate_cost(self, request: JobRequest) -> CostEstimate:
        self._validate_request(request)
        return CostEstimate(
            available=False,
            amount=None,
            currency=None,
            assumptions=(
                "MoneyPrinterTurbo v1 does not expose a complete cost-estimation endpoint.",
            ),
        )

    def create_job(self, request: JobRequest) -> JobStatus:
        self._validate_request(request)
        payload = self._to_upstream_payload(request)
        fingerprint = _request_fingerprint(request, payload)
        with self._idempotency_lock:
            existing = self._idempotency.get(request.request_id)
            if existing is not None:
                existing_fingerprint, existing_status = existing
                if existing_fingerprint != fingerprint:
                    raise ProviderResponseError(
                        "request_id was already used with a different job payload"
                    )
                return existing_status
            response = self.transport.request(
                "POST",
                "/api/v1/videos",
                payload=payload,
                headers={"x-task-id": request.request_id},
            )
            data = _unwrap_response(response)
            task_id = data.get("task_id")
            if not isinstance(task_id, str):
                raise ProviderResponseError("MoneyPrinterTurbo response is missing task_id")
            validate_identifier(task_id, "task_id")
            status = JobStatus(job_id=task_id, state=JobState.QUEUED, progress=0)
            self._idempotency[request.request_id] = (fingerprint, status)
            return status

    def get_status(self, job_id: str) -> JobStatus:
        data = self._fetch_task(job_id)
        return _status_from_upstream(data)

    def cancel_job(self, job_id: str) -> CancellationResult:
        validate_identifier(job_id, "job_id")
        return CancellationResult(
            job_id=job_id,
            accepted=False,
            reason="MoneyPrinterTurbo v1 does not expose cancellation for a running task.",
        )

    def get_result(self, job_id: str) -> JobResult:
        data = self._fetch_task(job_id)
        status = _status_from_upstream(data)
        if status.state in {JobState.QUEUED, JobState.RUNNING, JobState.AWAITING_REVIEW}:
            raise JobNotReadyError(f"job {job_id!r} has not completed")
        if status.state is JobState.FAILED:
            upstream_error = data.get("error")
            message = upstream_error if isinstance(upstream_error, str) else "upstream task failed"
            raise ProviderResponseError(_safe_message(message))
        artifacts = self._artifacts_from_upstream(data)
        if not artifacts:
            raise ProviderResponseError("completed MoneyPrinterTurbo task has no video artifacts")
        return JobResult(
            job_id=job_id,
            state=JobState.SUCCEEDED,
            artifacts=artifacts,
            receipt=Receipt(
                provider_id=self.descriptor.id,
                total=None,
                currency=None,
                line_items=(),
            ),
        )

    def _validate_request(self, request: JobRequest) -> None:
        if request.kind not in self.descriptor.capabilities:
            raise ValidationError(f"unsupported job kind: {request.kind}")
        request.text_input("brief")
        aspect_ratio = request.parameters.get("aspect_ratio", "9:16")
        if aspect_ratio not in _ALLOWED_ASPECT_RATIOS:
            raise ValidationError("aspect_ratio must be 16:9, 9:16, or 1:1")
        language = request.parameters.get("language", "")
        if not isinstance(language, str) or len(language) > 64 or not language.isprintable():
            raise ValidationError("language must be a printable string up to 64 characters")
        duration = request.parameters.get("duration_seconds")
        if duration is not None and (
            isinstance(duration, bool)
            or not isinstance(duration, (int, float))
            or not math.isfinite(duration)
            or not 1 <= duration <= 3_600
        ):
            raise ValidationError("duration_seconds must be between 1 and 3600")

    def _to_upstream_payload(self, request: JobRequest) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "video_subject": request.text_input("brief"),
            "video_aspect": request.parameters.get("aspect_ratio", "9:16"),
        }
        language = request.parameters.get("language")
        if language:
            payload["video_language"] = language
        duration = request.parameters.get("duration_seconds")
        if duration is not None:
            duration_text = str(int(duration)) if float(duration).is_integer() else str(duration)
            payload["video_script_prompt"] = (
                f"Target a finished duration of about {duration_text} seconds."
            )
        script = request.optional_text_input("script")
        if script:
            payload["video_script"] = script
        return payload

    def _fetch_task(self, job_id: str) -> Mapping[str, Any]:
        validate_identifier(job_id, "job_id")
        response = self.transport.request("GET", f"/api/v1/tasks/{job_id}")
        return _unwrap_response(response)

    def _artifacts_from_upstream(self, data: Mapping[str, Any]) -> tuple[Artifact, ...]:
        values = data.get("combined_videos") or data.get("videos") or []
        if not isinstance(values, list):
            raise ProviderResponseError("MoneyPrinterTurbo video artifacts must be an array")
        artifacts: list[Artifact] = []
        for index, value in enumerate(values, start=1):
            if not isinstance(value, str) or not value.strip():
                raise ProviderResponseError("MoneyPrinterTurbo returned an invalid artifact URI")
            artifacts.append(
                Artifact(
                    id=f"video-{index}",
                    media_type="video/mp4",
                    uri=_resolve_artifact_uri(self.base_url, value),
                )
            )
        return tuple(artifacts)


def _normalize_base_url(value: str) -> str:
    parsed = urlparse(value)
    try:
        _ = parsed.port
    except ValueError as exc:
        raise ValueError(
            "base_url must be an HTTP(S) origin without credentials or a path"
        ) from exc
    if (
        parsed.scheme not in {"http", "https"}
        or not parsed.hostname
        or parsed.username is not None
        or parsed.password is not None
        or parsed.path not in {"", "/"}
        or parsed.params
        or parsed.query
        or parsed.fragment
    ):
        raise ValueError("base_url must be an HTTP(S) origin without credentials or a path")
    return value.rstrip("/")


def _unwrap_response(response: Mapping[str, Any]) -> Mapping[str, Any]:
    status = response.get("status")
    if status != 200:
        message = response.get("message")
        safe_message = _safe_message(message) if isinstance(message, str) else "request failed"
        raise ProviderResponseError(f"MoneyPrinterTurbo request failed: {safe_message}")
    data = response.get("data")
    if not isinstance(data, Mapping):
        raise ProviderResponseError("MoneyPrinterTurbo response is missing a data object")
    return data


def _status_from_upstream(data: Mapping[str, Any]) -> JobStatus:
    task_id = data.get("task_id")
    state_value = data.get("state")
    progress = data.get("progress", 0)
    if not isinstance(task_id, str):
        raise ProviderResponseError("MoneyPrinterTurbo task response is missing task_id")
    if (
        isinstance(state_value, bool)
        or not isinstance(state_value, int)
        or state_value not in _UPSTREAM_STATES
    ):
        raise ProviderResponseError(
            f"unknown MoneyPrinterTurbo task state: {state_value!r}"
        )
    state = _UPSTREAM_STATES[state_value]
    if isinstance(progress, bool) or not isinstance(progress, int) or not 0 <= progress <= 100:
        raise ProviderResponseError("MoneyPrinterTurbo progress must be an integer from 0 to 100")
    message = data.get("error") if state is JobState.FAILED else None
    return JobStatus(
        job_id=task_id,
        state=state,
        progress=progress,
        message=_safe_message(message) if isinstance(message, str) else None,
    )


def _resolve_artifact_uri(base_url: str, value: str) -> str:
    parsed = urlparse(value)
    if parsed.scheme:
        if (
            parsed.scheme not in {"http", "https"}
            or not parsed.hostname
            or parsed.username is not None
            or parsed.password is not None
        ):
            raise ProviderResponseError("MoneyPrinterTurbo returned an unsafe artifact URI")
        return value
    if not value.startswith("/tasks/") or ".." in value or "\\" in value:
        raise ProviderResponseError("MoneyPrinterTurbo returned an unsafe artifact path")
    return f"{base_url}{value}"


def _safe_message(value: str) -> str:
    printable = "".join(character for character in value if character.isprintable())
    return printable[:500] or "upstream request failed"


def _request_fingerprint(request: JobRequest, payload: Mapping[str, Any]) -> str:
    canonical_request = {
        "protocol_version": request.protocol_version,
        "kind": request.kind,
        "inputs": [
            {
                "name": item.name,
                "media_type": item.media_type,
                "value": item.value,
            }
            for item in request.inputs
        ],
        "parameters": dict(request.parameters),
        "constraints": dict(request.constraints),
        "upstream_payload": dict(payload),
    }
    try:
        encoded = json.dumps(
            canonical_request,
            allow_nan=False,
            ensure_ascii=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode("utf-8")
    except (TypeError, ValueError) as exc:
        raise ValidationError("job request must contain JSON-compatible values") from exc
    return sha256(encoded).hexdigest()
