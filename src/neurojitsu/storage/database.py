"""Transactional local storage with optional SQLCipher enforcement."""

from __future__ import annotations

import hashlib
import json
import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from neurojitsu.core.models import FeedbackRecord, SessionWindow

_SCHEMA = """
PRAGMA foreign_keys = ON;
PRAGMA journal_mode = WAL;

CREATE TABLE IF NOT EXISTS participants (
    participant_id TEXT PRIMARY KEY,
    synthetic INTEGER NOT NULL CHECK (synthetic IN (0, 1)),
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS sessions (
    session_id TEXT PRIMARY KEY,
    participant_id TEXT NOT NULL REFERENCES participants(participant_id),
    state TEXT NOT NULL,
    started_at TEXT NOT NULL,
    ended_at TEXT,
    protocol_version TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS windows (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL REFERENCES sessions(session_id),
    participant_id TEXT NOT NULL REFERENCES participants(participant_id),
    timestamp_start TEXT NOT NULL,
    timestamp_end TEXT NOT NULL,
    phase TEXT NOT NULL,
    identity_status TEXT NOT NULL,
    payload_json TEXT NOT NULL,
    payload_sha256 TEXT NOT NULL,
    UNIQUE(session_id, participant_id, timestamp_start, phase)
);

CREATE TABLE IF NOT EXISTS feedback (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL REFERENCES sessions(session_id),
    participant_id TEXT NOT NULL REFERENCES participants(participant_id),
    recorded_at TEXT NOT NULL,
    payload_json TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS reports (
    session_id TEXT PRIMARY KEY REFERENCES sessions(session_id),
    participant_id TEXT NOT NULL REFERENCES participants(participant_id),
    generated_at TEXT NOT NULL,
    report_json TEXT NOT NULL,
    report_html TEXT NOT NULL,
    reviewed INTEGER NOT NULL DEFAULT 0 CHECK (reviewed IN (0, 1))
);

CREATE TABLE IF NOT EXISTS audit_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    occurred_at TEXT NOT NULL,
    actor_role TEXT NOT NULL,
    action TEXT NOT NULL,
    resource_type TEXT NOT NULL,
    resource_id TEXT NOT NULL,
    metadata_json TEXT NOT NULL
);
"""


