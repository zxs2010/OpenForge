from __future__ import annotations

import json
import threading
from http.client import HTTPConnection
from pathlib import Path
from unittest.mock import patch

import pytest
from openforge.gateway import OpenForgeGateway
from openforge.server import create_server
from openforge.store import ConcurrentUpdateError, SQLiteNetworkStore

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def running_server(tmp_path):
    gateway = OpenForgeGateway(
        SQLiteNetworkStore(tmp_path / "openforge.db"),
        catalog_path=REPOSITORY_ROOT / "providers",
    )
    gateway.seed()
    server = create_server("127.0.0.1", 0, gateway)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield server
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)


def request(address, method: str, path: str, payload=None, headers=None):
    if hasattr(address, "server_address"):
        address = address.server_address
    connection = HTTPConnection(*address, timeout=2)
    body = None if payload is None else json.dumps(payload)
    request_headers = dict(headers or {})
    if body is not None:
        request_headers["Content-Type"] = "application/json"
    connection.request(method, path, body=body, headers=request_headers)
    response = connection.getresponse()
    raw = response.read()
    parsed = json.loads(raw) if response.getheader("Content-Type", "").startswith(
        "application/json"
    ) else raw.decode("utf-8")
    headers_out = dict(response.getheaders())
    connection.close()
    return response.status, headers_out, parsed


def test_health_and_network_api(running_server) -> None:
    status, headers, body = request(running_server, "GET", "/healthz")
    assert status == 200
    assert body == {"status": "ok"}
    assert headers["X-Content-Type-Options"] == "nosniff"

    status, _, body = request(running_server, "GET", "/api/v1/network")
    assert status == 200
    assert body["counts"]["provider"] == 4


def test_api_runs_intent_to_activity_loop(running_server) -> None:
    status, _, submitted = request(
        running_server,
        "POST",
        "/api/v1/intents",
        {"summary": "Create a launch video", "desired_capabilities": ["video.generate"]},
    )
    assert status == 201

    intent_id = submitted["intent"]["id"]
    status, _, activated = request(
        running_server,
        "POST",
        f"/api/v1/intents/{intent_id}/activate",
        {},
    )
    assert status == 201
    assert activated["activity"]["state"] == "recruiting"

    status, _, detail = request(
        running_server,
        "GET",
        f"/api/v1/activities/{activated['activity']['id'].replace(':', '%3A')}",
    )
    assert status == 200
    assert detail["activity"]["id"] == activated["activity"]["id"]


def test_api_rejects_cross_origin_writes(running_server) -> None:
    status, _, body = request(
        running_server,
        "POST",
        "/api/v1/intents",
        {"summary": "Create something useful"},
        {"Origin": "https://attacker.example"},
    )

    assert status == 403
    assert body["error"]["code"] == "cross_origin_write"


def test_api_rejects_dns_rebinding_and_malformed_origins(running_server) -> None:
    status, _, body = request(
        running_server,
        "POST",
        "/api/v1/intents",
        {"summary": "Mutate a loopback node"},
        {"Host": "attacker.example", "Origin": "http://attacker.example"},
    )
    assert status == 403
    assert body["error"]["code"] == "invalid_host"

    status, _, body = request(
        running_server,
        "POST",
        "/api/v1/intents",
        {"summary": "Malformed origin"},
        {"Origin": "http://["},
    )
    assert status == 403
    assert body["error"]["code"] == "cross_origin_write"


def test_browser_writes_require_the_node_token(running_server) -> None:
    host = f"127.0.0.1:{running_server.server_address[1]}"
    status, _, body = request(running_server, "GET", "/api/v1/meta")
    assert status == 200
    token = body["write_token"]

    status, _, body = request(
        running_server,
        "POST",
        "/api/v1/intents",
        {"summary": "Same-origin browser request"},
        {"Origin": f"http://{host}"},
    )
    assert status == 403
    assert body["error"]["code"] == "write_token_required"

    status, _, body = request(
        running_server,
        "POST",
        "/api/v1/intents",
        {"summary": "Same-origin browser request"},
        {"Origin": f"http://{host}", "X-OpenForge-Token": token},
    )
    assert status == 201
    assert body["intent"]["summary"] == "Same-origin browser request"


def test_concurrent_updates_return_a_structured_conflict(running_server) -> None:
    with patch.object(
        running_server.gateway,
        "add_activity_event",
        side_effect=ConcurrentUpdateError("activity changed while appending an event"),
    ):
        status, _, body = request(
            running_server,
            "POST",
            "/api/v1/activities/activity%3A001/events",
            {"kind": "progress.recorded", "message": "Concurrent update"},
        )

    assert status == 409
    assert body["error"]["code"] == "conflict"


def test_api_rejects_non_json_and_oversized_requests(running_server) -> None:
    status, _, body = request(
        running_server,
        "POST",
        "/api/v1/intents",
        None,
        {"Content-Type": "text/plain"},
    )
    assert status == 415
    assert body["error"]["code"] == "json_required"

    connection = HTTPConnection(*running_server.server_address, timeout=2)
    connection.request(
        "POST",
        "/api/v1/intents",
        body=b"{}",
        headers={"Content-Type": "application/json", "Content-Length": "70000"},
    )
    response = connection.getresponse()
    assert response.status == 413
    connection.close()


def test_server_serves_the_community_gateway(running_server) -> None:
    status, headers, body = request(running_server, "GET", "/")
    assert status == 200
    assert "OPENFORGE" in body
    assert "Content-Security-Policy" in headers

    status, _, javascript = request(running_server, "GET", "/assets/app.js")
    assert status == 200
    assert "Route this intent" in javascript
    assert "match.reasons.join" in javascript
    assert "No route yet" in javascript
