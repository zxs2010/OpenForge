"""Application service for the OpenForge connection and activity loop."""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path
from uuid import uuid4

from openforge.catalog import ProviderCatalog
from openforge.models import ValidationError
from openforge.network import (
    Activity,
    ActivityEvent,
    ActivityState,
    ConnectionStatus,
    Intent,
    IntentState,
    NetworkNode,
    NodeKind,
    utc_now,
)
from openforge.router import IntentRouter
from openforge.store import RecordNotFoundError, SQLiteNetworkStore

_ACTIVITY_TRANSITIONS = {
    ActivityState.DRAFT: {ActivityState.RECRUITING, ActivityState.CANCELLED},
    ActivityState.RECRUITING: {
        ActivityState.PLANNED,
        ActivityState.ACTIVE,
        ActivityState.CANCELLED,
    },
    ActivityState.PLANNED: {
        ActivityState.ACTIVE,
        ActivityState.CANCELLED,
        ActivityState.FAILED,
    },
    ActivityState.ACTIVE: {
        ActivityState.AWAITING_REVIEW,
        ActivityState.COMPLETED,
        ActivityState.CANCELLED,
        ActivityState.FAILED,
    },
    ActivityState.AWAITING_REVIEW: {
        ActivityState.ACTIVE,
        ActivityState.COMPLETED,
        ActivityState.FAILED,
    },
    ActivityState.COMPLETED: set(),
    ActivityState.CANCELLED: set(),
    ActivityState.FAILED: set(),
}