class Database:
    """Small repository layer that keeps all writes transactional."""

    def __init__(
        self,
        path: str | Path,
        key: str | None = None,
        allow_unencrypted_synthetic_only: bool = True,
    ) -> None:
        self.path = Path(path)
        self.key = key
        self.allow_unencrypted_synthetic_only = allow_unencrypted_synthetic_only
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._driver = sqlite3
        self.encrypted = False

        if key:
            try:
                from sqlcipher3 import dbapi2 as sqlcipher_driver
            except ImportError as exc:
                raise RuntimeError(
                    "A database key was supplied, but SQLCipher is not installed. "
                    "Install the sqlcipher extra before storing real participant data."
                ) from exc
            self._driver = sqlcipher_driver
            self.encrypted = True

        with self.connection() as connection:
            connection.executescript(_SCHEMA)

    @contextmanager
    def connection(self) -> Iterator[Any]:
        connection = self._driver.connect(str(self.path))
        try:
            connection.row_factory = sqlite3.Row
            if self.key:
                escaped = self.key.replace("'", "''")
                connection.execute(f"PRAGMA key = '{escaped}'")
                connection.execute("PRAGMA cipher_memory_security = ON")
            yield connection
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def register_participant(self, participant_id: str, synthetic: bool) -> None:
        if not synthetic and not self.encrypted:
            raise PermissionError("Real participant records require SQLCipher encryption")
        if synthetic and not self.encrypted and not self.allow_unencrypted_synthetic_only:
            raise PermissionError("Unencrypted storage is disabled")
        with self.connection() as connection:
            connection.execute(
                "INSERT OR IGNORE INTO participants VALUES (?, ?, ?)",
                (participant_id, int(synthetic), datetime.now(UTC).isoformat()),
            )
        self.audit("system", "participant.register", "participant", participant_id, {"synthetic": synthetic})

    def create_session(
        self,
        session_id: str,
        participant_id: str,
        started_at: datetime,
        protocol_version: str = "0.1.0-research",
    ) -> None:
        with self.connection() as connection:
            connection.execute(
                """INSERT INTO sessions
                (session_id, participant_id, state, started_at, ended_at, protocol_version)
                VALUES (?, ?, 'created', ?, NULL, ?)""",
                (session_id, participant_id, started_at.isoformat(), protocol_version),
            )
        self.audit("system", "session.create", "session", session_id, {})

    def set_session_state(self, session_id: str, state: str, ended_at: datetime | None = None) -> None:
        with self.connection() as connection:
            cursor = connection.execute(
                "UPDATE sessions SET state = ?, ended_at = COALESCE(?, ended_at) WHERE session_id = ?",
                (state, ended_at.isoformat() if ended_at else None, session_id),
            )
            if cursor.rowcount != 1:
                raise KeyError(f"Session not found: {session_id}")
        self.audit("system", "session.state", "session", session_id, {"state": state})

    def store_windows(self, windows: list[SessionWindow]) -> int:
        rows = []
        for window in windows:
            payload = window.model_dump_json()
            rows.append(
                (
                    window.session_id,
                    window.participant_id,
                    window.timestamp_start.isoformat(),
                    window.timestamp_end.isoformat(),
                    window.phase.value,
                    window.identity_status.value,
                    payload,
                    hashlib.sha256(payload.encode("utf-8")).hexdigest(),
                )
            )
        with self.connection() as connection:
            connection.executemany(
                """INSERT OR REPLACE INTO windows
                (session_id, participant_id, timestamp_start, timestamp_end, phase,
                 identity_status, payload_json, payload_sha256)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                rows,
            )
        if rows:
            self.audit("system", "windows.store", "session", rows[0][0], {"count": len(rows)})
        return len(rows)

    def load_windows(self, session_id: str) -> list[SessionWindow]:
        with self.connection() as connection:
            rows = connection.execute(
                "SELECT payload_json, payload_sha256 FROM windows WHERE session_id = ? ORDER BY timestamp_start",
                (session_id,),
            ).fetchall()
        windows: list[SessionWindow] = []
        for row in rows:
            payload = str(row["payload_json"])
            digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()
            if digest != row["payload_sha256"]:
                raise ValueError("Stored window failed integrity verification")
            windows.append(SessionWindow.model_validate_json(payload))
        self.audit("researcher", "windows.read", "session", session_id, {"count": len(windows)})
        return windows

    def store_feedback(self, feedback: FeedbackRecord) -> None:
        payload = feedback.model_dump_json()
        with self.connection() as connection:
            connection.execute(
                """INSERT INTO feedback
                (session_id, participant_id, recorded_at, payload_json)
                VALUES (?, ?, ?, ?)""",
                (
                    feedback.session_id,
                    feedback.participant_id,
                    feedback.recorded_at.isoformat(),
                    payload,
                ),
            )
        self.audit("researcher", "feedback.store", "session", feedback.session_id, {})

    def store_report(self, session_id: str, participant_id: str, report_json: str, report_html: str) -> None:
        with self.connection() as connection:
            connection.execute(
                """INSERT OR REPLACE INTO reports
                (session_id, participant_id, generated_at, report_json, report_html, reviewed)
                VALUES (?, ?, ?, ?, ?, 0)""",
                (session_id, participant_id, datetime.now(UTC).isoformat(), report_json, report_html),
            )
        self.audit("system", "report.store", "session", session_id, {})

    def get_report(self, session_id: str) -> dict[str, str | int] | None:
        with self.connection() as connection:
            row = connection.execute(
                "SELECT report_json, report_html, reviewed FROM reports WHERE session_id = ?",
                (session_id,),
            ).fetchone()
        self.audit("researcher", "report.read", "session", session_id, {})
        return dict(row) if row else None

    def list_sessions(self) -> list[dict[str, Any]]:
        with self.connection() as connection:
            rows = connection.execute(
                "SELECT session_id, participant_id, state, started_at, ended_at FROM sessions ORDER BY started_at DESC"
            ).fetchall()
        return [dict(row) for row in rows]

    def audit(
        self,
        actor_role: str,
        action: str,
        resource_type: str,
        resource_id: str,
        metadata: dict[str, Any],
    ) -> None:
        with self.connection() as connection:
            connection.execute(
                """INSERT INTO audit_log
                (occurred_at, actor_role, action, resource_type, resource_id, metadata_json)
                VALUES (?, ?, ?, ?, ?, ?)""",
                (
                    datetime.now(UTC).isoformat(),
                    actor_role,
                    action,
                    resource_type,
                    resource_id,
                    json.dumps(metadata, ensure_ascii=False, sort_keys=True),
                ),
            )
