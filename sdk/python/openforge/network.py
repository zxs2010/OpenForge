"""Connection-network domain objects shared by humans and AI clients."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import TypeVar
from urllib.parse import urlparse

from openforge.models import ValidationError, validate_identifier

MAX_NAME_LENGTH = 120
MAX_SUMMARY_LENGTH = 2_000
MAX_EVENT_LENGTH = 4_000
MAX_URL_LENGTH = 2_048
MAX_CAPABILITIES = 64
EnumT = TypeVar("EnumT", bound=Enum)


def utc_now() -> str:
    """Return a stable UTC timestamp suitable for public records."""
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


class NodeKind(str, Enum):
    """Kinds of entities discoverable in the OpenForge network."""

    HUMAN = "human"
    AI = "ai"
    PROJECT = "project"
    SKILL = "skill"
    PROVIDER = "provider"
    COMPUTE = "compute"
    CHANNEL = "channel"


class ConnectionStatus(str, Enum):
    """Evidence level for a node's relationship with this network index."""

    IMPORTED = "imported"
    CLAIMED = "claimed"
    CONNECTED = "connected"
    VERIFIED = "verified"


class IntentState(str, Enum):
    """Lifecycle states for a request before and after activation."""

    OPEN = "open"
    MATCHED = "matched"
    ACTIVATED = "activated"
    CLOSED = "closed"


class ActivityState(str, Enum):
    """Community-level work states; provider jobs have their own lifecycle."""

    DRAFT = "draft"
    RECRUITING = "recruiting"
    PLANNED = "planned"
    ACTIVE = "active"
    AWAITING_REVIEW = "awaiting_review"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    FAILED = "failed"


@dataclass(frozen=True, slots=True)
class NetworkNode:
    """One independently operated entity visible through the network index."""

    id: str
    name: str
    kind: NodeKind
    summary: str
    capabilities: tuple[str, ...]
    status: ConnectionStatus = ConnectionStatus.IMPORTED
    origin_url: str | None = None
    created_at: str = field(default_factory=utc_now)

    def __post_init__(self) -> None:
        validate_identifier(self.id, "node id")
        object.__setattr__(self, "name", _clean_text(self.name, "node name", MAX_NAME_LENGTH))
        object.__setattr__(
            self, "summary", _clean_text(self.summary, "node summary", MAX_SUMMARY_LENGTH)
        )
        object.__setattr__(self, "kind", _enum_value(NodeKind, self.kind, "node kind"))
        object.__setattr__(
            self,
            "status",
            _enum_value(ConnectionStatus, self.status, "connection status"),
        )
        object.__setattr__(self, "capabilities", _capabilities(self.capabilities))
        if self.origin_url is not None:
            object.__setattr__(self, "origin_url", validate_public_url(self.origin_url))
        _validate_timestamp(self.created_at)

    def to_dict(self) -> dict[str, object]:
        return {
            "id": self.id,
            "name": self.name,
            "kind": self.kind.value,
            "summary": self.summary,
            "capabilities": list(self.capabilities),
            "connection_status": self.status.value,
            "origin_url": self.origin_url,
            "created_at": self.created_at,
        }


@dataclass(frozen=True, slots=True)
class Intent:
    """A desired outcome that can be matched before it becomes an activity."""

    id: str
    summary: str
    desired_capabilities: tuple[str, ...]
    state: IntentState = IntentState.OPEN
    created_at: str = field(default_factory=utc_now)

    def __post_init__(self) -> None:
        validate_identifier(self.id, "intent id")
        object.__setattr__(
            self, "summary", _clean_text(self.summary, "intent summary", MAX_SUMMARY_LENGTH)
        )
        object.__setattr__(
            self, "desired_capabilities", _capabilities(self.desired_capabilities)
        )
        object.__setattr__(self, "state", _enum_value(IntentState, self.state, "intent state"))
        _validate_timestamp(self.created_at)

    def to_dict(self) -> dict[str, object]:
        return {
            "id": self.id,
            "summary": self.summary,
            "desired_capabilities": list(self.desired_capabilities),
            "state": self.state.value,
            "created_at": self.created_at,
        }


