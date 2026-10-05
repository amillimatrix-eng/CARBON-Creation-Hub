from __future__ import annotations

import fcntl
import hashlib
import hmac
import json
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, RedirectResponse
from pydantic import BaseModel, Field

from .state import aggregate_state
from overdrive.payment_truth import payment_state
from .store import EvidenceStore, SCHEMA_VERSION, T10_FIELDS, T10_SCHEMA


class SearchRequest(BaseModel):
    query: str = Field(min_length=1, max_length=500)
    limit: int = Field(default=8, ge=1, le=50)


class ProposalChangeRequest(BaseModel):
    selected_modules: list[str] = Field(default_factory=list, max_length=20)
    message: str = Field(default="", max_length=1200)
    contact: str = Field(default="", max_length=120)
    action: str = Field(default="REQUEST_CHANGE", pattern="^(REQUEST_CHANGE|REQUEST_CALLBACK)$")


class EvidencePayload(BaseModel):
    evidence_id: str
    capability: str
    artifact: str
    authoritative_source: str
    source_pointer: str | None = None
    date_version: str | None = None
    role_contribution: str | None = None
    acceptance_test: str | None = None
    durable_receipts: list[str] = Field(default_factory=list)
    durable_receipt: str | None = None
    artifact_hash: str | None = None
    source_hash: str | None = None
    status_freshness: str
    interview_safe_explanation: str
    T10_JOB: str
    T10_ACTUAL: str
    T10_EVIDENCE: str
    T10_CHANGE: str
    T10_REMAINING_GAP: str
    T10_PASS: str = Field(pattern="^(PASS|HOLD|FAIL|UNKNOWN)$")
    inspect_route: str | None = None
    visibility: str = "PRIVATE"
    tags: list[str] = Field(default_factory=list)


