from __future__ import annotations

from openforge.network import (
    Activity,
    ActivityEvent,
    ActivityState,
    ConnectionStatus,
    Intent,
    IntentState,
    NetworkNode,
    NodeKind,
)
from openforge.store import SQLiteNetworkStore


def test_store_round_trips_network_records(tmp_path) -> None:
    store = SQLiteNetworkStore(tmp_path / "openforge.db")
    node = NetworkNode(
        id="human:reviewer",
        name="Human Reviewer",
        kind=NodeKind.HUMAN,
        summary="Reviews final creative work.",
        capabilities=("creative.review",),
        status=ConnectionStatus.CLAIMED,
        created_at="2026-08-31T00:00:00Z",
    )
    intent = Intent(
        id="intent:launch",
        summary="Launch a public creative activity",
        desired_capabilities=("creative.review",),
        state=IntentState.MATCHED,
        created_at="2026-08-31T00:01:00Z",
    )
    activity = Activity(
        id="activity:launch",
        intent_id=intent.id,
        title="Launch a public creative activity",
        state=ActivityState.RECRUITING,
        participant_ids=(node.id,),
        created_at="2026-08-31T00:02:00Z",
        updated_at="2026-08-31T00:02:00Z",
    )
    event = ActivityEvent(
        id="event:one",
        activity_id=activity.id,
        kind="activity.opened",
        message="The activity room opened.",
        actor_node_id=node.id,
        created_at="2026-08-31T00:03:00Z",
    )

    store.put_node(node)
    store.put_intent(intent)
    store.put_activity(activity)
    store.append_event(event)

    assert store.get_node(node.id) == node
    assert store.get_intent(intent.id) == intent
    assert store.get_activity(activity.id) == activity
    assert store.list_events(activity.id) == (event,)


def test_put_node_updates_mutable_connection_metadata(tmp_path) -> None:
    store = SQLiteNetworkStore(tmp_path / "openforge.db")
    imported = NetworkNode(
        id="project:external",
        name="External Project",
        kind=NodeKind.PROJECT,
        summary="Imported from a public manifest.",
        capabilities=("video.generate",),
        status=ConnectionStatus.IMPORTED,
        created_at="2026-08-31T00:00:00Z",
    )
    connected = NetworkNode(
        id=imported.id,
        name=imported.name,
        kind=imported.kind,
        summary="Connected through its public API.",
        capabilities=imported.capabilities,
        status=ConnectionStatus.CONNECTED,
        created_at=imported.created_at,
    )

    store.put_node(imported)
    store.put_node(connected)

    assert store.get_node(imported.id) == connected
    assert len(store.list_nodes()) == 1
