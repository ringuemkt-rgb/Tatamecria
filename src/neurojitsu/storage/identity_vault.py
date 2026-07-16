"""Separate SQLCipher-only identity map.

This module is deliberately independent from analytic storage so the public
research dataset can remain pseudonymized.
"""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from typing import Any


class IdentityVault:
    """Store the participant-code mapping only in a separate encrypted database."""

    def __init__(self, path: str | Path, key: str) -> None:
        if len(key) < 16:
            raise ValueError("Identity-vault key must contain at least 16 characters")
        try:
            from sqlcipher3 import dbapi2 as sqlcipher
        except ImportError as exc:  # pragma: no cover - optional dependency
            raise RuntimeError("SQLCipher is required for the identity vault") from exc

        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._driver = sqlcipher
        self._key = key
        with self._connect() as connection:
            connection.execute(
                """CREATE TABLE IF NOT EXISTS identity_map (
                participant_id TEXT PRIMARY KEY,
                encrypted_external_reference TEXT NOT NULL,
                created_at TEXT NOT NULL,
                active INTEGER NOT NULL DEFAULT 1 CHECK(active IN (0, 1))
                )"""
            )

    def _connect(self) -> Any:
        connection = self._driver.connect(str(self.path))
        escaped = self._key.replace("'", "''")
        connection.execute(f"PRAGMA key = '{escaped}'")
        connection.execute("PRAGMA cipher_memory_security = ON")
        return connection

    def put(self, participant_id: str, external_reference: str) -> None:
        with self._connect() as connection:
            connection.execute(
                """INSERT OR REPLACE INTO identity_map
                (participant_id, encrypted_external_reference, created_at, active)
                VALUES (?, ?, ?, 1)""",
                (participant_id, external_reference, datetime.now(UTC).isoformat()),
            )
            connection.commit()
