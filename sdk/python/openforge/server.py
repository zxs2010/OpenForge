"""Dependency-free HTTP server for the OpenForge reference node."""

from __future__ import annotations

import json
import re
import secrets
import socket
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import unquote, urlsplit

from openforge.gateway import OpenForgeGateway
from openforge.models import OpenForgeError, ValidationError
from openforge.store import ConcurrentUpdateError, RecordNotFoundError

MAX_REQUEST_BYTES = 64 * 1024
_IDENTIFIER_ROUTE = r"([A-Za-z0-9][A-Za-z0-9._:-]{0,127})"
_ACTIVATE_ROUTE = re.compile(rf"^/api/v1/intents/{_IDENTIFIER_ROUTE}/activate$")
_ACTIVITY_ROUTE = re.compile(rf"^/api/v1/activities/{_IDENTIFIER_ROUTE}$")
_EVENT_ROUTE = re.compile(rf"^/api/v1/activities/{_IDENTIFIER_ROUTE}/events$")


class OpenForgeHTTPServer(ThreadingHTTPServer):
    """Threaded reference server carrying one application service."""

    daemon_threads = True
    allow_reuse_address = True

    def __init__(
        self,
        address: tuple[str, int],
        gateway: OpenForgeGateway,
        web_root: Path,
    ) -> None:
        self.gateway = gateway
        self.web_root = web_root
        super().__init__(address, OpenForgeRequestHandler)
        bound_port = int(self.server_address[1])
        self.allowed_hosts = _allowed_hosts(address[0], bound_port)
        self.write_token = secrets.token_urlsafe(32)

    def get_request(self) -> tuple[socket.socket, Any]:
        request, client_address = super().get_request()
        request.settimeout(10)
        return request, client_address