class OpenForgeGateway:
    """Coordinates node discovery, intent routing, and activity records."""

    def __init__(self, store: SQLiteNetworkStore, catalog_path: Path) -> None:
        self.store = store
        self.catalog_path = catalog_path
        self.router = IntentRouter()

    def seed(self) -> None:
        """Idempotently import known providers and the self-hosting activity."""
        self.store.put_seed_node(
            NetworkNode(
                id="project.openforge",
                name="OpenForge",
                kind=NodeKind.PROJECT,
                summary="Open collaboration network for AI-native content production.",
                capabilities=("activity.host", "community.coordinate", "network.index"),
                status=ConnectionStatus.CONNECTED,
                origin_url="https://github.com/zxs2010/OpenForge",
                created_at="2026-08-31T00:00:00Z",
            )
        )
        self.store.put_seed_node(
            NetworkNode(
                id="ai.openforge-router",
                name="OpenForge Router",
                kind=NodeKind.AI,
                summary="Matches intents to declared capabilities with visible reasons.",
                capabilities=("community.coordinate", "intent.route"),
                status=ConnectionStatus.CONNECTED,
                created_at="2026-08-31T00:00:01Z",
            )
        )
        self.store.put_seed_node(
            NetworkNode(
                id="channel.openforge-github",
                name="OpenForge on GitHub",
                kind=NodeKind.CHANNEL,
                summary="Public source, issues, and contribution channel for the project.",
                capabilities=("channel.distribute", "code.host"),
                status=ConnectionStatus.CONNECTED,
                origin_url="https://github.com/zxs2010/OpenForge",
                created_at="2026-08-31T00:00:02Z",
            )
        )
        for manifest in ProviderCatalog.load(self.catalog_path).manifests:
            status = (
                ConnectionStatus.CONNECTED
                if manifest.status == "adapter-ready"
                else ConnectionStatus.IMPORTED
            )
            self.store.put_seed_node(
                NetworkNode(
                    id=manifest.id,
                    name=manifest.name,
                    kind=NodeKind.PROVIDER,
                    summary=(
                        f"Community provider catalog entry; integration status: "
                        f"{manifest.status}."
                    ),
                    capabilities=manifest.capabilities,
                    status=status,
                    origin_url=f"https://github.com/{manifest.upstream.repository}",
                    created_at="2026-08-31T00:01:00Z",
                )
            )

        try:
            self.store.get_intent("intent:openforge-v1")
        except RecordNotFoundError:
            self.store.put_intent(
                Intent(
                    id="intent:openforge-v1",
                    summary="Open and validate the first OpenForge connection network",
                    desired_capabilities=("community.coordinate", "code.host"),
                    state=IntentState.ACTIVATED,
                    created_at="2026-08-31T00:02:00Z",
                )
            )
        try:
            self.store.get_activity("activity:001")
        except RecordNotFoundError:
            self.store.put_activity(
                Activity(
                    id="activity:001",
                    intent_id="intent:openforge-v1",
                    title="Open and validate OpenForge V1",
                    state=ActivityState.ACTIVE,
                    participant_ids=(
                        "project.openforge",
                        "ai.openforge-router",
                        "channel.openforge-github",
                    ),
                    created_at="2026-08-31T00:03:00Z",
                    updated_at="2026-08-31T00:04:00Z",
                )
            )
        self.store.append_event(
            ActivityEvent(
                id="event:001-scope",
                activity_id="activity:001",
                kind="scope.accepted",
                message="V1 scope fixed: node, intent, match, activity, and receipt flow.",
                actor_node_id="project.openforge",
                created_at="2026-08-31T00:03:30Z",
            )
        )
        self.store.append_event(
            ActivityEvent(
                id="event:001-catalog",
                activity_id="activity:001",
                kind="nodes.imported",
                message="The first independent production providers were indexed.",
                actor_node_id="ai.openforge-router",
                created_at="2026-08-31T00:04:00Z",
            )
        )

    def network_snapshot(self) -> dict[str, object]:
        nodes = self.store.list_nodes()
        counts = {kind.value: 0 for kind in NodeKind}
        statuses = {status.value: 0 for status in ConnectionStatus}
        for node in nodes:
            counts[node.kind.value] += 1
            statuses[node.status.value] += 1
        return {
            "nodes": [node.to_dict() for node in nodes],
            "counts": counts,
            "connection_statuses": statuses,
        }

    def register_node(self, payload: object) -> dict[str, object]:
        data = _object(payload)
        node = NetworkNode(
            id=f"{_required(data, 'kind')}:{uuid4().hex[:12]}",
            name=_required(data, "name"),
            kind=_node_kind(_required(data, "kind")),
            summary=_required(data, "summary"),
            capabilities=_string_tuple(data.get("capabilities", ()), "capabilities"),
            status=ConnectionStatus.CLAIMED,
            origin_url=_optional_string(data.get("origin_url"), "origin_url"),
        )
        self.store.put_node(node)
        return node.to_dict()

    def submit_intent(self, payload: object) -> dict[str, object]:
        data = _object(payload)
        desired = _string_tuple(data.get("desired_capabilities", ()), "desired_capabilities")
        provisional = Intent(
            id=f"intent:{uuid4().hex[:12]}",
            summary=_required(data, "summary"),
            desired_capabilities=desired,
        )
        matches = self.router.route(provisional, self.store.list_nodes())
        intent = replace(
            provisional,
            desired_capabilities=(
                desired or self.router.infer_capabilities(provisional.summary)
            ),
            state=IntentState.MATCHED if matches else IntentState.OPEN,
        )
        self.store.put_intent(intent)
        return {
            "intent": intent.to_dict(),
            "matches": [match.to_dict() for match in matches],
        }

    def list_intents(self) -> list[dict[str, object]]:
        return [intent.to_dict() for intent in self.store.list_intents()]

    def activate_intent(self, intent_id: str) -> dict[str, object]:
        existing = self.store.get_activity_by_intent(intent_id)
        if existing is not None:
            return self.activity_detail(existing.id)
        intent = self.store.get_intent(intent_id)
        matches = self.router.route(intent, self.store.list_nodes())
        timestamp = utc_now()
        activity = Activity(
            id=f"activity:{uuid4().hex[:12]}",
            intent_id=intent.id,
            title=intent.summary,
            state=ActivityState.RECRUITING,
            participant_ids=tuple(match.node.id for match in matches),
            created_at=timestamp,
            updated_at=timestamp,
        )
        event = ActivityEvent(
            id=f"event:{uuid4().hex[:12]}",
            activity_id=activity.id,
            kind="activity.opened",
            message=(
                f"Activity opened with {len(activity.participant_ids)} matched participant"
                f"{'s' if len(activity.participant_ids) != 1 else ''}."
            ),
        )
        opened = self.store.open_activity_for_intent(intent, activity, event)
        return self.activity_detail(opened.id)

    def list_activities(self) -> list[dict[str, object]]:
        return [self._activity_summary(activity) for activity in self.store.list_activities()]

    def activity_detail(self, activity_id: str) -> dict[str, object]:
        activity = self.store.get_activity(activity_id)
        participants = [self.store.get_node(node_id) for node_id in activity.participant_ids]
        events = self.store.list_events(activity.id)
        return {
            "activity": activity.to_dict(),
            "participants": [node.to_dict() for node in participants],
            "events": [event.to_dict() for event in events],
        }

    def add_activity_event(self, activity_id: str, payload: object) -> dict[str, object]:
        data = _object(payload)
        activity = self.store.get_activity(activity_id)
        actor = _optional_string(data.get("actor_node_id"), "actor_node_id")
        if actor is not None:
            self.store.get_node(actor)
        event = ActivityEvent(
            id=f"event:{uuid4().hex[:12]}",
            activity_id=activity.id,
            kind=_required(data, "kind"),
            message=_required(data, "message"),
            actor_node_id=actor,
            artifact_url=_optional_string(data.get("artifact_url"), "artifact_url"),
        )
        next_state_value = data.get("next_state")
        if next_state_value is not None:
            try:
                next_state = ActivityState(next_state_value)
            except (TypeError, ValueError) as exc:
                raise ValidationError("next_state is not a valid activity state") from exc
            if next_state not in _ACTIVITY_TRANSITIONS[activity.state]:
                raise ValidationError(
                    f"activity cannot move from {activity.state.value} to {next_state.value}"
                )
        else:
            next_state = None
        self.store.append_activity_event(
            event,
            expected_state=activity.state,
            next_state=next_state,
        )
        return event.to_dict()

    def _activity_summary(self, activity: Activity) -> dict[str, object]:
        value = activity.to_dict()
        value["event_count"] = len(self.store.list_events(activity.id))
        return value

def _object(value: object) -> dict[str, object]:
    if not isinstance(value, dict):
        raise ValidationError("request body must be a JSON object")
    return value


def _required(value: dict[str, object], key: str) -> str:
    result = value.get(key)
    if not isinstance(result, str) or not result.strip():
        raise ValidationError(f"{key} is required")
    return result


def _optional_string(value: object, field_name: str) -> str | None:
    if value is None or value == "":
        return None
    if not isinstance(value, str):
        raise ValidationError(f"{field_name} must be text")
    return value


def _string_tuple(value: object, field_name: str) -> tuple[str, ...]:
    if not isinstance(value, list) and not isinstance(value, tuple):
        raise ValidationError(f"{field_name} must be an array")
    if not all(isinstance(item, str) for item in value):
        raise ValidationError(f"{field_name} must contain strings")
    return tuple(value)


def _node_kind(value: str) -> NodeKind:
    try:
        return NodeKind(value)
    except ValueError as exc:
        raise ValidationError("kind is not a valid node kind") from exc