def create_app(repo_root: Path | None = None, db_path: Path | None = None) -> FastAPI:
    root = Path(repo_root or os.getenv("AMX_REPO_ROOT") or Path(__file__).resolve().parents[1]).resolve()
    db = Path(db_path or os.getenv("AMX_DB_PATH") or root / "data/amx_evidence.db").resolve()
    store = EvidenceStore(db)
    seed_stats = store.import_seed(root / "evidence/index.json")

    app = FastAPI(title="AMilliMATRiX Evidence + House Control Backend", version="2.0.0")
    app.state.repo_root = root
    app.state.store = store
    app.state.seed_stats = seed_stats

    def house_visible(record: dict[str, Any]) -> bool:
        return str(record.get("visibility", "PRIVATE")).upper() in {"HOUSE", "PUBLIC"}

    def visible_evidence() -> list[dict[str, Any]]:
        return [r for r in store.list() if house_visible(r)]

    def t10_contract(records: list[dict[str, Any]]) -> dict[str, Any]:
        return {
            "schema": T10_SCHEMA,
            "fields": list(T10_FIELDS),
            "rule": "Activity is not outcome. A hypothesis is not a finding. A remediation action is not a verified fix until the original condition is retested.",
            "coverage": store.t10_coverage(records),
        }

    origins = [o.strip() for o in os.getenv("AMX_CORS_ORIGINS", "").split(",") if o.strip()]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins or [],
        allow_credentials=False,
        allow_methods=["GET", "POST", "PUT"],
        allow_headers=["Content-Type", "X-AMX-Admin"],
    )

    def require_admin(x_amx_admin: str | None = Header(default=None)) -> None:
        secret = os.getenv("AMX_ADMIN_TOKEN")
        if not secret:
            raise HTTPException(status_code=503, detail="admin writes disabled: AMX_ADMIN_TOKEN is not configured")
        if not x_amx_admin or not hmac.compare_digest(x_amx_admin, secret):
            raise HTTPException(status_code=401, detail="invalid admin credential")

    @app.get("/", include_in_schema=False)
    def public_entry():
        if not (root / "house/remediation/index.html").is_file():
            raise HTTPException(status_code=503, detail="House interface unavailable")
        return RedirectResponse(url="/house", status_code=307)

    @app.get("/api/health")
    def health() -> dict[str, Any]:
        records = visible_evidence()
        return {
            "status": "CONNECTED",
            "backend": "provider-neutral/local",
            "schema_version": SCHEMA_VERSION,
            "state_source": "LOCAL_SNAPSHOT",
            "seed_import": app.state.seed_stats,
            "t10": t10_contract(records),
        }

    @app.get("/api/t10", dependencies=[Depends(require_admin)])
    def t10_status() -> dict[str, Any]:
        state = aggregate_state(root)
        records = visible_evidence()
        return {
            **t10_contract(records),
            "operator": state.get("t10"),
            "truth_screen": state.get("system_truth_t10"),
        }

    @app.get("/api/evidence")
    def list_evidence() -> dict[str, Any]:
        records = visible_evidence()
        return {
            "records": records,
            "count": len(records),
            "state_source": "LOCAL_DB",
            "t10": t10_contract(records),
        }

    @app.get("/api/evidence/{evidence_id}")
    def get_evidence(evidence_id: str) -> dict[str, Any]:
        record = store.get(evidence_id)
        if record is None or not house_visible(record):
            raise HTTPException(status_code=404, detail="evidence record not found")
        return record

    @app.get("/api/evidence/{evidence_id}/versions", dependencies=[Depends(require_admin)])
    def get_evidence_versions(evidence_id: str) -> dict[str, Any]:
        if store.get(evidence_id) is None:
            raise HTTPException(status_code=404, detail="evidence record not found")
        versions = store.versions(evidence_id)
        return {"evidence_id": evidence_id, "versions": versions, "count": len(versions)}

    @app.post("/api/evidence/search")
    def search_evidence(req: SearchRequest) -> dict[str, Any]:
        results = [r for r in store.search(req.query, req.limit * 2) if house_visible(r)][:req.limit]
        return {
            "query": req.query,
            "supported": bool(results),
            "results": results,
            "count": len(results),
            "gap": None if results else "No governed evidence matched this query. UNKNOWN/HOLD over inference.",
            "retrieval": "SQLite FTS5 / deterministic local search",
        }

    @app.put("/api/evidence/{evidence_id}", dependencies=[Depends(require_admin)])
    def put_evidence(evidence_id: str, payload: EvidencePayload) -> dict[str, Any]:
        body = payload.model_dump()
        if body["evidence_id"] != evidence_id:
            raise HTTPException(status_code=400, detail="path evidence_id must match payload evidence_id")
        try:
            record, changed = store.upsert(body)
        except ValueError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc
        return {"record": record, "changed": changed}

    @app.post("/api/evidence/export", dependencies=[Depends(require_admin)])
    def export_evidence() -> dict[str, Any]:
        target = root / "evidence/export.json"
        payload = store.export_projection(target)
        return {
            "path": str(target.relative_to(root)),
            "count": len(payload["records"]),
            "generated_at": payload["generated_at"],
            "t10": payload["t10"],
        }

    @app.get("/api/operator/state", dependencies=[Depends(require_admin)])
    def operator_state() -> dict[str, Any]:
        return aggregate_state(root)

    @app.get("/api/opportunities", dependencies=[Depends(require_admin)])
    def opportunities() -> dict[str, Any]:
        return aggregate_state(root)["opportunities"]

    @app.get("/api/opportunities/{record_key:path}", dependencies=[Depends(require_admin)])
    def opportunity(record_key: str) -> dict[str, Any]:
        import json
        path = root / "overdrive/opportunities.json"
        payload = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {"records": {}}
        record = payload.get("records", {}).get(record_key)
        if record is None:
            raise HTTPException(status_code=404, detail="opportunity not found")

        record = dict(record)
        record["state"] = payment_state(record, record_key)
        if record["state"] == "PAYMENT_UNVERIFIED":
            record.pop("t10", None)
            record.pop("T10", None)
        native_t10 = record.get("t10") or record.get("T10")
        if isinstance(native_t10, dict) and all(str(native_t10.get(field, "")).strip() for field in T10_FIELDS):
            outcome = {field: native_t10[field] for field in T10_FIELDS}
        else:
            evidence_items = record.get("evidence", [])
            evidence_count = len(evidence_items) if isinstance(evidence_items, list) else 0
            outcome = {
                "T10_JOB": str(record.get("next_action") or "Preserve and verify the current commercial outcome without inferring closure."),
                "T10_ACTUAL": (
                    f"Current durable state={record.get('state', 'UNKNOWN')}; "
                    f"execution_owner={record.get('execution_owner', 'UNKNOWN')}; "
                    f"last_action_at={record.get('last_action_at', 'UNKNOWN')}."
                ),
                "T10_EVIDENCE": f"overdrive/opportunities.json::records/{record_key}; embedded evidence items={evidence_count}",
                "T10_CHANGE": "This read exposes the latest durable ledger state only; it does not infer a newer conversion, acceptance, payment, or closure outcome.",
                "T10_REMAINING_GAP": (
                    "This opportunity record does not yet carry native T10 outcome fields. "
                    f"Current next action: {record.get('next_action') or 'not explicitly recorded; closure remains unproven.'}"
                ),
                "T10_PASS": "HOLD",
            }
        return {"record_key": record_key, "record": record, "t10": outcome}

    def proposal_registry() -> dict[str, Any]:
        configured = os.getenv("AMX_PROPOSAL_REGISTRY_PATH", "")
        if not configured:
            raise HTTPException(status_code=404, detail="customer portal disabled")
        path = Path(configured).resolve()
        if path.is_relative_to(root):
            raise HTTPException(status_code=503, detail="proposal registry must be private runtime storage outside the repository")
        if not path.exists():
            return {"schema": "AMX_CARBON_CUSTOMER_PORTAL_V1", "proposals": {}}
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise HTTPException(status_code=503, detail="proposal registry unavailable") from exc
        if not isinstance(payload, dict) or not isinstance(payload.get("proposals"), dict):
            raise HTTPException(status_code=503, detail="proposal registry invalid")
        return payload

    def proposal_projection(portal_token: str) -> dict[str, Any]:
        record = proposal_registry()["proposals"].get(portal_token)
        if not isinstance(record, dict):
            raise HTTPException(status_code=404, detail="proposal not found")

        if str(record.get("status", "")).upper() in {"REVOKED", "CANCELLED"}:
            raise HTTPException(status_code=404, detail="proposal not found")
        public_fields = {"proposal_ref", "business_name", "status", "issued_at", "validity_hours", "full_proposal_url",
                         "headline", "subhead", "visual_note", "visuals", "market_context", "offer", "modules", "sources"}
        projected = {k: v for k, v in record.items() if k in public_fields}
        issued_at = projected.get("issued_at")
        validity_hours = int(projected.get("validity_hours") or 24)
        status = str(projected.get("status") or "DRAFT").upper()
        valid_until = None

        if status in {"REVOKED", "CANCELLED"}:
            quote_status = status
        elif not issued_at:
            quote_status = "DRAFT_NOT_ISSUED"
        else:
            try:
                issued = datetime.fromisoformat(str(issued_at).replace("Z", "+00:00"))
                if issued.tzinfo is None:
                    issued = issued.replace(tzinfo=timezone.utc)
                valid_until_dt = issued.astimezone(timezone.utc) + timedelta(hours=validity_hours)
                valid_until = valid_until_dt.isoformat().replace("+00:00", "Z")
                quote_status = "ACTIVE" if datetime.now(timezone.utc) < valid_until_dt else "EXPIRED"
            except ValueError:
                quote_status = "UNKNOWN"

        projected["portal_token"] = portal_token
        projected["quote_status"] = quote_status
        projected["valid_until"] = valid_until
        projected["validity_hours"] = validity_hours
        return projected

    @app.get("/api/proposals/{portal_token}")
    def customer_proposal(portal_token: str) -> dict[str, Any]:
        return proposal_projection(portal_token)

    @app.post("/api/proposals/{portal_token}/request-change")
    def customer_proposal_change(portal_token: str, payload: ProposalChangeRequest) -> dict[str, Any]:
        proposal = proposal_projection(portal_token)
        allowed = {str(item.get("id")) for item in proposal.get("modules", []) if isinstance(item, dict)}
        selected = sorted({module for module in payload.selected_modules if module in allowed})
        association = proposal_registry()["proposals"][portal_token]
        opportunity_key = association.get("opportunity_key")
        ledger_path = root / "overdrive/opportunities.json"
        ledger = json.loads(ledger_path.read_text()) if ledger_path.exists() else {}
        record = ledger.get("records", {}).get(opportunity_key, {})
        if (record.get("execution_owner") != "PRI" or not record.get("thread_id")
                or association.get("thread_id") != record["thread_id"] or not association.get("customer_id")):
            raise HTTPException(status_code=503, detail="verified PRI customer/thread association required")
        identity = {"opportunity_key": opportunity_key, "thread_id": record["thread_id"],
                    "customer_id": association["customer_id"], "proposal_ref": proposal["proposal_ref"],
                    "action": payload.action, "selected_modules": selected,
                    "message": payload.message.strip(), "contact": payload.contact.strip()}
        request_id = "CPR-" + hashlib.sha256(json.dumps(identity, sort_keys=True).encode()).hexdigest()[:24].upper()
        receipt = {
            "request_id": request_id,
            "received_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "proposal_ref": proposal.get("proposal_ref"),
            **identity,
            "quote_status_at_request": proposal.get("quote_status"),
            "action": payload.action,
            "selected_modules": selected,
            "message": payload.message.strip(),
            "contact": payload.contact.strip(),
            "binding": False,
            "note": "Customer portal request only. It does not automatically modify, accept, invoice, or pay the quote.",
        }
        target = Path(os.getenv("AMX_CUSTOMER_REQUEST_PATH", str(root / "data/proposal_requests.jsonl")))
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open("a+", encoding="utf-8") as handle:
            fcntl.flock(handle, fcntl.LOCK_EX)
            handle.seek(0)
            existing = [json.loads(line) for line in handle if line.strip()]
            if not any(r.get("request_id") == request_id for r in existing):
                handle.seek(0, 2)
                handle.write(json.dumps(receipt, ensure_ascii=False) + "\n")
                handle.flush()
                os.fsync(handle.fileno())
        return {"request_id": request_id, "received": True, "binding": False}

    @app.get("/api/customer-requests/{request_id}", dependencies=[Depends(require_admin)])
    def private_customer_request(request_id: str) -> dict[str, Any]:
        target = Path(os.getenv("AMX_CUSTOMER_REQUEST_PATH", str(root / "data/proposal_requests.jsonl")))
        if target.exists():
            with target.open() as handle:
                fcntl.flock(handle, fcntl.LOCK_SH)
                for line in handle:
                    request = json.loads(line)
                    if request.get("request_id") == request_id:
                        return request
        raise HTTPException(status_code=404, detail="customer request not found")

    @app.get("/api/house/bootstrap")
    def house_bootstrap() -> dict[str, Any]:
        state = aggregate_state(root)
        evidence = visible_evidence()
        gallery = [
            r for r in evidence
            if "carbon" in str(r.get("capability", "")).lower()
            or "production" in str(r.get("capability", "")).lower()
        ]
        return {
            "backend": {
                "status": "DEGRADED" if state.get("adapter_errors") else "CONNECTED",
                "state_source": state["state_source"],
                "refreshed_at": state["refreshed_at"],
                "adapter_errors": state.get("adapter_errors", []),
            },
            "operator": {"state_source": state["state_source"], "refreshed_at": state["refreshed_at"]},
            "evidence": {"count": len(evidence), "records": evidence},
            "gallery": gallery,
            "t10": t10_contract(evidence),
            "controls": {
                "no_false_live_state": True,
                "unknown_hold_over_inference": True,
                "full_ledger_not_routing_subset": True,
                "model_not_matrix": True,
                "t10_outcome_truth": True,
                "activity_not_outcome": True,
                "remediation_requires_original_condition_retest": True,
            },
        }

    house_dir = root / "house/remediation"
    if house_dir.exists():
        @app.get("/house/assets/{asset}")
        def public_asset(asset: str):
            if asset == "config.js":
                from fastapi.responses import Response
                return Response('window.AMX_API_BASE = "";', media_type="application/javascript")
            if asset not in {"house.css", "house.js", "proposal.css", "proposal.js"}:
                raise HTTPException(status_code=404, detail="asset not found")
            path = house_dir / asset
            if path.is_symlink() or not path.is_file():
                raise HTTPException(status_code=404, detail="asset not found")
            return FileResponse(path)

        @app.get("/proposal/{portal_token}")
        @app.get("/proposal/{portal_token}/")
        def customer_proposal_page(portal_token: str):
            proposal_projection(portal_token)
            return FileResponse(house_dir / "proposal.html")

        @app.get("/house")
        @app.get("/house/")
        def house_index():
            return FileResponse(house_dir / "index.html")

    return app


app = create_app()
