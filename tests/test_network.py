from __future__ import annotations

import pytest
from openforge.models import ValidationError
from openforge.network import (
    ActivityState,
    ConnectionStatus,
    Intent,
    IntentState,
    NetworkNode,
    NodeKind,
)


def test_network_node_normalizes_capabilities_and_serializes() -> None:
    node = NetworkNode(
        id="provider:comic-drama",
        name="Comic Drama Studio",
        kind=NodeKind.PROVIDER,
        summary="An independently hosted production system.",
        capabilities=("video.generate", "video.generate", "script.write"),
        status=ConnectionStatus.CONNECTED,
        origin_url="https://example.test/studio",
        created_at="2026-08-31T00:00:00Z",
    )

    assert node.capabilities == ("script.write", "video.generate")
    assert node.to_dict()["kind"] == "provider"
    assert node.to_dict()["connection_status"] == "connected"


@pytest.mark.parametrize("url", ["javascript:alert(1)", "file:///tmp/private", "//example.test"])
def test_network_node_rejects_unsafe_origin_urls(url: str) -> None:
    with pytest.raises(ValidationError, match="http or https"):
        NetworkNode(
            id="node:unsafe",
            name="Unsafe",
            kind=NodeKind.PROJECT,
            summary="Rejected external node.",
            capabilities=("project.coordinate",),
            origin_url=url,
        )


def test_intent_requires_a_meaningful_summary() -> None:
    with pytest.raises(ValidationError, match="summary"):
        Intent(id="intent:empty", summary="  ", desired_capabilities=())


def test_lifecycle_values_are_explicit() -> None:
    assert IntentState.ACTIVATED.value == "activated"
    assert ActivityState.AWAITING_REVIEW.value == "awaiting_review"
