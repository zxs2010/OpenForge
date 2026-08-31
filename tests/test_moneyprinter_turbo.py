from __future__ import annotations

from collections.abc import Mapping
from typing import Any
from urllib.error import HTTPError, URLError

import pytest
from openforge.models import JobInput, JobRequest, JobState, ValidationError
from openforge.providers.moneyprinter_turbo import (
    JsonHttpTransport,
    MoneyPrinterTurboProvider,
    ProviderResponseError,
)


class FakeTransport:
    def __init__(self, *responses: Mapping[str, Any]) -> None:
        self.responses = list(responses)
        self.calls: list[dict[str, Any]] = []

    def request(
        self,
        method: str,
        path: str,
        *,
        payload: Mapping[str, Any] | None = None,
        headers: Mapping[str, str] | None = None,
    ) -> Mapping[str, Any]:
        self.calls.append(
            {
                "method": method,
                "path": path,
                "payload": dict(payload or {}),
                "headers": dict(headers or {}),
            }
        )
        return self.responses.pop(0)


class FakeHttpResponse:
    def __init__(self, body: bytes) -> None:
        self.body = body

    def __enter__(self) -> FakeHttpResponse:
        return self

    def __exit__(self, *_: object) -> None:
        return None

    def read(self, _: int) -> bytes:
        return self.body


class FakeOpener:
    def __init__(self, response: FakeHttpResponse | Exception) -> None:
        self.response = response
        self.requests: list[Any] = []

    def open(self, request: Any, *, timeout: float) -> FakeHttpResponse:
        self.requests.append((request, timeout))
        if isinstance(self.response, Exception):
            raise self.response
        return self.response


def make_request() -> JobRequest:
    return JobRequest(
        request_id="req-001",
        kind="video.generate",
        inputs=(
            JobInput(
                name="brief",
                media_type="text/plain",
                value="Create a product launch video",
            ),
        ),
        parameters={
            "aspect_ratio": "9:16",
            "duration_seconds": 15,
            "language": "zh-CN",
        },
    )


def test_create_job_maps_openforge_request_to_moneyprinter_api() -> None:
    transport = FakeTransport(
        {"status": 200, "message": "success", "data": {"task_id": "task-123"}}
    )
    provider = MoneyPrinterTurboProvider(transport=transport)

    status = provider.create_job(make_request())

    assert status.job_id == "task-123"
    assert status.state is JobState.QUEUED
    assert transport.calls == [
        {
            "method": "POST",
            "path": "/api/v1/videos",
            "payload": {
                "video_subject": "Create a product launch video",
                "video_aspect": "9:16",
                "video_language": "zh-CN",
                "video_script_prompt": "Target a finished duration of about 15 seconds.",
            },
            "headers": {"x-task-id": "req-001"},
        }
    ]


def test_create_job_is_idempotent_within_adapter_lifetime() -> None:
    transport = FakeTransport(
        {"status": 200, "message": "success", "data": {"task_id": "task-123"}}
    )
    provider = MoneyPrinterTurboProvider(transport=transport)

    first = provider.create_job(make_request())
    second = provider.create_job(make_request())

    assert first == second
    assert len(transport.calls) == 1


def test_create_job_rejects_request_id_reuse_with_different_payload() -> None:
    transport = FakeTransport(
        {"status": 200, "message": "success", "data": {"task_id": "task-123"}}
    )
    provider = MoneyPrinterTurboProvider(transport=transport)
    provider.create_job(make_request())
    changed = JobRequest(
        request_id="req-001",
        kind="video.generate",
        inputs=(
            JobInput(name="brief", media_type="text/plain", value="A different video"),
        ),
    )

    with pytest.raises(ProviderResponseError, match="request_id"):
        provider.create_job(changed)

    assert len(transport.calls) == 1


def test_idempotency_fingerprint_includes_constraints() -> None:
    transport = FakeTransport(
        {"status": 200, "message": "success", "data": {"task_id": "task-123"}}
    )
    provider = MoneyPrinterTurboProvider(transport=transport)
    original = make_request()
    provider.create_job(original)
    changed = JobRequest(
        request_id=original.request_id,
        kind=original.kind,
        inputs=original.inputs,
        parameters=original.parameters,
        constraints={"budget": "5.00"},
    )

    with pytest.raises(ProviderResponseError, match="request_id"):
        provider.create_job(changed)


@pytest.mark.parametrize(
    ("upstream_state", "expected"),
    [(4, JobState.RUNNING), (1, JobState.SUCCEEDED), (-1, JobState.FAILED)],
)
def test_get_status_maps_upstream_states(
    upstream_state: int, expected: JobState
) -> None:
    transport = FakeTransport(
        {
            "status": 200,
            "data": {
                "task_id": "task-123",
                "state": upstream_state,
                "progress": 40,
            },
        }
    )
    provider = MoneyPrinterTurboProvider(transport=transport)

    status = provider.get_status("task-123")

    assert status.state is expected
    assert status.progress == 40