class OpenForgeRequestHandler(BaseHTTPRequestHandler):
    """Small same-origin API and explicit static-file router."""

    server: OpenForgeHTTPServer
    server_version = "OpenForge"
    sys_version = ""

    def do_GET(self) -> None:
        if not self._valid_host():
            self._error(HTTPStatus.FORBIDDEN, "invalid_host", "Host is not served by this node")
            return
        try:
            path = unquote(urlsplit(self.path).path)
            if path == "/healthz":
                self._json(HTTPStatus.OK, {"status": "ok"})
            elif path == "/api/v1/meta":
                self._json(
                    HTTPStatus.OK,
                    {
                        "name": "OpenForge",
                        "version": "0.1.0",
                        "protocol_version": "0.1",
                        "write_scope": "local-reference-node",
                        "write_token": self.server.write_token,
                    },
                )
            elif path == "/api/v1/network":
                self._json(HTTPStatus.OK, self.server.gateway.network_snapshot())
            elif path == "/api/v1/intents":
                self._json(
                    HTTPStatus.OK, {"intents": self.server.gateway.list_intents()}
                )
            elif path == "/api/v1/activities":
                self._json(
                    HTTPStatus.OK,
                    {"activities": self.server.gateway.list_activities()},
                )
            elif match := _ACTIVITY_ROUTE.fullmatch(path):
                self._json(
                    HTTPStatus.OK,
                    self.server.gateway.activity_detail(match.group(1)),
                )
            else:
                self._static(path)
        except RecordNotFoundError as exc:
            self._error(HTTPStatus.NOT_FOUND, "not_found", str(exc))
        except (OpenForgeError, ValueError) as exc:
            self._error(HTTPStatus.UNPROCESSABLE_ENTITY, "invalid_request", str(exc))

    def do_POST(self) -> None:
        if not self._valid_host():
            self._error(HTTPStatus.FORBIDDEN, "invalid_host", "Host is not served by this node")
            return
        if not self._same_origin():
            self._error(
                HTTPStatus.FORBIDDEN,
                "cross_origin_write",
                "writes must come from the same origin as this OpenForge node",
            )
            return
        if self.headers.get("Origin") is not None and not self._valid_write_token():
            self._error(
                HTTPStatus.FORBIDDEN,
                "write_token_required",
                "browser writes require this node's per-process write token",
            )
            return
        try:
            path = unquote(urlsplit(self.path).path)
            payload = self._read_json()
            if path == "/api/v1/nodes":
                self._json(
                    HTTPStatus.CREATED,
                    {"node": self.server.gateway.register_node(payload)},
                )
            elif path == "/api/v1/intents":
                self._json(HTTPStatus.CREATED, self.server.gateway.submit_intent(payload))
            elif match := _ACTIVATE_ROUTE.fullmatch(path):
                self._json(
                    HTTPStatus.CREATED,
                    self.server.gateway.activate_intent(match.group(1)),
                )
            elif match := _EVENT_ROUTE.fullmatch(path):
                self._json(
                    HTTPStatus.CREATED,
                    {
                        "event": self.server.gateway.add_activity_event(
                            match.group(1), payload
                        )
                    },
                )
            else:
                self._error(HTTPStatus.NOT_FOUND, "not_found", "route not found")
        except _RequestError as exc:
            self._error(exc.status, exc.code, exc.message)
        except ConcurrentUpdateError as exc:
            self._error(HTTPStatus.CONFLICT, "conflict", str(exc))
        except RecordNotFoundError as exc:
            self._error(HTTPStatus.NOT_FOUND, "not_found", str(exc))
        except ValidationError as exc:
            self._error(HTTPStatus.UNPROCESSABLE_ENTITY, "invalid_request", str(exc))
        except (OpenForgeError, ValueError) as exc:
            self._error(HTTPStatus.BAD_REQUEST, "bad_request", str(exc))

    def do_OPTIONS(self) -> None:
        self._error(HTTPStatus.METHOD_NOT_ALLOWED, "method_not_allowed", "OPTIONS is disabled")

    def _read_json(self) -> object:
        content_type = self.headers.get_content_type()
        if content_type != "application/json":
            raise _RequestError(
                HTTPStatus.UNSUPPORTED_MEDIA_TYPE,
                "json_required",
                "Content-Type must be application/json",
            )
        raw_length = self.headers.get("Content-Length")
        if raw_length is None:
            raise _RequestError(
                HTTPStatus.LENGTH_REQUIRED,
                "length_required",
                "Content-Length is required",
            )
        try:
            length = int(raw_length)
        except ValueError as exc:
            raise _RequestError(
                HTTPStatus.BAD_REQUEST,
                "invalid_length",
                "Content-Length must be an integer",
            ) from exc
        if length < 0:
            raise _RequestError(
                HTTPStatus.BAD_REQUEST,
                "invalid_length",
                "Content-Length must not be negative",
            )
        if length > MAX_REQUEST_BYTES:
            raise _RequestError(
                HTTPStatus.REQUEST_ENTITY_TOO_LARGE,
                "request_too_large",
                f"request body exceeds {MAX_REQUEST_BYTES} bytes",
            )
        raw = self.rfile.read(length)
        try:
            return json.loads(raw)
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise _RequestError(
                HTTPStatus.BAD_REQUEST,
                "invalid_json",
                "request body is not valid JSON",
            ) from exc

    def _same_origin(self) -> bool:
        origin = self.headers.get("Origin")
        if origin is None:
            return True
        try:
            parsed = urlsplit(origin)
            if (
                parsed.scheme not in {"http", "https"}
                or parsed.hostname is None
                or parsed.username is not None
                or parsed.password is not None
                or parsed.path not in {"", "/"}
                or parsed.query
                or parsed.fragment
            ):
                return False
            default_port = 443 if parsed.scheme == "https" else 80
            origin_authority = f"{parsed.hostname.casefold()}:{parsed.port or default_port}"
        except ValueError:
            return False
        return origin_authority == _normalize_host_header(self.headers.get("Host", ""))

    def _valid_host(self) -> bool:
        authority = _normalize_host_header(self.headers.get("Host", ""))
        return authority in self.server.allowed_hosts

    def _valid_write_token(self) -> bool:
        supplied = self.headers.get("X-OpenForge-Token", "")
        return secrets.compare_digest(supplied, self.server.write_token)

    def _static(self, path: str) -> None:
        files = {
            "/": ("index.html", "text/html; charset=utf-8"),
            "/assets/styles.css": ("styles.css", "text/css; charset=utf-8"),
            "/assets/app.js": ("app.js", "text/javascript; charset=utf-8"),
        }
        if path.startswith("/activities/"):
            path = "/"
        asset = files.get(path)
        if asset is None:
            self._error(HTTPStatus.NOT_FOUND, "not_found", "route not found")
            return
        filename, media_type = asset
        try:
            body = (self.server.web_root / filename).read_bytes()
        except OSError:
            self._error(
                HTTPStatus.SERVICE_UNAVAILABLE,
                "web_unavailable",
                "the web interface is not installed",
            )
            return
        self.send_response(HTTPStatus.OK)
        self._headers(media_type, len(body), cache="public, max-age=300")
        self.end_headers()
        self.wfile.write(body)

    def _json(self, status: HTTPStatus, payload: Any) -> None:
        body = json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode()
        self.send_response(status)
        self._headers("application/json; charset=utf-8", len(body), cache="no-store")
        self.end_headers()
        self.wfile.write(body)

    def _error(self, status: HTTPStatus, code: str, message: str) -> None:
        self._json(status, {"error": {"code": code, "message": message}})

    def _headers(self, media_type: str, length: int, cache: str) -> None:
        self.send_header("Content-Type", media_type)
        self.send_header("Content-Length", str(length))
        self.send_header("Cache-Control", cache)
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header("X-Frame-Options", "DENY")
        self.send_header(
            "Content-Security-Policy",
            "default-src 'self'; script-src 'self'; style-src 'self'; "
            "img-src 'self' data:; connect-src 'self'; object-src 'none'; "
            "base-uri 'none'; frame-ancestors 'none'; form-action 'self'",
        )

    def log_message(self, format: str, *args: object) -> None:
        """Keep library use quiet; callers can put a proxy in front for access logs."""


