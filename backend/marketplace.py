from __future__ import annotations

import hashlib
import json
import os
import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

from fastapi import APIRouter, FastAPI, Header, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field, model_validator


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def iso(dt: datetime | None = None) -> str:
    return (dt or utcnow()).astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def parse_time(value: str) -> datetime:
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError("invalid ISO-8601 timestamp") from exc
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def actor_ref(raw: str) -> str:
    normalized = raw.strip()
    if len(normalized) < 8:
        raise ValueError("actor credential must be at least 8 characters")
    digest = hashlib.sha256(("CARBON°::" + normalized).encode("utf-8")).hexdigest().upper()
    return f"C°{digest[:10]}"


def public_id(prefix: str) -> str:
    return f"{prefix}-{uuid4().hex[:16].upper()}"


class CreateListingRequest(BaseModel):
    title: str = Field(min_length=2, max_length=120)
    description: str = Field(default="", max_length=1500)
    price_minor: int = Field(gt=0, le=100_000_000_000)
    currency: str = Field(default="ZAR", min_length=3, max_length=3)
    seller_intent: str = Field(default="OPEN", pattern="^(PATIENT|OPEN|MOTIVATED|URGENT)$")
    negotiability: str = Field(default="OPEN", pattern="^(FIXED|OPEN|NEGOTIABLE)$")
    min_bond_minor: int = Field(ge=0, le=100_000_000_000)
    max_considered_bond_minor: int = Field(gt=0, le=100_000_000_000)
    min_at_risk_bps: int = Field(default=3000, ge=0, le=10_000)
    max_at_risk_bps: int = Field(default=6000, ge=0, le=10_000)
    commitment_ttl_minutes: int = Field(default=1440, ge=15, le=10_080)

    @model_validator(mode="after")
    def validate_bounds(self):
        if self.max_considered_bond_minor < self.min_bond_minor:
            raise ValueError("max_considered_bond_minor must be >= min_bond_minor")
        if self.max_at_risk_bps < self.min_at_risk_bps:
            raise ValueError("max_at_risk_bps must be >= min_at_risk_bps")
        if self.max_considered_bond_minor > self.price_minor:
            raise ValueError("maximum bond cannot exceed the item price")
        return self


class CreateInterestRequest(BaseModel):
    bond_minor: int = Field(gt=0, le=100_000_000_000)
    at_risk_bps: int = Field(ge=0, le=10_000)
    proposed_start_at: str
    proposed_duration_minutes: int = Field(default=60, ge=15, le=1440)


class SelectInterestRequest(BaseModel):
    cancellation_buffer_minutes: int = Field(default=120, ge=0, le=10_080)


class CancelRequest(BaseModel):
    reason: str = Field(default="", max_length=500)


class DisputeRequest(BaseModel):
    reason: str = Field(min_length=3, max_length=1200)


class MessageRequest(BaseModel):
    body: str = Field(min_length=1, max_length=1200)


class ExtensionRequest(BaseModel):
    proposed_start_at: str
    proposed_duration_minutes: int = Field(default=60, ge=15, le=1440)
    reason: str = Field(default="", max_length=500)


class ExtensionResponse(BaseModel):
    action: str = Field(pattern="^(ACCEPT|REJECT)$")