def test_get_result_returns_normalized_video_artifacts() -> None:
    transport = FakeTransport(
        {
            "status": 200,
            "data": {
                "task_id": "task-123",
                "state": 1,
                "progress": 100,
                "combined_videos": ["/tasks/task-123/final.mp4"],
            },
        }
    )
    provider = MoneyPrinterTurboProvider(
        base_url="http://127.0.0.1:8080", transport=transport
    )

    result = provider.get_result("task-123")

    assert result.state is JobState.SUCCEEDED
    assert result.artifacts[0].media_type == "video/mp4"
    assert result.artifacts[0].uri == "http://127.0.0.1:8080/tasks/task-123/final.mp4"
    assert result.receipt.total is None


def test_cancel_is_explicitly_unsupported_without_deleting_upstream_task() -> None:
    transport = FakeTransport()
    provider = MoneyPrinterTurboProvider(transport=transport)

    cancellation = provider.cancel_job("task-123")

    assert cancellation.accepted is False
    assert "does not expose cancellation" in cancellation.reason
    assert transport.calls == []


def test_estimate_does_not_claim_zero_cost_when_upstream_has_no_estimator() -> None:
    provider = MoneyPrinterTurboProvider(transport=FakeTransport())

    estimate = provider.estimate_cost(make_request())

    assert estimate.available is False
    assert estimate.amount is None
    assert "does not expose" in estimate.assumptions[0]


def test_provider_rejects_malformed_success_response() -> None:
    provider = MoneyPrinterTurboProvider(
        transport=FakeTransport({"status": 200, "data": {}})
    )

    with pytest.raises(ProviderResponseError, match="task_id"):
        provider.create_job(make_request())


def test_provider_rejects_non_text_optional_script() -> None:
    transport = FakeTransport()
    provider = MoneyPrinterTurboProvider(transport=transport)
    request = JobRequest(
        request_id="req-001",
        kind="video.generate",
        inputs=(
            JobInput(name="brief", media_type="text/plain", value="Film"),
            JobInput(name="script", media_type="application/json", value="{}"),
        ),
    )

    with pytest.raises(ValidationError, match=r"script.*not text"):
        provider.create_job(request)

    assert transport.calls == []


@pytest.mark.parametrize(
    "base_url",
    [
        "file:///tmp/provider",
        "http://user:password@example.com",
        "http://example.com/path?token=secret",
        "http://localhost:notaport",
        "not-a-url",
    ],
)
def test_http_transport_rejects_unsafe_base_urls(base_url: str) -> None:
    with pytest.raises(ValueError, match="base_url"):
        JsonHttpTransport(base_url=base_url)


def test_api_key_is_sent_only_as_header_and_hidden_from_repr() -> None:
    transport = JsonHttpTransport(
        base_url="http://127.0.0.1:8080", api_key="top-secret"
    )

    assert "top-secret" not in repr(transport)


def test_http_transport_sends_bounded_json_request() -> None:
    transport = JsonHttpTransport(
        base_url="http://127.0.0.1:8080",
        api_key="top-secret",
        timeout_seconds=5,
    )
    opener = FakeOpener(FakeHttpResponse(b'{"status":200,"data":{"ok":true}}'))
    transport._opener = opener

    response = transport.request(
        "POST",
        "/api/v1/videos",
        payload={"video_subject": "Demo"},
        headers={"x-task-id": "req-001"},
    )

    request, timeout = opener.requests[0]
    assert response["data"] == {"ok": True}
    assert request.full_url == "http://127.0.0.1:8080/api/v1/videos"
    assert request.data == b'{"video_subject":"Demo"}'
    assert request.get_header("X-api-key") == "top-secret"
    assert timeout == 5


@pytest.mark.parametrize(
    ("response", "message"),
    [
        (FakeHttpResponse(b"not-json"), "invalid JSON"),
        (FakeHttpResponse(b"[]"), "JSON object"),
        (FakeHttpResponse(b"x" * 11), "size limit"),
        (URLError("offline"), "unavailable"),
        (HTTPError("http://localhost", 503, "down", {}, None), "HTTP 503"),
    ],
)
def test_http_transport_normalizes_network_and_response_failures(
    response: FakeHttpResponse | Exception, message: str
) -> None:
    transport = JsonHttpTransport(
        base_url="http://127.0.0.1:8080",
        max_response_bytes=10,
    )
    transport._opener = FakeOpener(response)

    with pytest.raises(ProviderResponseError, match=message):
        transport.request("GET", "/api/v1/tasks/task-123")


@pytest.mark.parametrize(
    ("method", "path"),
    [("DELETE", "/api/v1/tasks/task-123"), ("GET", "../secrets")],
)
def test_http_transport_rejects_unapproved_method_or_path(method: str, path: str) -> None:
    transport = JsonHttpTransport()

    with pytest.raises(ValueError):
        transport.request(method, path)


def test_result_rejects_unsafe_artifact_path() -> None:
    provider = MoneyPrinterTurboProvider(
        transport=FakeTransport(
            {
                "status": 200,
                "data": {
                    "task_id": "task-123",
                    "state": 1,
                    "progress": 100,
                    "videos": ["../../private.mp4"],
                },
            }
        )
    )

    with pytest.raises(ProviderResponseError, match="unsafe artifact path"):
        provider.get_result("task-123")