class _RequestError(Exception):
    def __init__(self, status: HTTPStatus, code: str, message: str) -> None:
        super().__init__(message)
        self.status = status
        self.code = code
        self.message = message


def _allowed_hosts(configured_host: str, port: int) -> frozenset[str]:
    configured = configured_host.strip("[]").casefold()
    hosts = {configured}
    if configured in {"localhost", "127.0.0.1", "::1"}:
        hosts.update({"localhost", "127.0.0.1", "::1"})
    return frozenset(f"{host}:{port}" for host in hosts)


def _normalize_host_header(value: str) -> str | None:
    try:
        parsed = urlsplit(f"//{value}")
        if (
            parsed.hostname is None
            or parsed.username is not None
            or parsed.password is not None
            or parsed.path
            or parsed.query
            or parsed.fragment
        ):
            return None
        return f"{parsed.hostname.casefold()}:{parsed.port or 80}"
    except ValueError:
        return None


def create_server(
    host: str,
    port: int,
    gateway: OpenForgeGateway,
    web_root: Path | None = None,
) -> OpenForgeHTTPServer:
    """Build a configured reference server without starting its event loop."""
    if not 0 <= port <= 65_535:
        raise ValueError("port must be between 0 and 65535")
    root = web_root or Path(__file__).with_name("web")
    return OpenForgeHTTPServer((host, port), gateway, root)


def serve(host: str, port: int, gateway: OpenForgeGateway) -> None:
    """Run until interrupted by the local operator."""
    server = create_server(host, port, gateway)
    address, bound_port = server.server_address[:2]
    address_text = address.decode() if isinstance(address, bytes) else address
    print(f"OpenForge V1 is running at http://{address_text}:{bound_port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