class MarketplaceStore:
    def __init__(self, db_path: Path):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_schema()

    def _conn(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path, timeout=15)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys=ON")
        conn.execute("PRAGMA journal_mode=WAL")
        return conn

    def _init_schema(self) -> None:
        with self._conn() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS listings (
                    id TEXT PRIMARY KEY,
                    seller_ref TEXT NOT NULL,
                    title TEXT NOT NULL,
                    description TEXT NOT NULL DEFAULT '',
                    price_minor INTEGER NOT NULL,
                    currency TEXT NOT NULL,
                    seller_intent TEXT NOT NULL,
                    negotiability TEXT NOT NULL,
                    min_bond_minor INTEGER NOT NULL,
                    max_considered_bond_minor INTEGER NOT NULL,
                    min_at_risk_bps INTEGER NOT NULL,
                    max_at_risk_bps INTEGER NOT NULL,
                    commitment_ttl_minutes INTEGER NOT NULL,
                    status TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS interests (
                    id TEXT PRIMARY KEY,
                    listing_id TEXT NOT NULL REFERENCES listings(id),
                    buyer_ref TEXT NOT NULL,
                    bond_minor INTEGER NOT NULL,
                    considered_bond_minor INTEGER NOT NULL,
                    at_risk_bps INTEGER NOT NULL,
                    proposed_start_at TEXT NOT NULL,
                    proposed_duration_minutes INTEGER NOT NULL,
                    state TEXT NOT NULL,
                    provider_ref TEXT NOT NULL,
                    provider_state TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS commitments (
                    id TEXT PRIMARY KEY,
                    listing_id TEXT NOT NULL REFERENCES listings(id),
                    interest_id TEXT NOT NULL UNIQUE REFERENCES interests(id),
                    buyer_ref TEXT NOT NULL,
                    seller_ref TEXT NOT NULL,
                    start_at TEXT NOT NULL,
                    end_at TEXT NOT NULL,
                    cancellation_deadline_at TEXT NOT NULL,
                    bond_minor INTEGER NOT NULL,
                    at_risk_minor INTEGER NOT NULL,
                    seller_confirmed INTEGER NOT NULL DEFAULT 0,
                    buyer_confirmed INTEGER NOT NULL DEFAULT 0,
                    buyer_performed INTEGER NOT NULL DEFAULT 0,
                    seller_performed INTEGER NOT NULL DEFAULT 0,
                    state TEXT NOT NULL,
                    resolution TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS deals (
                    id TEXT PRIMARY KEY,
                    commitment_id TEXT NOT NULL UNIQUE REFERENCES commitments(id),
                    listing_id TEXT NOT NULL REFERENCES listings(id),
                    buyer_ref TEXT NOT NULL,
                    seller_ref TEXT NOT NULL,
                    price_minor INTEGER NOT NULL,
                    currency TEXT NOT NULL,
                    buyer_accept INTEGER NOT NULL DEFAULT 0,
                    seller_accept INTEGER NOT NULL DEFAULT 0,
                    state TEXT NOT NULL,
                    settlement_state TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    entity_kind TEXT NOT NULL,
                    entity_id TEXT NOT NULL,
                    actor_ref TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    payload_json TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS messages (
                    id TEXT PRIMARY KEY,
                    interest_id TEXT NOT NULL REFERENCES interests(id),
                    sender_ref TEXT NOT NULL,
                    body TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS extension_requests (
                    id TEXT PRIMARY KEY,
                    commitment_id TEXT NOT NULL REFERENCES commitments(id),
                    requester_ref TEXT NOT NULL,
                    proposed_start_at TEXT NOT NULL,
                    proposed_end_at TEXT NOT NULL,
                    reason TEXT NOT NULL DEFAULT '',
                    status TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );

                CREATE INDEX IF NOT EXISTS idx_interests_listing ON interests(listing_id, state);
                CREATE INDEX IF NOT EXISTS idx_commitments_listing ON commitments(listing_id, state);
                CREATE INDEX IF NOT EXISTS idx_events_entity ON events(entity_kind, entity_id, id);
                CREATE INDEX IF NOT EXISTS idx_messages_interest ON messages(interest_id, created_at);
                CREATE INDEX IF NOT EXISTS idx_extensions_commitment ON extension_requests(commitment_id, status);
                """
            )

    def _event(
        self,
        conn: sqlite3.Connection,
        entity_kind: str,
        entity_id: str,
        actor: str,
        event_type: str,
        payload: dict[str, Any] | None = None,
    ) -> None:
        conn.execute(
            "INSERT INTO events(entity_kind, entity_id, actor_ref, event_type, payload_json, created_at) VALUES(?,?,?,?,?,?)",
            (entity_kind, entity_id, actor, event_type, json.dumps(payload or {}, sort_keys=True), iso()),
        )

    def create_listing(self, seller_ref: str, payload: CreateListingRequest) -> dict[str, Any]:
        listing_id = public_id("LST")
        now = iso()
        with self._conn() as conn:
            conn.execute(
                """INSERT INTO listings(
                    id,seller_ref,title,description,price_minor,currency,seller_intent,negotiability,
                    min_bond_minor,max_considered_bond_minor,min_at_risk_bps,max_at_risk_bps,
                    commitment_ttl_minutes,status,created_at,updated_at
                ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (
                    listing_id, seller_ref, payload.title.strip(), payload.description.strip(),
                    payload.price_minor, payload.currency.upper(), payload.seller_intent, payload.negotiability,
                    payload.min_bond_minor, payload.max_considered_bond_minor, payload.min_at_risk_bps,
                    payload.max_at_risk_bps, payload.commitment_ttl_minutes, "OPEN", now, now,
                ),
            )
            self._event(conn, "listing", listing_id, seller_ref, "LISTING_CREATED", {
                "seller_intent": payload.seller_intent,
                "min_bond_minor": payload.min_bond_minor,
                "max_considered_bond_minor": payload.max_considered_bond_minor,
            })
            row = conn.execute("SELECT * FROM listings WHERE id=?", (listing_id,)).fetchone()
        return self._public_listing(dict(row))

    def list_listings(self) -> list[dict[str, Any]]:
        with self._conn() as conn:
            rows = conn.execute("SELECT * FROM listings WHERE status='OPEN' ORDER BY created_at DESC").fetchall()
            return [self._public_listing(dict(row), conn) for row in rows]

    def get_listing(self, listing_id: str) -> dict[str, Any] | None:
        with self._conn() as conn:
            row = conn.execute("SELECT * FROM listings WHERE id=?", (listing_id,)).fetchone()
            return self._public_listing(dict(row), conn) if row else None

    def _role_evidence(self, conn: sqlite3.Connection, participant_ref: str, role: str) -> dict[str, Any]:
        field = "buyer_ref" if role == "buyer" else "seller_ref"
        commitments = conn.execute(
            f"""SELECT state FROM commitments
                WHERE {field}=?""",
            (participant_ref,),
        ).fetchall()
        states = [row["state"] for row in commitments]
        bonded_deals = conn.execute(
            f"""SELECT COUNT(*) AS n FROM deals
                WHERE {field}=? AND state='BONDED_DEAL'""",
            (participant_ref,),
        ).fetchone()["n"]
        if role == "buyer":
            adverse = {"BUYER_BREACH_REVIEW","DISPUTED","PERFORMANCE_REVIEW"}
        else:
            adverse = {"SELLER_BREACH_REVIEW","DISPUTED","PERFORMANCE_REVIEW"}
        return {
            "evidence_state": "UNKNOWN" if not states else "OBSERVED",
            "commitments_observed": len(states),
            "honoured": sum(1 for state in states if state in {"HONOURED","CLOSED_NO_DEAL"}),
            "valid_exits": sum(1 for state in states if state in {"VALID_EXIT","MUTUAL_RELEASE"}),
            "review_states": sum(1 for state in states if state in adverse),
            "bonded_deals": int(bonded_deals or 0),
            "score": None,
        }

    def _public_listing(self, record: dict[str, Any], conn: sqlite3.Connection | None = None) -> dict[str, Any]:
        close = False
        if conn is None:
            conn = self._conn()
            close = True
        try:
            stats = conn.execute(
                """SELECT
                    COUNT(*) AS interested,
                    SUM(CASE WHEN state IN ('BONDED_INTEREST','SELECTED','ACTIVE_COMMITMENT') THEN 1 ELSE 0 END) AS bonded,
                    SUM(CASE WHEN state IN ('SELECTED','ACTIVE_COMMITMENT') THEN 1 ELSE 0 END) AS qualified
                   FROM interests WHERE listing_id=?""",
                (record["id"],),
            ).fetchone()
            active = conn.execute(
                "SELECT COUNT(*) AS n FROM commitments WHERE listing_id=? AND state='ACTIVE_COMMITMENT'",
                (record["id"],),
            ).fetchone()["n"]
            return {
                **record,
                "market": {
                    "interested": int(stats["interested"] or 0),
                    "bonded": int(stats["bonded"] or 0),
                    "qualified": int(stats["qualified"] or 0),
                    "active_commitments": int(active or 0),
                },
                "seller_evidence": self._role_evidence(conn, record["seller_ref"], "seller"),
            }
        finally:
            if close:
                conn.close()

    def create_interest(
        self,
        listing_id: str,
        buyer_ref: str,
        payload: CreateInterestRequest,
        provider_ref: str,
    ) -> dict[str, Any]:
        start = parse_time(payload.proposed_start_at)
        if start < utcnow() - timedelta(minutes=5):
            raise ValueError("proposed_start_at cannot be in the past")
        with self._conn() as conn:
            listing = conn.execute("SELECT * FROM listings WHERE id=?", (listing_id,)).fetchone()
            if not listing or listing["status"] != "OPEN":
                raise KeyError("listing not found")
            if listing["seller_ref"] == buyer_ref:
                raise ValueError("seller cannot bond their own listing")
            existing_interest = conn.execute(
                """SELECT id,state FROM interests
                   WHERE listing_id=? AND buyer_ref=?
                   AND state NOT IN ('RELEASED','CLOSED')
                   LIMIT 1""",
                (listing_id, buyer_ref),
            ).fetchone()
            if existing_interest:
                raise ValueError("buyer already has an unresolved interest in this listing")
            if payload.bond_minor < listing["min_bond_minor"]:
                raise ValueError("bond does not meet seller minimum")
            if payload.bond_minor > listing["max_considered_bond_minor"]:
                raise ValueError("bond exceeds seller/platform maximum; excess money cannot buy priority")
            if not (listing["min_at_risk_bps"] <= payload.at_risk_bps <= listing["max_at_risk_bps"]):
                raise ValueError("at-risk percentage is outside seller-permitted range")

            interest_id = public_id("INT")
            considered = payload.bond_minor
            now = iso()
            conn.execute(
                """INSERT INTO interests(
                    id,listing_id,buyer_ref,bond_minor,considered_bond_minor,at_risk_bps,
                    proposed_start_at,proposed_duration_minutes,state,provider_ref,provider_state,created_at,updated_at
                ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (
                    interest_id, listing_id, buyer_ref, payload.bond_minor, considered, payload.at_risk_bps,
                    iso(start), payload.proposed_duration_minutes, "BONDED_INTEREST", provider_ref,
                    "SANDBOX_RESERVED", now, now,
                ),
            )
            self._event(conn, "interest", interest_id, buyer_ref, "BONDED_INTEREST_CREATED", {
                "listing_id": listing_id,
                "bond_minor": payload.bond_minor,
                "considered_bond_minor": considered,
                "at_risk_bps": payload.at_risk_bps,
                "provider_state": "SANDBOX_RESERVED",
                "money_moved": False,
            })
            row = conn.execute("SELECT * FROM interests WHERE id=?", (interest_id,)).fetchone()
        return dict(row)

    def list_interest_for_listing(self, listing_id: str, seller_ref: str) -> list[dict[str, Any]]:
        with self._conn() as conn:
            listing = conn.execute("SELECT seller_ref FROM listings WHERE id=?", (listing_id,)).fetchone()
            if not listing:
                raise KeyError("listing not found")
            if listing["seller_ref"] != seller_ref:
                raise PermissionError("seller credential required")
            rows = conn.execute(
                """SELECT id,listing_id,buyer_ref,bond_minor,considered_bond_minor,at_risk_bps,
                          proposed_start_at,proposed_duration_minutes,state,provider_state,created_at,updated_at
                   FROM interests WHERE listing_id=? ORDER BY considered_bond_minor DESC, created_at ASC""",
                (listing_id,),
            ).fetchall()
            records = []
            for row in rows:
                record = dict(row)
                record["buyer_evidence"] = self._role_evidence(conn, record["buyer_ref"], "buyer")
                records.append(record)
            return records

    def select_interest(
        self,
        interest_id: str,
        seller_ref: str,
        cancellation_buffer_minutes: int,
    ) -> dict[str, Any]:
        with self._conn() as conn:
            interest = conn.execute("SELECT * FROM interests WHERE id=?", (interest_id,)).fetchone()
            if not interest:
                raise KeyError("interest not found")
            listing = conn.execute("SELECT * FROM listings WHERE id=?", (interest["listing_id"],)).fetchone()
            if listing["seller_ref"] != seller_ref:
                raise PermissionError("seller credential required")
            existing = conn.execute("SELECT * FROM commitments WHERE interest_id=?", (interest_id,)).fetchone()
            if existing:
                return dict(existing)
            if listing["status"] != "OPEN":
                raise ValueError("listing is no longer open")
            blocking = conn.execute(
                """SELECT id,state FROM commitments
                   WHERE listing_id=? AND state IN ('SELECTED','ACTIVE_COMMITMENT','HONOURED')
                   LIMIT 1""",
                (interest["listing_id"],),
            ).fetchone()
            if blocking:
                raise ValueError("listing already has a selected/active buyer; other bonded interests remain queued")
            if interest["state"] != "BONDED_INTEREST":
                raise ValueError("interest is not selectable")

            start = parse_time(interest["proposed_start_at"])
            end = start + timedelta(minutes=interest["proposed_duration_minutes"])
            cancellation_deadline = start - timedelta(minutes=cancellation_buffer_minutes)
            at_risk_minor = (interest["bond_minor"] * interest["at_risk_bps"]) // 10_000
            commitment_id = public_id("COM")
            now = iso()
            conn.execute(
                """INSERT INTO commitments(
                    id,listing_id,interest_id,buyer_ref,seller_ref,start_at,end_at,cancellation_deadline_at,
                    bond_minor,at_risk_minor,seller_confirmed,buyer_confirmed,buyer_performed,seller_performed,
                    state,resolution,created_at,updated_at
                ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (
                    commitment_id, interest["listing_id"], interest_id, interest["buyer_ref"], seller_ref,
                    iso(start), iso(end), iso(cancellation_deadline), interest["bond_minor"], at_risk_minor,
                    1, 0, 0, 0, "SELECTED", None, now, now,
                ),
            )
            conn.execute("UPDATE interests SET state='SELECTED',updated_at=? WHERE id=?", (now, interest_id))
            self._event(conn, "commitment", commitment_id, seller_ref, "SELLER_SELECTED_INTEREST", {
                "interest_id": interest_id,
                "buyer_consequence_active": False,
                "seller_commitment_declared": True,
            })
            row = conn.execute("SELECT * FROM commitments WHERE id=?", (commitment_id,)).fetchone()
        return dict(row)

    def get_commitment(self, commitment_id: str) -> dict[str, Any] | None:
        with self._conn() as conn:
            row = conn.execute("SELECT * FROM commitments WHERE id=?", (commitment_id,)).fetchone()
            return dict(row) if row else None

    def confirm_buyer(self, commitment_id: str, buyer_ref: str) -> dict[str, Any]:
        with self._conn() as conn:
            row = conn.execute("SELECT * FROM commitments WHERE id=?", (commitment_id,)).fetchone()
            if not row:
                raise KeyError("commitment not found")
            if row["buyer_ref"] != buyer_ref:
                raise PermissionError("buyer credential required")
            if row["state"] not in {"SELECTED", "ACTIVE_COMMITMENT"}:
                raise ValueError("commitment cannot be activated")
            if row["state"] == "ACTIVE_COMMITMENT":
                return dict(row)
            now = iso()
            conn.execute(
                "UPDATE commitments SET buyer_confirmed=1,state='ACTIVE_COMMITMENT',updated_at=? WHERE id=?",
                (now, commitment_id),
            )
            conn.execute(
                "UPDATE interests SET state='ACTIVE_COMMITMENT',updated_at=? WHERE id=?",
                (now, row["interest_id"]),
            )
            self._event(conn, "commitment", commitment_id, buyer_ref, "BILATERAL_COMMITMENT_ACTIVATED", {
                "at_risk_minor": row["at_risk_minor"],
                "start_at": row["start_at"],
                "end_at": row["end_at"],
                "financial_resolution": "NOT_AUTOMATIC",
            })
            row = conn.execute("SELECT * FROM commitments WHERE id=?", (commitment_id,)).fetchone()
        return dict(row)

    def cancel_commitment(self, commitment_id: str, actor: str, reason: str) -> dict[str, Any]:
        with self._conn() as conn:
            row = conn.execute("SELECT * FROM commitments WHERE id=?", (commitment_id,)).fetchone()
            if not row:
                raise KeyError("commitment not found")
            if actor not in {row["buyer_ref"], row["seller_ref"]}:
                raise PermissionError("participant credential required")
            if row["state"] in {"HONOURED", "DISPUTED", "BUYER_BREACH_REVIEW", "SELLER_BREACH_REVIEW", "VALID_EXIT", "MUTUAL_RELEASE"}:
                raise ValueError("commitment already resolved")

            if row["state"] == "SELECTED":
                state = "MUTUAL_RELEASE"
                resolution = "FULL_RELEASE_PRE_ACTIVATION"
            else:
                before_deadline = utcnow() <= parse_time(row["cancellation_deadline_at"])
                if before_deadline:
                    state = "VALID_EXIT"
                    resolution = "RELEASE_SUBJECT_TO_PROVIDER_RULES"
                elif actor == row["buyer_ref"]:
                    state = "BUYER_BREACH_REVIEW"
                    resolution = "HOLD_FOR_REVIEW_NO_AUTOMATIC_FORFEITURE"
                else:
                    state = "SELLER_BREACH_REVIEW"
                    resolution = "HOLD_FOR_REVIEW_NO_AUTOMATIC_PENALTY"

            now = iso()
            conn.execute(
                "UPDATE commitments SET state=?,resolution=?,updated_at=? WHERE id=?",
                (state, resolution, now, commitment_id),
            )
            interest_state = "RELEASE_PENDING" if state in {"MUTUAL_RELEASE", "VALID_EXIT"} else "REVIEW_PENDING"
            conn.execute("UPDATE interests SET state=?,updated_at=? WHERE id=?", (interest_state, now, row["interest_id"]))
            self._event(conn, "commitment", commitment_id, actor, "COMMITMENT_EXIT", {
                "state": state,
                "resolution": resolution,
                "reason": reason.strip(),
            })
            updated = conn.execute("SELECT * FROM commitments WHERE id=?", (commitment_id,)).fetchone()
        return dict(updated)

    def mark_performance(self, commitment_id: str, actor: str) -> dict[str, Any]:
        with self._conn() as conn:
            row = conn.execute("SELECT * FROM commitments WHERE id=?", (commitment_id,)).fetchone()
            if not row:
                raise KeyError("commitment not found")
            if row["state"] not in {"ACTIVE_COMMITMENT", "HONOURED"}:
                raise ValueError("only active commitments can be performed")
            if actor == row["buyer_ref"]:
                field = "buyer_performed"
            elif actor == row["seller_ref"]:
                field = "seller_performed"
            else:
                raise PermissionError("participant credential required")
            now = iso()
            conn.execute(f"UPDATE commitments SET {field}=1,updated_at=? WHERE id=?", (now, commitment_id))
            fresh = conn.execute("SELECT * FROM commitments WHERE id=?", (commitment_id,)).fetchone()
            state = fresh["state"]
            resolution = fresh["resolution"]
            if fresh["buyer_performed"] and fresh["seller_performed"]:
                state = "HONOURED"
                resolution = "BILATERAL_PERFORMANCE_CONFIRMED"
                conn.execute(
                    "UPDATE commitments SET state=?,resolution=?,updated_at=? WHERE id=?",
                    (state, resolution, now, commitment_id),
                )
                conn.execute("UPDATE interests SET state='HONOURED',updated_at=? WHERE id=?", (now, fresh["interest_id"]))
            self._event(conn, "commitment", commitment_id, actor, "PERFORMANCE_CONFIRMED", {"state": state})
            updated = conn.execute("SELECT * FROM commitments WHERE id=?", (commitment_id,)).fetchone()
        return dict(updated)

    def dispute(self, commitment_id: str, actor: str, reason: str) -> dict[str, Any]:
        with self._conn() as conn:
            row = conn.execute("SELECT * FROM commitments WHERE id=?", (commitment_id,)).fetchone()
            if not row:
                raise KeyError("commitment not found")
            if actor not in {row["buyer_ref"], row["seller_ref"]}:
                raise PermissionError("participant credential required")
            if row["state"] in {"MUTUAL_RELEASE", "VALID_EXIT"}:
                raise ValueError("released commitments cannot be disputed")
            now = iso()
            conn.execute(
                "UPDATE commitments SET state='DISPUTED',resolution='PROVIDER_HOLD_PENDING_REVIEW',updated_at=? WHERE id=?",
                (now, commitment_id),
            )
            conn.execute(
                "UPDATE interests SET state='DISPUTED',provider_state='SANDBOX_HOLD',updated_at=? WHERE id=?",
                (now, row["interest_id"]),
            )
            self._event(conn, "commitment", commitment_id, actor, "DISPUTE_OPENED", {"reason": reason.strip()})
            updated = conn.execute("SELECT * FROM commitments WHERE id=?", (commitment_id,)).fetchone()
        return dict(updated)

    def open_deal(self, commitment_id: str, actor: str) -> dict[str, Any]:
        with self._conn() as conn:
            com = conn.execute("SELECT * FROM commitments WHERE id=?", (commitment_id,)).fetchone()
            if not com:
                raise KeyError("commitment not found")
            if actor not in {com["buyer_ref"], com["seller_ref"]}:
                raise PermissionError("participant credential required")
            if com["state"] != "HONOURED":
                raise ValueError("deal can open only after bilateral performance")
            existing = conn.execute("SELECT * FROM deals WHERE commitment_id=?", (commitment_id,)).fetchone()
            if existing:
                return dict(existing)
            listing = conn.execute("SELECT * FROM listings WHERE id=?", (com["listing_id"],)).fetchone()
            deal_id = public_id("DEAL")
            now = iso()
            conn.execute(
                """INSERT INTO deals(id,commitment_id,listing_id,buyer_ref,seller_ref,price_minor,currency,
                   buyer_accept,seller_accept,state,settlement_state,created_at,updated_at)
                   VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (
                    deal_id, commitment_id, com["listing_id"], com["buyer_ref"], com["seller_ref"],
                    listing["price_minor"], listing["currency"], 0, 0, "INSPECTION", "NOT_READY", now, now,
                ),
            )
            self._event(conn, "deal", deal_id, actor, "INSPECTION_OPENED", {"commitment_id": commitment_id})
            row = conn.execute("SELECT * FROM deals WHERE id=?", (deal_id,)).fetchone()
        return dict(row)

    def decline_deal(self, deal_id: str, actor: str, reason: str) -> dict[str, Any]:
        with self._conn() as conn:
            deal = conn.execute("SELECT * FROM deals WHERE id=?", (deal_id,)).fetchone()
            if not deal:
                raise KeyError("deal not found")
            if actor not in {deal["buyer_ref"], deal["seller_ref"]}:
                raise PermissionError("participant credential required")
            if deal["state"] != "INSPECTION":
                raise ValueError("only an inspection-stage deal can be declined")
            commitment = conn.execute(
                "SELECT * FROM commitments WHERE id=?",
                (deal["commitment_id"],),
            ).fetchone()
            now = iso()
            conn.execute(
                "UPDATE deals SET state='NO_DEAL',settlement_state='NO_PURCHASE_SETTLEMENT',updated_at=? WHERE id=?",
                (now, deal_id),
            )
            conn.execute(
                "UPDATE commitments SET state='CLOSED_NO_DEAL',resolution='BILATERAL_PERFORMANCE_NO_PURCHASE',updated_at=? WHERE id=?",
                (now, deal["commitment_id"]),
            )
            conn.execute(
                "UPDATE interests SET state='HONOURED_RELEASE_PENDING',provider_state='SANDBOX_RELEASE_PENDING',updated_at=? WHERE id=?",
                (now, commitment["interest_id"]),
            )
            self._event(conn, "deal", deal_id, actor, "DEAL_DECLINED_AFTER_INSPECTION", {
                "reason": reason.strip(),
                "bond_resolution": "RELEASE_PENDING",
                "money_moved": False,
            })
            updated = conn.execute("SELECT * FROM deals WHERE id=?", (deal_id,)).fetchone()
        return dict(updated)

    def accept_deal(self, deal_id: str, actor: str) -> dict[str, Any]:
        with self._conn() as conn:
            deal = conn.execute("SELECT * FROM deals WHERE id=?", (deal_id,)).fetchone()
            if not deal:
                raise KeyError("deal not found")
            if deal["state"] == "BONDED_DEAL":
                return dict(deal)
            if actor == deal["buyer_ref"]:
                field = "buyer_accept"
            elif actor == deal["seller_ref"]:
                field = "seller_accept"
            else:
                raise PermissionError("participant credential required")
            now = iso()
            conn.execute(f"UPDATE deals SET {field}=1,updated_at=? WHERE id=?", (now, deal_id))
            fresh = conn.execute("SELECT * FROM deals WHERE id=?", (deal_id,)).fetchone()
            if fresh["buyer_accept"] and fresh["seller_accept"]:
                conn.execute(
                    "UPDATE deals SET state='BONDED_DEAL',settlement_state='SANDBOX_READY_FOR_PROVIDER',updated_at=? WHERE id=?",
                    (now, deal_id),
                )
                conn.execute("UPDATE listings SET status='COMMITTED',updated_at=? WHERE id=?", (now, fresh["listing_id"]))
                commitment = conn.execute(
                    "SELECT interest_id FROM commitments WHERE id=?",
                    (fresh["commitment_id"],),
                ).fetchone()
                queued = conn.execute(
                    """SELECT id FROM interests
                       WHERE listing_id=? AND id<>? AND state='BONDED_INTEREST'""",
                    (fresh["listing_id"], commitment["interest_id"]),
                ).fetchall()
                for queued_interest in queued:
                    conn.execute(
                        "UPDATE interests SET state='RELEASE_PENDING',provider_state='SANDBOX_RELEASE_PENDING',updated_at=? WHERE id=?",
                        (now, queued_interest["id"]),
                    )
                    self._event(conn, "interest", queued_interest["id"], "SYSTEM", "QUEUE_RELEASED_AFTER_SALE", {
                        "listing_id": fresh["listing_id"],
                        "money_moved": False,
                    })
            self._event(conn, "deal", deal_id, actor, "DEAL_ACCEPTANCE_RECORDED", {
                "buyer_accept": bool(fresh["buyer_accept"] or actor == fresh["buyer_ref"]),
                "seller_accept": bool(fresh["seller_accept"] or actor == fresh["seller_ref"]),
                "money_moved": False,
            })
            updated = conn.execute("SELECT * FROM deals WHERE id=?", (deal_id,)).fetchone()
        return dict(updated)

    def get_events(self, entity_kind: str, entity_id: str) -> list[dict[str, Any]]:
        with self._conn() as conn:
            rows = conn.execute(
                "SELECT id,entity_kind,entity_id,actor_ref,event_type,payload_json,created_at FROM events WHERE entity_kind=? AND entity_id=? ORDER BY id",
                (entity_kind, entity_id),
            ).fetchall()
            result = []
            for row in rows:
                record = dict(row)
                record["payload"] = json.loads(record.pop("payload_json"))
                result.append(record)
            return result

    def request_extension(
        self,
        commitment_id: str,
        actor: str,
        proposed_start_at: str,
        proposed_duration_minutes: int,
        reason: str,
    ) -> dict[str, Any]:
        start = parse_time(proposed_start_at)
        if start <= utcnow():
            raise ValueError("extension start must be in the future")
        end = start + timedelta(minutes=proposed_duration_minutes)
        with self._conn() as conn:
            commitment = conn.execute("SELECT * FROM commitments WHERE id=?", (commitment_id,)).fetchone()
            if not commitment:
                raise KeyError("commitment not found")
            if actor not in {commitment["buyer_ref"], commitment["seller_ref"]}:
                raise PermissionError("participant credential required")
            if commitment["state"] != "ACTIVE_COMMITMENT":
                raise ValueError("extensions require an active bilateral commitment")
            pending = conn.execute(
                "SELECT id FROM extension_requests WHERE commitment_id=? AND status='PENDING' LIMIT 1",
                (commitment_id,),
            ).fetchone()
            if pending:
                raise ValueError("an extension request is already pending")
            request_id = public_id("EXT")
            now = iso()
            conn.execute(
                """INSERT INTO extension_requests(
                    id,commitment_id,requester_ref,proposed_start_at,proposed_end_at,reason,status,created_at,updated_at
                ) VALUES(?,?,?,?,?,?,?,?,?)""",
                (
                    request_id, commitment_id, actor, iso(start), iso(end), reason.strip(),
                    "PENDING", now, now,
                ),
            )
            self._event(conn, "commitment", commitment_id, actor, "EXTENSION_REQUESTED", {
                "extension_id": request_id,
                "proposed_start_at": iso(start),
                "proposed_end_at": iso(end),
                "original_commitment_unchanged": True,
            })
            row = conn.execute("SELECT * FROM extension_requests WHERE id=?", (request_id,)).fetchone()
        return dict(row)

    def respond_extension(self, extension_id: str, actor: str, action: str) -> dict[str, Any]:
        with self._conn() as conn:
            ext = conn.execute("SELECT * FROM extension_requests WHERE id=?", (extension_id,)).fetchone()
            if not ext:
                raise KeyError("extension request not found")
            if ext["status"] != "PENDING":
                return dict(ext)
            commitment = conn.execute("SELECT * FROM commitments WHERE id=?", (ext["commitment_id"],)).fetchone()
            if not commitment:
                raise KeyError("commitment not found")
            if actor not in {commitment["buyer_ref"], commitment["seller_ref"]}:
                raise PermissionError("participant credential required")
            if actor == ext["requester_ref"]:
                raise PermissionError("requester cannot approve their own extension")
            if commitment["state"] != "ACTIVE_COMMITMENT":
                raise ValueError("commitment is no longer eligible for extension")
            now = iso()
            if action == "ACCEPT":
                old_start = parse_time(commitment["start_at"])
                old_deadline = parse_time(commitment["cancellation_deadline_at"])
                buffer = max(timedelta(0), old_start - old_deadline)
                new_start = parse_time(ext["proposed_start_at"])
                new_end = parse_time(ext["proposed_end_at"])
                new_deadline = new_start - buffer
                conn.execute(
                    """UPDATE commitments
                       SET start_at=?,end_at=?,cancellation_deadline_at=?,updated_at=?
                       WHERE id=?""",
                    (iso(new_start), iso(new_end), iso(new_deadline), now, commitment["id"]),
                )
                status = "ACCEPTED"
            else:
                status = "REJECTED"
            conn.execute(
                "UPDATE extension_requests SET status=?,updated_at=? WHERE id=?",
                (status, now, extension_id),
            )
            self._event(conn, "commitment", commitment["id"], actor, "EXTENSION_"+status, {
                "extension_id": extension_id,
                "new_window_applied": status == "ACCEPTED",
            })
            row = conn.execute("SELECT * FROM extension_requests WHERE id=?", (extension_id,)).fetchone()
        return dict(row)

    def _interest_participants(self, conn: sqlite3.Connection, interest_id: str) -> tuple[sqlite3.Row, str]:
        interest = conn.execute("SELECT * FROM interests WHERE id=?", (interest_id,)).fetchone()
        if not interest:
            raise KeyError("interest not found")
        listing = conn.execute("SELECT seller_ref FROM listings WHERE id=?", (interest["listing_id"],)).fetchone()
        return interest, listing["seller_ref"]

    def list_messages(self, interest_id: str, actor: str) -> list[dict[str, Any]]:
        with self._conn() as conn:
            interest, seller_ref = self._interest_participants(conn, interest_id)
            if actor not in {interest["buyer_ref"], seller_ref}:
                raise PermissionError("interest participant credential required")
            rows = conn.execute(
                "SELECT id,interest_id,sender_ref,body,created_at FROM messages WHERE interest_id=? ORDER BY created_at,id",
                (interest_id,),
            ).fetchall()
            return [dict(row) for row in rows]

    def post_message(self, interest_id: str, actor: str, body: str) -> dict[str, Any]:
        with self._conn() as conn:
            interest, seller_ref = self._interest_participants(conn, interest_id)
            if actor not in {interest["buyer_ref"], seller_ref}:
                raise PermissionError("interest participant credential required")
            if interest["state"] not in {
                "BONDED_INTEREST","SELECTED","ACTIVE_COMMITMENT","HONOURED",
                "REVIEW_PENDING","DISPUTED","HONOURED_RELEASE_PENDING"
            }:
                raise ValueError("this bonded conversation is closed")
            message_id = public_id("MSG")
            now = iso()
            clean = body.strip()
            conn.execute(
                "INSERT INTO messages(id,interest_id,sender_ref,body,created_at) VALUES(?,?,?,?,?)",
                (message_id, interest_id, actor, clean, now),
            )
            self._event(conn, "interest", interest_id, actor, "BONDED_MESSAGE_SENT", {
                "message_id": message_id,
                "characters": len(clean),
                "content_stored_privately": True,
            })
            row = conn.execute(
                "SELECT id,interest_id,sender_ref,body,created_at FROM messages WHERE id=?",
                (message_id,),
            ).fetchone()
        return dict(row)

    def seed_demo(self) -> list[dict[str, Any]]:
        with self._conn() as conn:
            count = conn.execute("SELECT COUNT(*) AS n FROM listings").fetchone()["n"]
        if count:
            return self.list_listings()
        seller = actor_ref("carbon-demo-seller-2026")
        samples = [
            CreateListingRequest(
                title='MacBook Pro 14"',
                description="Local handover. Inspect before either side confirms the deal.",
                price_minor=28_500_00,
                currency="ZAR",
                seller_intent="PATIENT",
                negotiability="OPEN",
                min_bond_minor=500_00,
                max_considered_bond_minor=1500_00,
                min_at_risk_bps=3000,
                max_at_risk_bps=6000,
                commitment_ttl_minutes=1440,
            ),
            CreateListingRequest(
                title="Sony A7 IV body",
                description="High demand. Seller is available this evening for inspection.",
                price_minor=31_000_00,
                currency="ZAR",
                seller_intent="MOTIVATED",
                negotiability="FIXED",
                min_bond_minor=750_00,
                max_considered_bond_minor=2000_00,
                min_at_risk_bps=3000,
                max_at_risk_bps=7000,
                commitment_ttl_minutes=720,
            ),
            CreateListingRequest(
                title="Workshop tool bundle",
                description="Seller wants it gone today. Collection only.",
                price_minor=7_500_00,
                currency="ZAR",
                seller_intent="URGENT",
                negotiability="NEGOTIABLE",
                min_bond_minor=200_00,
                max_considered_bond_minor=600_00,
                min_at_risk_bps=2500,
                max_at_risk_bps=5000,
                commitment_ttl_minutes=360,
            ),
        ]
        return [self.create_listing(seller, item) for item in samples]


class SandboxMoneyAdapter:
    """Non-custodial development adapter. It records intent only and never moves money."""

    name = "SANDBOX_NO_MONEY_MOVED"

    def reserve(self, listing_id: str, buyer_ref: str, amount_minor: int) -> str:
        material = f"{listing_id}:{buyer_ref}:{amount_minor}:{uuid4().hex}"
        return "SBX-" + hashlib.sha256(material.encode()).hexdigest()[:24].upper()


def mount_marketplace(
    app: FastAPI,
    root: Path,
    *,
    db_path: Path | None = None,
    demo_mode: bool | None = None,
) -> None:
    db = Path(db_path or os.getenv("CARBON_MARKETPLACE_DB_PATH") or root / "data/carbon_marketplace.db")
    store = MarketplaceStore(db)
    money = SandboxMoneyAdapter()
    demo_enabled = demo_mode if demo_mode is not None else os.getenv("CARBON_MARKETPLACE_DEMO_MODE", "").strip() in {"1", "true", "TRUE", "yes", "YES"}
    app.state.carbon_marketplace_store = store

    router = APIRouter()

    def actor(x_carbon_actor: str | None = Header(default=None)) -> str:
        if not x_carbon_actor:
            raise HTTPException(status_code=401, detail="X-CARBON-Actor is required")
        try:
            return actor_ref(x_carbon_actor)
        except ValueError as exc:
            raise HTTPException(status_code=401, detail=str(exc)) from exc

    def require_demo() -> None:
        if not demo_enabled:
            raise HTTPException(status_code=503, detail="marketplace writes are fail-closed until production identity/payment providers are configured")

    def map_error(exc: Exception) -> HTTPException:
        if isinstance(exc, KeyError):
            return HTTPException(status_code=404, detail=str(exc).strip("'"))
        if isinstance(exc, PermissionError):
            return HTTPException(status_code=403, detail=str(exc))
        if isinstance(exc, ValueError):
            return HTTPException(status_code=422, detail=str(exc))
        return HTTPException(status_code=500, detail="marketplace operation failed")

    @router.get("/api/carbon/bootstrap")
    def bootstrap() -> dict[str, Any]:
        return {
            "product": "CARBON°",
            "thesis": "The marketplace where intent has weight.",
            "money_adapter": money.name,
            "money_moved": False,
            "demo_mode": demo_enabled,
            "laws": {
                "freedom_until_commitment": True,
                "unknown_is_not_bad": True,
                "money_does_not_buy_priority": True,
                "bilateral_commitment": True,
                "proper_exit_is_not_breach": True,
            },
            "listings": store.list_listings(),
        }

    @router.post("/api/carbon/demo/seed")
    def demo_seed() -> dict[str, Any]:
        require_demo()
        return {"listings": store.seed_demo(), "money_moved": False}

    @router.get("/api/carbon/listings")
    def listings() -> dict[str, Any]:
        records = store.list_listings()
        return {"records": records, "count": len(records)}

    @router.get("/api/carbon/listings/{listing_id}")
    def listing(listing_id: str) -> dict[str, Any]:
        record = store.get_listing(listing_id)
        if not record:
            raise HTTPException(status_code=404, detail="listing not found")
        return record

    @router.post("/api/carbon/listings")
    def create_listing(payload: CreateListingRequest, x_carbon_actor: str | None = Header(default=None)) -> dict[str, Any]:
        require_demo()
        seller = actor(x_carbon_actor)
        return {"record": store.create_listing(seller, payload)}

    @router.post("/api/carbon/listings/{listing_id}/interests")
    def create_interest(listing_id: str, payload: CreateInterestRequest, x_carbon_actor: str | None = Header(default=None)) -> dict[str, Any]:
        require_demo()
        buyer = actor(x_carbon_actor)
        try:
            provider_ref = money.reserve(listing_id, buyer, payload.bond_minor)
            record = store.create_interest(listing_id, buyer, payload, provider_ref)
            return {"record": record, "money_moved": False, "provider": money.name}
        except Exception as exc:
            raise map_error(exc) from exc

    @router.get("/api/carbon/listings/{listing_id}/interests")
    def seller_interests(listing_id: str, x_carbon_actor: str | None = Header(default=None)) -> dict[str, Any]:
        require_demo()
        seller = actor(x_carbon_actor)
        try:
            records = store.list_interest_for_listing(listing_id, seller)
            return {"records": records, "count": len(records)}
        except Exception as exc:
            raise map_error(exc) from exc

    @router.post("/api/carbon/interests/{interest_id}/select")
    def select_interest(interest_id: str, payload: SelectInterestRequest, x_carbon_actor: str | None = Header(default=None)) -> dict[str, Any]:
        require_demo()
        seller = actor(x_carbon_actor)
        try:
            record = store.select_interest(interest_id, seller, payload.cancellation_buffer_minutes)
            return {"record": record, "at_risk_active": False}
        except Exception as exc:
            raise map_error(exc) from exc

    @router.get("/api/carbon/commitments/{commitment_id}")
    def commitment(commitment_id: str) -> dict[str, Any]:
        record = store.get_commitment(commitment_id)
        if not record:
            raise HTTPException(status_code=404, detail="commitment not found")
        return record

    @router.post("/api/carbon/commitments/{commitment_id}/confirm")
    def confirm_commitment(commitment_id: str, x_carbon_actor: str | None = Header(default=None)) -> dict[str, Any]:
        require_demo()
        buyer = actor(x_carbon_actor)
        try:
            return {"record": store.confirm_buyer(commitment_id, buyer), "at_risk_active": True}
        except Exception as exc:
            raise map_error(exc) from exc

    @router.post("/api/carbon/commitments/{commitment_id}/cancel")
    def cancel(commitment_id: str, payload: CancelRequest, x_carbon_actor: str | None = Header(default=None)) -> dict[str, Any]:
        require_demo()
        participant = actor(x_carbon_actor)
        try:
            return {"record": store.cancel_commitment(commitment_id, participant, payload.reason)}
        except Exception as exc:
            raise map_error(exc) from exc

    @router.post("/api/carbon/commitments/{commitment_id}/perform")
    def perform(commitment_id: str, x_carbon_actor: str | None = Header(default=None)) -> dict[str, Any]:
        require_demo()
        participant = actor(x_carbon_actor)
        try:
            return {"record": store.mark_performance(commitment_id, participant)}
        except Exception as exc:
            raise map_error(exc) from exc

    @router.post("/api/carbon/commitments/{commitment_id}/dispute")
    def dispute(commitment_id: str, payload: DisputeRequest, x_carbon_actor: str | None = Header(default=None)) -> dict[str, Any]:
        require_demo()
        participant = actor(x_carbon_actor)
        try:
            return {"record": store.dispute(commitment_id, participant, payload.reason), "provider_state": "SANDBOX_HOLD"}
        except Exception as exc:
            raise map_error(exc) from exc

    @router.post("/api/carbon/commitments/{commitment_id}/deal")
    def open_deal(commitment_id: str, x_carbon_actor: str | None = Header(default=None)) -> dict[str, Any]:
        require_demo()
        participant = actor(x_carbon_actor)
        try:
            return {"record": store.open_deal(commitment_id, participant)}
        except Exception as exc:
            raise map_error(exc) from exc

    @router.post("/api/carbon/deals/{deal_id}/decline")
    def decline_deal(deal_id: str, payload: CancelRequest, x_carbon_actor: str | None = Header(default=None)) -> dict[str, Any]:
        require_demo()
        participant = actor(x_carbon_actor)
        try:
            return {"record": store.decline_deal(deal_id, participant, payload.reason), "money_moved": False}
        except Exception as exc:
            raise map_error(exc) from exc

    @router.post("/api/carbon/deals/{deal_id}/accept")
    def accept_deal(deal_id: str, x_carbon_actor: str | None = Header(default=None)) -> dict[str, Any]:
        require_demo()
        participant = actor(x_carbon_actor)
        try:
            return {"record": store.accept_deal(deal_id, participant), "money_moved": False}
        except Exception as exc:
            raise map_error(exc) from exc

    @router.post("/api/carbon/commitments/{commitment_id}/extensions")
    def request_extension(commitment_id: str, payload: ExtensionRequest, x_carbon_actor: str | None = Header(default=None)) -> dict[str, Any]:
        require_demo()
        participant = actor(x_carbon_actor)
        try:
            return {"record": store.request_extension(
                commitment_id,
                participant,
                payload.proposed_start_at,
                payload.proposed_duration_minutes,
                payload.reason,
            )}
        except Exception as exc:
            raise map_error(exc) from exc

    @router.post("/api/carbon/extensions/{extension_id}/respond")
    def respond_extension(extension_id: str, payload: ExtensionResponse, x_carbon_actor: str | None = Header(default=None)) -> dict[str, Any]:
        require_demo()
        participant = actor(x_carbon_actor)
        try:
            return {"record": store.respond_extension(extension_id, participant, payload.action)}
        except Exception as exc:
            raise map_error(exc) from exc

    @router.get("/api/carbon/interests/{interest_id}/messages")
    def messages(interest_id: str, x_carbon_actor: str | None = Header(default=None)) -> dict[str, Any]:
        require_demo()
        participant = actor(x_carbon_actor)
        try:
            records = store.list_messages(interest_id, participant)
            return {"records": records, "count": len(records), "bond_gated": True}
        except Exception as exc:
            raise map_error(exc) from exc

    @router.post("/api/carbon/interests/{interest_id}/messages")
    def send_message(interest_id: str, payload: MessageRequest, x_carbon_actor: str | None = Header(default=None)) -> dict[str, Any]:
        require_demo()
        participant = actor(x_carbon_actor)
        try:
            return {"record": store.post_message(interest_id, participant, payload.body), "bond_gated": True}
        except Exception as exc:
            raise map_error(exc) from exc

    @router.get("/api/carbon/events/{entity_kind}/{entity_id}")
    def events(entity_kind: str, entity_id: str) -> dict[str, Any]:
        if entity_kind not in {"listing", "interest", "commitment", "deal"}:
            raise HTTPException(status_code=422, detail="unsupported entity kind")
        records = store.get_events(entity_kind, entity_id)
        return {"records": records, "count": len(records)}

    market_dir = root / "marketplace"
    if market_dir.exists():
        @router.get("/market/assets/{asset}")
        def market_asset(asset: str):
            if asset not in {"styles.css", "app.js"}:
                raise HTTPException(status_code=404, detail="asset not found")
            path = market_dir / asset
            if path.is_symlink() or not path.is_file():
                raise HTTPException(status_code=404, detail="asset not found")
            return FileResponse(path)

        @router.get("/market")
        @router.get("/market/")
        def market_index():
            return FileResponse(market_dir / "index.html")

    app.include_router(router)
