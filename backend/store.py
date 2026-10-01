from __future__ import annotations

import hashlib
import json
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

SCHEMA_VERSION = 1


def utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def fingerprint(value: Any) -> str:
    if isinstance(value, dict):
        value = {k: v for k, v in value.items() if k not in {"created_at", "updated_at"}}
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


class EvidenceStore:
    def __init__(self, db_path: Path):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    @contextmanager
    def connect(self):
        con = sqlite3.connect(self.db_path)
        con.row_factory = sqlite3.Row
        con.execute("PRAGMA foreign_keys=ON")
        try:
            yield con
            con.commit()
        finally:
            con.close()

    def _init_db(self) -> None:
        with self.connect() as con:
            con.executescript(
                """
                CREATE TABLE IF NOT EXISTS meta (
                  key TEXT PRIMARY KEY,
                  value TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS evidence (
                  evidence_id TEXT PRIMARY KEY,
                  payload_json TEXT NOT NULL,
                  payload_hash TEXT NOT NULL,
                  created_at TEXT NOT NULL,
                  updated_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS evidence_versions (
                  version_id INTEGER PRIMARY KEY AUTOINCREMENT,
                  evidence_id TEXT NOT NULL,
                  payload_json TEXT NOT NULL,
                  payload_hash TEXT NOT NULL,
                  archived_at TEXT NOT NULL,
                  FOREIGN KEY(evidence_id) REFERENCES evidence(evidence_id)
                );
                CREATE VIRTUAL TABLE IF NOT EXISTS evidence_fts USING fts5(
                  evidence_id UNINDEXED,
                  capability,
                  artifact,
                  explanation,
                  tags,
                  source
                );
                """
            )
            con.execute(
                "INSERT INTO meta(key,value) VALUES('schema_version', ?) ON CONFLICT(key) DO UPDATE SET value=excluded.value",
                (str(SCHEMA_VERSION),),
            )

    @staticmethod
    def normalize_record(record: dict[str, Any]) -> dict[str, Any]:
        record = dict(record)
        if not record.get("evidence_id"):
            raise ValueError("evidence_id is required")
        required = ["capability", "artifact", "authoritative_source", "status_freshness", "interview_safe_explanation"]
        missing = [k for k in required if not str(record.get(k, "")).strip()]
        if missing:
            raise ValueError(f"missing required evidence fields: {', '.join(missing)}")
        record.setdefault("source_pointer", record.get("authoritative_source"))
        record.setdefault("durable_receipts", [])
        if isinstance(record.get("durable_receipt"), str) and record["durable_receipt"].strip():
            record["durable_receipts"] = [x.strip() for x in record["durable_receipt"].split(";") if x.strip()]
        if not isinstance(record.get("durable_receipts"), list):
            raise ValueError("durable_receipts must be a list")
        record.setdefault("artifact_hash", None)
        record.setdefault("source_hash", None)
        record.setdefault("visibility", "HOUSE")
        record.setdefault("tags", [])
        if not isinstance(record.get("tags"), list):
            raise ValueError("tags must be a list")
        now = utcnow()
        record.setdefault("created_at", now)
        record["updated_at"] = now
        return record

    def _refresh_fts(self, con: sqlite3.Connection, record: dict[str, Any]) -> None:
        con.execute("DELETE FROM evidence_fts WHERE evidence_id=?", (record["evidence_id"],))
        con.execute(
            "INSERT INTO evidence_fts(evidence_id,capability,artifact,explanation,tags,source) VALUES(?,?,?,?,?,?)",
            (
                record["evidence_id"],
                record.get("capability", ""),
                record.get("artifact", ""),
                record.get("interview_safe_explanation", ""),
                " ".join(map(str, record.get("tags", []))),
                " ".join(filter(None, [str(record.get("authoritative_source", "")), str(record.get("source_pointer", ""))])),
            ),
        )

    def upsert(self, record: dict[str, Any]) -> tuple[dict[str, Any], bool]:
        normalized = self.normalize_record(record)
        eid = normalized["evidence_id"]
        with self.connect() as con:
            existing = con.execute("SELECT * FROM evidence WHERE evidence_id=?", (eid,)).fetchone()
            if existing:
                old = json.loads(existing["payload_json"])
                normalized["created_at"] = old.get("created_at", existing["created_at"])
            h = fingerprint(normalized)
            if existing and existing["payload_hash"] == h:
                return json.loads(existing["payload_json"]), False
            if existing:
                con.execute(
                    "INSERT INTO evidence_versions(evidence_id,payload_json,payload_hash,archived_at) VALUES(?,?,?,?)",
                    (eid, existing["payload_json"], existing["payload_hash"], utcnow()),
                )
                con.execute(
                    "UPDATE evidence SET payload_json=?,payload_hash=?,updated_at=? WHERE evidence_id=?",
                    (canonical_json(normalized), h, normalized["updated_at"], eid),
                )
            else:
                con.execute(
                    "INSERT INTO evidence(evidence_id,payload_json,payload_hash,created_at,updated_at) VALUES(?,?,?,?,?)",
                    (eid, canonical_json(normalized), h, normalized["created_at"], normalized["updated_at"]),
                )
            self._refresh_fts(con, normalized)
            return normalized, True

    def import_seed(self, seed_path: Path) -> dict[str, int]:
        if not seed_path.exists():
            return {"seen": 0, "inserted_or_updated": 0}
        payload = json.loads(seed_path.read_text(encoding="utf-8"))
        records = payload.get("records", [])
        changed = 0
        for r in records:
            _, did_change = self.upsert(r)
            changed += int(did_change)
        return {"seen": len(records), "inserted_or_updated": changed}

    def get(self, evidence_id: str) -> dict[str, Any] | None:
        with self.connect() as con:
            row = con.execute("SELECT payload_json FROM evidence WHERE evidence_id=?", (evidence_id,)).fetchone()
            return json.loads(row[0]) if row else None

    def list(self) -> list[dict[str, Any]]:
        with self.connect() as con:
            rows = con.execute("SELECT payload_json FROM evidence ORDER BY evidence_id").fetchall()
            return [json.loads(r[0]) for r in rows]

    def versions(self, evidence_id: str) -> list[dict[str, Any]]:
        with self.connect() as con:
            rows = con.execute(
                "SELECT version_id,payload_json,payload_hash,archived_at FROM evidence_versions WHERE evidence_id=? ORDER BY version_id DESC",
                (evidence_id,),
            ).fetchall()
            return [
                {"version_id": r[0], "payload": json.loads(r[1]), "payload_hash": r[2], "archived_at": r[3]}
                for r in rows
            ]

    @staticmethod
    def _fts_query(query: str) -> str:
        tokens = ["".join(ch for ch in token if ch.isalnum() or ch in "_-°") for token in query.split()]
        tokens = [t for t in tokens if t]
        return " OR ".join(f'"{t}"*' for t in tokens[:12])

    def search(self, query: str, limit: int = 8) -> list[dict[str, Any]]:
        query = query.strip()
        if not query:
            return []
        fts_q = self._fts_query(query)
        with self.connect() as con:
            rows: Iterable[sqlite3.Row]
            if fts_q:
                try:
                    rows = con.execute(
                        "SELECT evidence_id,bm25(evidence_fts) AS rank FROM evidence_fts WHERE evidence_fts MATCH ? ORDER BY rank LIMIT ?",
                        (fts_q, limit),
                    ).fetchall()
                except sqlite3.OperationalError:
                    rows = []
            else:
                rows = []
            ids = [r[0] for r in rows]
            if not ids:
                like = f"%{query.lower()}%"
                raw = con.execute("SELECT evidence_id,payload_json FROM evidence ORDER BY evidence_id").fetchall()
                ids = [r[0] for r in raw if like.strip("%") in r[1].lower()][:limit]
        return [r for eid in ids if (r := self.get(eid)) is not None]

    def export_projection(self, output_path: Path) -> dict[str, Any]:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "version": SCHEMA_VERSION,
            "generated_at": utcnow(),
            "control": "Demonstrated capability != claimed skill. UNKNOWN/HOLD over inference.",
            "records": self.list(),
        }
        output_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        return payload
