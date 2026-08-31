"""Small SQLite repository for an OpenForge reference node."""

from __future__ import annotations

import json
import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import replace
from pathlib import Path

from openforge.network import (
    Activity,
    ActivityEvent,
    ActivityState,
    Intent,
    IntentState,
    NetworkNode,
)


class RecordNotFoundError(LookupError):
    """Raised when a requested network record does not exist."""


class ConcurrentUpdateError(RuntimeError):
    """Raised when an activity changed after a caller read it."""


class SQLiteNetworkStore:
    """Persistence for the reference node using one connection per operation."""

    def __init__(self, path: Path) -> None:
        self.path = path.resolve()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.path, timeout=5)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        return connection

    @contextmanager
    def _session(self, *, immediate: bool = False) -> Iterator[sqlite3.Connection]:
        connection = self._connect()
        try:
            if immediate:
                connection.execute("BEGIN IMMEDIATE")
            yield connection
            connection.commit()
        except BaseException:
            connection.rollback()
            raise
        finally:
            connection.close()

    def _initialize(self) -> None:
        with self._session() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS nodes (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    kind TEXT NOT NULL,
                    summary TEXT NOT NULL,
                    capabilities TEXT NOT NULL,
                    connection_status TEXT NOT NULL,
                    origin_url TEXT,
                    created_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS intents (
                    id TEXT PRIMARY KEY,
                    summary TEXT NOT NULL,
                    desired_capabilities TEXT NOT NULL,
                    state TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS activities (
                    id TEXT PRIMARY KEY,
                    intent_id TEXT NOT NULL UNIQUE,
                    title TEXT NOT NULL,
                    state TEXT NOT NULL,
                    participant_ids TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    FOREIGN KEY (intent_id) REFERENCES intents(id)
                );
                CREATE TABLE IF NOT EXISTS activity_events (
                    id TEXT PRIMARY KEY,
                    activity_id TEXT NOT NULL,
                    kind TEXT NOT NULL,
                    message TEXT NOT NULL,
                    actor_node_id TEXT,
                    artifact_url TEXT,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (activity_id) REFERENCES activities(id),
                    FOREIGN KEY (actor_node_id) REFERENCES nodes(id)
                );
                CREATE INDEX IF NOT EXISTS events_by_activity
                    ON activity_events(activity_id, created_at, id);
                """
            )

    def put_node(self, node: NetworkNode) -> None:
        with self._session() as connection:
            connection.execute(
                """
                INSERT INTO nodes VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    name = excluded.name,
                    kind = excluded.kind,
                    summary = excluded.summary,
                    capabilities = excluded.capabilities,
                    connection_status = excluded.connection_status,
                    origin_url = excluded.origin_url,
                    created_at = excluded.created_at
                """,
                _node_values(node),
            )

    def put_seed_node(self, node: NetworkNode) -> None:
        """Refresh managed catalog fields without rewriting first-seen time."""
        with self._session() as connection:
            connection.execute(
                """
                INSERT INTO nodes VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    name = excluded.name,
                    kind = excluded.kind,
                    summary = excluded.summary,
                    capabilities = excluded.capabilities,
                    connection_status = excluded.connection_status,
                    origin_url = excluded.origin_url
                """,
                _node_values(node),
            )

    def get_node(self, node_id: str) -> NetworkNode:
        with self._session() as connection:
            row = connection.execute("SELECT * FROM nodes WHERE id = ?", (node_id,)).fetchone()
        if row is None:
            raise RecordNotFoundError(f"unknown node: {node_id}")
        return _node(row)

    def list_nodes(self) -> tuple[NetworkNode, ...]:
        with self._session() as connection:
            rows = connection.execute(
                "SELECT * FROM nodes ORDER BY kind, name COLLATE NOCASE, id"
            ).fetchall()
        return tuple(_node(row) for row in rows)

    def put_intent(self, intent: Intent) -> None:
        with self._session() as connection:
            connection.execute(
                """
                INSERT INTO intents VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    summary = excluded.summary,
                    desired_capabilities = excluded.desired_capabilities,
                    state = excluded.state,
                    created_at = excluded.created_at
                """,
                _intent_values(intent),
            )

    def get_intent(self, intent_id: str) -> Intent:
        with self._session() as connection:
            row = connection.execute(
                "SELECT * FROM intents WHERE id = ?", (intent_id,)
            ).fetchone()
        if row is None:
            raise RecordNotFoundError(f"unknown intent: {intent_id}")
        return _intent(row)

    def list_intents(self) -> tuple[Intent, ...]:
        with self._session() as connection:
            rows = connection.execute(
                "SELECT * FROM intents ORDER BY created_at DESC, id DESC"
            ).fetchall()
        return tuple(_intent(row) for row in rows)

    def put_activity(self, activity: Activity) -> None:
        with self._session() as connection:
            connection.execute(
                """
                INSERT INTO activities VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    intent_id = excluded.intent_id,
                    title = excluded.title,
                    state = excluded.state,
                    participant_ids = excluded.participant_ids,
                    created_at = excluded.created_at,
                    updated_at = excluded.updated_at
                """,
                _activity_values(activity),
            )

    def get_activity(self, activity_id: str) -> Activity:
        with self._session() as connection:
            row = connection.execute(
                "SELECT * FROM activities WHERE id = ?", (activity_id,)
            ).fetchone()
        if row is None:
            raise RecordNotFoundError(f"unknown activity: {activity_id}")
        return _activity(row)

    def get_activity_by_intent(self, intent_id: str) -> Activity | None:
        with self._session() as connection:
            row = connection.execute(
                "SELECT * FROM activities WHERE intent_id = ?", (intent_id,)
            ).fetchone()
        return None if row is None else _activity(row)

    def list_activities(self) -> tuple[Activity, ...]:
        with self._session() as connection:
            rows = connection.execute(
                "SELECT * FROM activities ORDER BY updated_at DESC, id DESC"
            ).fetchall()
        return tuple(_activity(row) for row in rows)

    def open_activity_for_intent(
        self,
        intent: Intent,
        activity: Activity,
        event: ActivityEvent,
    ) -> Activity:
        """Create an activity, activate its intent, and append its first event atomically."""
        with self._session(immediate=True) as connection:
            row = connection.execute(
                "SELECT * FROM activities WHERE intent_id = ?", (intent.id,)
            ).fetchone()
            if row is not None:
                return _activity(row)
            connection.execute(
                "INSERT INTO activities VALUES (?, ?, ?, ?, ?, ?, ?)",
                _activity_values(activity),
            )
            updated = connection.execute(
                "UPDATE intents SET state = ? WHERE id = ?",
                (IntentState.ACTIVATED.value, intent.id),
            )
            if updated.rowcount != 1:
                raise RecordNotFoundError(f"unknown intent: {intent.id}")
            connection.execute(
                "INSERT INTO activity_events VALUES (?, ?, ?, ?, ?, ?, ?)",
                _event_values(event),
            )
        return activity

    def append_activity_event(
        self,
        event: ActivityEvent,
        *,
        expected_state: ActivityState,
        next_state: ActivityState | None,
    ) -> Activity:
        """Append an event and update its activity using one guarded transaction."""
        with self._session(immediate=True) as connection:
            row = connection.execute(
                "SELECT * FROM activities WHERE id = ?", (event.activity_id,)
            ).fetchone()
            if row is None:
                raise RecordNotFoundError(f"unknown activity: {event.activity_id}")
            current = _activity(row)
            if current.state is not expected_state:
                raise ConcurrentUpdateError(
                    f"activity changed from {expected_state.value} to {current.state.value}"
                )
            updated_activity = replace(
                current,
                state=next_state or current.state,
                updated_at=event.created_at,
            )
            updated = connection.execute(
                """
                UPDATE activities SET state = ?, updated_at = ?
                WHERE id = ? AND state = ?
                """,
                (
                    updated_activity.state.value,
                    updated_activity.updated_at,
                    updated_activity.id,
                    expected_state.value,
                ),
            )
            if updated.rowcount != 1:
                raise ConcurrentUpdateError(f"activity changed while appending {event.id}")
            connection.execute(
                "INSERT INTO activity_events VALUES (?, ?, ?, ?, ?, ?, ?)",
                _event_values(event),
            )
        return updated_activity

    def append_event(self, event: ActivityEvent) -> None:
        with self._session() as connection:
            connection.execute(
                "INSERT OR IGNORE INTO activity_events VALUES (?, ?, ?, ?, ?, ?, ?)",
                _event_values(event),
            )

    def list_events(self, activity_id: str) -> tuple[ActivityEvent, ...]:
        with self._session() as connection:
            rows = connection.execute(
                """
                SELECT * FROM activity_events
                WHERE activity_id = ?
                ORDER BY created_at, id
                """,
                (activity_id,),
            ).fetchall()
        return tuple(_event(row) for row in rows)


def _encode(values: tuple[str, ...]) -> str:
    return json.dumps(values, separators=(",", ":"))


def _node_values(node: NetworkNode) -> tuple[str, str, str, str, str, str, str | None, str]:
    return (
        node.id,
        node.name,
        node.kind.value,
        node.summary,
        _encode(node.capabilities),
        node.status.value,
        node.origin_url,
        node.created_at,
    )


def _intent_values(intent: Intent) -> tuple[str, str, str, str, str]:
    return (
        intent.id,
        intent.summary,
        _encode(intent.desired_capabilities),
        intent.state.value,
        intent.created_at,
    )


def _activity_values(activity: Activity) -> tuple[str, str, str, str, str, str, str]:
    return (
        activity.id,
        activity.intent_id,
        activity.title,
        activity.state.value,
        _encode(activity.participant_ids),
        activity.created_at,
        activity.updated_at,
    )


def _event_values(
    event: ActivityEvent,
) -> tuple[str, str, str, str, str | None, str | None, str]:
    return (
        event.id,
        event.activity_id,
        event.kind,
        event.message,
        event.actor_node_id,
        event.artifact_url,
        event.created_at,
    )


def _node(row: sqlite3.Row) -> NetworkNode:
    return NetworkNode(
        id=row["id"],
        name=row["name"],
        kind=row["kind"],
        summary=row["summary"],
        capabilities=tuple(json.loads(row["capabilities"])),
        status=row["connection_status"],
        origin_url=row["origin_url"],
        created_at=row["created_at"],
    )


def _intent(row: sqlite3.Row) -> Intent:
    return Intent(
        id=row["id"],
        summary=row["summary"],
        desired_capabilities=tuple(json.loads(row["desired_capabilities"])),
        state=row["state"],
        created_at=row["created_at"],
    )


def _activity(row: sqlite3.Row) -> Activity:
    return Activity(
        id=row["id"],
        intent_id=row["intent_id"],
        title=row["title"],
        state=row["state"],
        participant_ids=tuple(json.loads(row["participant_ids"])),
        created_at=row["created_at"],
        updated_at=row["updated_at"],
    )


def _event(row: sqlite3.Row) -> ActivityEvent:
    return ActivityEvent(
        id=row["id"],
        activity_id=row["activity_id"],
        kind=row["kind"],
        message=row["message"],
        actor_node_id=row["actor_node_id"],
        artifact_url=row["artifact_url"],
        created_at=row["created_at"],
    )
