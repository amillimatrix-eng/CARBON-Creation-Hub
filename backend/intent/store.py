from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .models import SearchSession


def utcnow() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


class SearchSessionStore:
    def __init__(self, db_path: Path):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_schema()

    def _conn(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path, timeout=15)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        return conn

    def _init_schema(self) -> None:
        with self._conn() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS search_sessions (
                    session_id TEXT PRIMARY KEY,
                    contract_version TEXT NOT NULL,
                    surface TEXT NOT NULL,
                    payload_json TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS search_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    payload_json TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS idx_search_events_session ON search_events(session_id,id);
                CREATE TABLE IF NOT EXISTS search_calibration (
                    key TEXT PRIMARY KEY,
                    positive INTEGER NOT NULL DEFAULT 0,
                    negative INTEGER NOT NULL DEFAULT 0,
                    version INTEGER NOT NULL DEFAULT 1,
                    updated_at TEXT NOT NULL
                );
                """
            )

    def save(self, session: SearchSession, event_type: str = "SESSION_SNAPSHOT", event: dict[str, Any] | None = None) -> None:
        now = utcnow()
        payload = session.model_dump(mode="json")
        with self._conn() as conn:
            conn.execute(
                """INSERT INTO search_sessions(session_id,contract_version,surface,payload_json,created_at,updated_at)
                   VALUES(?,?,?,?,?,?)
                   ON CONFLICT(session_id) DO UPDATE SET
                    contract_version=excluded.contract_version,
                    surface=excluded.surface,
                    payload_json=excluded.payload_json,
                    updated_at=excluded.updated_at""",
                (session.session_id, session.contract_version, session.surface, json.dumps(payload, sort_keys=True), session.created_at, now),
            )
            conn.execute(
                "INSERT INTO search_events(session_id,event_type,payload_json,created_at) VALUES(?,?,?,?)",
                (session.session_id, event_type, json.dumps(event or {}, sort_keys=True), now),
            )

    def get(self, session_id: str) -> SearchSession | None:
        with self._conn() as conn:
            row = conn.execute("SELECT payload_json FROM search_sessions WHERE session_id=?", (session_id,)).fetchone()
        return SearchSession.model_validate(json.loads(row["payload_json"])) if row else None

    def events(self, session_id: str) -> list[dict[str, Any]]:
        with self._conn() as conn:
            rows = conn.execute(
                "SELECT id,event_type,payload_json,created_at FROM search_events WHERE session_id=? ORDER BY id",
                (session_id,),
            ).fetchall()
        return [
            {"id": row["id"], "event_type": row["event_type"], "payload": json.loads(row["payload_json"]), "created_at": row["created_at"]}
            for row in rows
        ]

    def record_feedback(self, key: str, positive: bool) -> dict[str, Any]:
        now = utcnow()
        with self._conn() as conn:
            conn.execute(
                """INSERT INTO search_calibration(key,positive,negative,version,updated_at)
                   VALUES(?,?,?,?,?)
                   ON CONFLICT(key) DO UPDATE SET
                    positive=positive+excluded.positive,
                    negative=negative+excluded.negative,
                    version=version+1,
                    updated_at=excluded.updated_at""",
                (key, 1 if positive else 0, 0 if positive else 1, 1, now),
            )
            row = conn.execute("SELECT * FROM search_calibration WHERE key=?", (key,)).fetchone()
        return dict(row)

    def calibration(self) -> list[dict[str, Any]]:
        with self._conn() as conn:
            rows = conn.execute("SELECT * FROM search_calibration ORDER BY key").fetchall()
        return [dict(row) for row in rows]
