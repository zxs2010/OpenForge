"""Transport-neutral OpenForge protocol value objects."""

from __future__ import annotations

import re
from collections.abc import Mapping
from dataclasses import dataclass, field
from decimal import Decimal
from enum import Enum
from types import MappingProxyType
from typing import Any

MAX_IDENTIFIER_LENGTH = 128
MAX_TEXT_INPUT_LENGTH = 8_000
_IDENTIFIER_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$")


class OpenForgeError(Exception):
    """Base exception for OpenForge SDK errors."""


class ValidationError(OpenForgeError, ValueError):
    """Raised when a protocol value fails validation."""


class ProviderError(OpenForgeError):
    """Raised when a provider cannot satisfy an operation."""


class JobNotReadyError(ProviderError):
    """Raised when a result is requested before a job reaches a terminal state."""


def validate_identifier(value: str, field_name: str) -> str:
    """Return a safe protocol identifier or raise a validation error."""
    if not isinstance(value, str) or not _IDENTIFIER_PATTERN.fullmatch(value):
        raise ValidationError(
            f"{field_name} must be 1-{MAX_IDENTIFIER_LENGTH} characters using "
            "letters, numbers, dot, underscore, colon, or hyphen"
        )
    return value


class JobState(str, Enum):
    """OpenForge base lifecycle states."""

    QUEUED = "queued"
    RUNNING = "running"
    AWAITING_REVIEW = "awaiting_review"
    CANCELLING = "cancelling"
    CANCELLED = "cancelled"
    SUCCEEDED = "succeeded"
    FAILED = "failed"


@dataclass(frozen=True, slots=True)
class JobInput:
    """One named input supplied to a production job."""

    name: str
    media_type: str
    value: str

    def __post_init__(self) -> None:
        validate_identifier(self.name, "input name")
        if not isinstance(self.media_type, str) or "/" not in self.media_type:
            raise ValidationError("media_type must be a valid type/subtype string")
        if not isinstance(self.value, str):
            raise ValidationError("input value must be text in protocol v0.1")
        if len(self.value) > MAX_TEXT_INPUT_LENGTH:
            raise ValidationError(
                f"input value maximum length is {MAX_TEXT_INPUT_LENGTH} characters"
            )


@dataclass(frozen=True, slots=True)
class JobRequest:
    """A versioned, idempotent production request."""

    request_id: str
    kind: str
    inputs: tuple[JobInput, ...]
    parameters: Mapping[str, Any] = field(default_factory=dict)
    constraints: Mapping[str, Any] = field(default_factory=dict)
    protocol_version: str = "0.1"

    def __post_init__(self) -> None:
        validate_identifier(self.request_id, "request_id")
        validate_identifier(self.kind, "kind")
        if self.protocol_version != "0.1":
            raise ValidationError("protocol_version must be 0.1")
        if not isinstance(self.inputs, tuple):
            object.__setattr__(self, "inputs", tuple(self.inputs))
        names = [item.name for item in self.inputs]
        if len(names) != len(set(names)):
            raise ValidationError("job input names must be unique")
        object.__setattr__(self, "parameters", _freeze_mapping(self.parameters, "parameters"))
        object.__setattr__(self, "constraints", _freeze_mapping(self.constraints, "constraints"))

    def text_input(self, name: str) -> str:
        """Return a named text input, failing explicitly when it is absent."""
        value = self.optional_text_input(name)
        if value is not None:
            return value
        raise ValidationError(f"required text input {name!r} is missing")

    def optional_text_input(self, name: str) -> str | None:
        """Return an optional named text input while still validating its media type."""
        for item in self.inputs:
            if item.name == name:
                if not item.media_type.startswith("text/"):
                    raise ValidationError(f"input {name!r} is not text")
                return item.value
        return None


def _freeze_mapping(value: Mapping[str, Any], field_name: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise ValidationError(f"{field_name} must be an object")
    for key in value:
        validate_identifier(key, f"{field_name} key")
    return MappingProxyType(dict(value))


@dataclass(frozen=True, slots=True)
class ProviderDescriptor:
    """Identity and capabilities declared by a provider adapter."""

    id: str
    name: str
    version: str
    capabilities: tuple[str, ...]

    def __post_init__(self) -> None:
        validate_identifier(self.id, "provider id")
        if not self.name.strip():
            raise ValidationError("provider name must not be empty")
        if not self.version.strip():
            raise ValidationError("provider version must not be empty")
        for capability in self.capabilities:
            validate_identifier(capability, "provider capability")


@dataclass(frozen=True, slots=True)
class CostEstimate:
    """A provider's non-binding price estimate."""

    available: bool
    amount: Decimal | None
    currency: str | None
    assumptions: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if self.available and (self.amount is None or self.currency is None):
            raise ValidationError("available estimates require amount and currency")
        if self.amount is not None and self.amount < 0:
            raise ValidationError("estimate amount must not be negative")


@dataclass(frozen=True, slots=True)
class JobStatus:
    """Normalized observable state for one provider job."""

    job_id: str
    state: JobState
    progress: int | None = None
    message: str | None = None

    def __post_init__(self) -> None:
        validate_identifier(self.job_id, "job_id")
        if self.progress is not None and not 0 <= self.progress <= 100:
            raise ValidationError("progress must be between 0 and 100")


@dataclass(frozen=True, slots=True)
class Artifact:
    """One immutable output reference returned by a provider."""

    id: str
    media_type: str
    uri: str
    role: str = "primary"

    def __post_init__(self) -> None:
        validate_identifier(self.id, "artifact id")
        if "/" not in self.media_type:
            raise ValidationError("artifact media_type must be a type/subtype string")
        if not self.uri.strip():
            raise ValidationError("artifact uri must not be empty")


@dataclass(frozen=True, slots=True)
class Receipt:
    """Auditable final usage summary; unknown cost is represented explicitly."""

    provider_id: str
    total: Decimal | None
    currency: str | None
    line_items: tuple[Mapping[str, Any], ...] = ()

    def __post_init__(self) -> None:
        validate_identifier(self.provider_id, "provider id")
        if self.total is not None and self.total < 0:
            raise ValidationError("receipt total must not be negative")


@dataclass(frozen=True, slots=True)
class JobResult:
    """Normalized terminal result returned by a provider."""

    job_id: str
    state: JobState
    artifacts: tuple[Artifact, ...]
    receipt: Receipt

    def __post_init__(self) -> None:
        validate_identifier(self.job_id, "job_id")
        if self.state not in {JobState.SUCCEEDED, JobState.FAILED, JobState.CANCELLED}:
            raise ValidationError("job result must use a terminal state")


@dataclass(frozen=True, slots=True)
class CancellationResult:
    """Outcome of a cancellation request."""

    job_id: str
    accepted: bool
    reason: str

    def __post_init__(self) -> None:
        validate_identifier(self.job_id, "job_id")
        if not self.reason.strip():
            raise ValidationError("cancellation reason must not be empty")
