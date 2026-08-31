from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from dataclasses import replace
from pathlib import Path

from openforge.gateway import OpenForgeGateway
from openforge.network import ActivityEvent, ActivityState, ConnectionStatus, NodeKind
from openforge.store import ConcurrentUpdateError, SQLiteNetworkStore

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]


def make_gateway(tmp_path) -> OpenForgeGateway:
    return OpenForgeGateway(
        SQLiteNetworkStore(tmp_path / "openforge.db"),
        catalog_path=REPOSITORY_ROOT / "providers",
    )


def test_seed_builds_an_honest_self_hosting_activity(tmp_path) -> None:
    gateway = make_gateway(tmp_path)

    gateway.seed()
    gateway.seed()

    network = gateway.network_snapshot()
    activity = gateway.activity_detail("activity:001")
    assert network["counts"]["provider"] == 4
    assert network["counts"]["project"] == 1
    assert activity["activity"]["state"] == "active"
    assert activity["activity"]["title"] == "Open and validate OpenForge V1"
    assert len(activity["events"]) >= 2


def test_submit_intent_returns_explainable_matches(tmp_path) -> None:
    gateway = make_gateway(tmp_path)
    gateway.seed()

    result = gateway.submit_intent(
        {
            "summary": "制作一条 15 秒 AI 漫剧预告视频",
            "desired_capabilities": ["video.generate"],
        }
    )

    assert result["intent"]["state"] == "matched"
    assert result["matches"][0]["node"]["id"] == "community.moneyprinter-turbo"
    assert "video.generate" in result["matches"][0]["reasons"]
    assert result["matches"][0]["node"]["connection_status"] == "connected"


def test_activate_intent_is_idempotent_and_preserves_match_order(tmp_path) -> None:
    gateway = make_gateway(tmp_path)
    gateway.seed()
    submitted = gateway.submit_intent(
        {"summary": "Create a product video", "desired_capabilities": ["video.generate"]}
    )
    intent_id = submitted["intent"]["id"]

    first = gateway.activate_intent(intent_id)
    second = gateway.activate_intent(intent_id)

    assert first["activity"] == second["activity"]
    assert first["activity"]["state"] == "recruiting"
    assert first["activity"]["participant_ids"][0] == "community.moneyprinter-turbo"


def test_activate_intent_is_idempotent_under_concurrency(tmp_path) -> None:
    gateway = make_gateway(tmp_path)
    gateway.seed()
    submitted = gateway.submit_intent(
        {"summary": "Create a product video", "desired_capabilities": ["video.generate"]}
    )
    intent_id = submitted["intent"]["id"]

    with ThreadPoolExecutor(max_workers=8) as executor:
        results = list(executor.map(lambda _: gateway.activate_intent(intent_id), range(16)))

    activity_ids = {result["activity"]["id"] for result in results}
    assert len(activity_ids) == 1
    assert len(gateway.activity_detail(activity_ids.pop())["events"]) == 1


def test_external_node_can_join_network_without_sharing_a_repository(tmp_path) -> None:
    gateway = make_gateway(tmp_path)
    gateway.seed()

    result = gateway.register_node(
        {
            "name": "Independent Comic Drama System",
            "kind": NodeKind.PROVIDER.value,
            "summary": "Runs in its own repository and connects over HTTP.",
            "capabilities": ["video.generate", "comic-drama.produce"],
            "origin_url": "https://example.test/comic-drama",
        }
    )

    assert result["connection_status"] == ConnectionStatus.CLAIMED.value
    assert result["origin_url"] == "https://example.test/comic-drama"


def test_activity_events_move_the_shared_work_forward(tmp_path) -> None:
    gateway = make_gateway(tmp_path)
    gateway.seed()

    event = gateway.add_activity_event(
        "activity:001",
        {
            "kind": "artifact.published",
            "message": "The reference node was published.",
            "artifact_url": "https://github.com/zxs2010/OpenForge",
            "next_state": ActivityState.AWAITING_REVIEW.value,
        },
    )

    detail = gateway.activity_detail("activity:001")
    assert event["kind"] == "artifact.published"
    assert detail["activity"]["state"] == "awaiting_review"
    assert detail["events"][-1]["artifact_url"].endswith("/OpenForge")


def test_progress_event_always_refreshes_activity_timestamp(tmp_path) -> None:
    gateway = make_gateway(tmp_path)
    gateway.seed()
    before = gateway.activity_detail("activity:001")["activity"]["updated_at"]

    event = gateway.add_activity_event(
        "activity:001",
        {"kind": "progress.recorded", "message": "A connector contract was verified."},
    )

    after = gateway.activity_detail("activity:001")["activity"]["updated_at"]
    assert after == event["created_at"]
    assert after != before


def test_concurrent_activity_transitions_cannot_regress_state(tmp_path) -> None:
    gateway = make_gateway(tmp_path)
    gateway.seed()
    events = (
        ActivityEvent(
            id="event:concurrent-review",
            activity_id="activity:001",
            kind="review.requested",
            message="Review requested.",
        ),
        ActivityEvent(
            id="event:concurrent-complete",
            activity_id="activity:001",
            kind="activity.completed",
            message="Activity completed.",
        ),
    )
    with ThreadPoolExecutor(max_workers=2) as executor:
        futures = [
            executor.submit(
                gateway.store.append_activity_event,
                event,
                expected_state=ActivityState.ACTIVE,
                next_state=next_state,
            )
            for event, next_state in zip(
                events,
                (ActivityState.AWAITING_REVIEW, ActivityState.COMPLETED),
                strict=True,
            )
        ]
    results = []
    errors = []
    for future in futures:
        try:
            results.append(future.result())
        except ConcurrentUpdateError as exc:
            errors.append(exc)

    detail = gateway.activity_detail("activity:001")
    assert len(results) == 1
    assert len(errors) == 1
    assert detail["activity"]["state"] in {"awaiting_review", "completed"}
    assert detail["events"][-1]["id"] in {event.id for event in events}


def test_seed_refreshes_managed_node_metadata_without_rewriting_creation(tmp_path) -> None:
    gateway = make_gateway(tmp_path)
    gateway.seed()
    node = gateway.store.get_node("community.moneyprinter-turbo")
    gateway.store.put_node(
        replace(
            node,
            name="Stale catalog name",
            status=ConnectionStatus.IMPORTED,
            created_at="2025-01-01T00:00:00Z",
        )
    )

    gateway.seed()

    refreshed = gateway.store.get_node(node.id)
    assert refreshed.name == "MoneyPrinterTurbo"
    assert refreshed.status is ConnectionStatus.CONNECTED
    assert refreshed.created_at == "2025-01-01T00:00:00Z"