@dataclass(frozen=True, slots=True)
class Match:
    """An explainable compatibility suggestion for one node."""

    node: NetworkNode
    score: int
    reasons: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.score < 0:
            raise ValidationError("match score must not be negative")
        if not self.reasons:
            raise ValidationError("match requires at least one reason")

    def to_dict(self) -> dict[str, object]:
        return {
            "node": self.node.to_dict(),
            "score": self.score,
            "reasons": list(self.reasons),
        }


@dataclass(frozen=True, slots=True)
class Activity:
    """Shared coordination space produced by activating an intent."""

    id: str
    intent_id: str
    title: str
    state: ActivityState
    participant_ids: tuple[str, ...]
    created_at: str = field(default_factory=utc_now)
    updated_at: str = field(default_factory=utc_now)

    def __post_init__(self) -> None:
        validate_identifier(self.id, "activity id")
        validate_identifier(self.intent_id, "activity intent id")
        object.__setattr__(self, "title", _clean_text(self.title, "activity title", 240))
        object.__setattr__(
            self, "state", _enum_value(ActivityState, self.state, "activity state")
        )
        participants = tuple(dict.fromkeys(self.participant_ids))
        for participant_id in participants:
            validate_identifier(participant_id, "participant node id")
        object.__setattr__(self, "participant_ids", participants)
        _validate_timestamp(self.created_at)
        _validate_timestamp(self.updated_at)

    def to_dict(self) -> dict[str, object]:
        return {
            "id": self.id,
            "intent_id": self.intent_id,
            "title": self.title,
            "state": self.state.value,
            "participant_ids": list(self.participant_ids),
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }


@dataclass(frozen=True, slots=True)
class ActivityEvent:
    """Append-only statement of meaningful progress inside an activity."""

    id: str
    activity_id: str
    kind: str
    message: str
    actor_node_id: str | None = None
    artifact_url: str | None = None
    created_at: str = field(default_factory=utc_now)

    def __post_init__(self) -> None:
        validate_identifier(self.id, "event id")
        validate_identifier(self.activity_id, "event activity id")
        validate_identifier(self.kind, "event kind")
        object.__setattr__(
            self, "message", _clean_text(self.message, "event message", MAX_EVENT_LENGTH)
        )
        if self.actor_node_id is not None:
            validate_identifier(self.actor_node_id, "event actor node id")
        if self.artifact_url is not None:
            object.__setattr__(self, "artifact_url", validate_public_url(self.artifact_url))
        _validate_timestamp(self.created_at)

    def to_dict(self) -> dict[str, object]:
        return {
            "id": self.id,
            "activity_id": self.activity_id,
            "kind": self.kind,
            "message": self.message,
            "actor_node_id": self.actor_node_id,
            "artifact_url": self.artifact_url,
            "created_at": self.created_at,
        }


def validate_public_url(value: str) -> str:
    """Allow only absolute HTTP(S) links in public domain records."""
    cleaned = _clean_text(value, "URL", MAX_URL_LENGTH)
    parsed = urlparse(cleaned)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc or parsed.username:
        raise ValidationError("URL must be an absolute http or https URL without credentials")
    return cleaned


def _clean_text(value: object, field_name: str, maximum: int) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValidationError(f"{field_name} must not be empty")
    cleaned = value.strip()
    if len(cleaned) > maximum or not cleaned.isprintable():
        raise ValidationError(f"{field_name} must be printable and at most {maximum} characters")
    return cleaned


def _capabilities(values: object) -> tuple[str, ...]:
    if isinstance(values, str) or not isinstance(values, (list, tuple)):
        raise ValidationError("capabilities must be an array")
    if len(values) > MAX_CAPABILITIES:
        raise ValidationError(f"capabilities may contain at most {MAX_CAPABILITIES} values")
    normalized: set[str] = set()
    for value in values:
        if not isinstance(value, str):
            raise ValidationError("capabilities must contain strings")
        normalized.add(validate_identifier(value, "capability"))
    return tuple(sorted(normalized))


def _enum_value(enum_type: type[EnumT], value: object, field_name: str) -> EnumT:
    try:
        return enum_type(value)
    except (TypeError, ValueError) as exc:
        allowed = ", ".join(item.value for item in enum_type)
        raise ValidationError(f"{field_name} must be one of: {allowed}") from exc


def _validate_timestamp(value: str) -> None:
    if not isinstance(value, str):
        raise ValidationError("timestamp must be text")
    try:
        datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValidationError("timestamp must use ISO 8601 format") from exc
