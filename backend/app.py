from __future__ import annotations

import hmac
import os
from pathlib import Path
from typing import Any

from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from .state import aggregate_state
from .store import EvidenceStore, SCHEMA_VERSION, T10_FIELDS, T10_SCHEMA


class SearchRequest(BaseModel):
    query: str = Field(min_length=1, max_length=500)
    limit: int = Field(default=8, ge=1, le=50)


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
    visibility: str = "HOUSE"
    tags: list[str] = Field(default_factory=list)


class LearningOutcomePayload(BaseModel):
    outcome_id: str = Field(pattern="^[A-Za-z0-9_-]{1,100}$")
    action: str = Field(min_length=1, max_length=500)
    result: dict[str, Any]
    source: str = Field(min_length=1, max_length=300)


class LessonPayload(BaseModel):
    lesson_id: str
    outcome_id: str
    kind: str
    statement: str = Field(min_length=1, max_length=1000)


class CandidatePayload(BaseModel):
    candidate_id: str
    lesson_id: str
    changes: dict[str, Any]


class PromotionPayload(BaseModel):
    expected_version: int = Field(ge=1)


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
        return str(record.get("visibility", "HOUSE")).upper() not in {"PRIVATE", "SECRET", "INTERNAL_ONLY"}

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

    def learning_role(role: str, supplied: str | None) -> None:
        if os.getenv("AMX_LEARNING_DURABLE_STORAGE") != "accepted":
            raise HTTPException(status_code=503, detail="durable learning storage not accepted")
        secret = os.getenv("AMX_"+role.upper()+"_TOKEN")
        others = [os.getenv("AMX_"+name+"_TOKEN") for name in ("REAPER", "CRITIC", "ROOT") if name.lower() != role]
        if secret and any(other and hmac.compare_digest(secret, other) for other in others):
            raise HTTPException(status_code=503, detail="learning role credentials must be distinct")
        if not secret or not supplied or not hmac.compare_digest(secret, supplied):
            raise HTTPException(status_code=401, detail="worker role credential required")

    def reaper_role(x_amx_reaper: str | None = Header(default=None)) -> None:
        learning_role("reaper", x_amx_reaper)

    def critic_role(x_amx_critic: str | None = Header(default=None)) -> None:
        learning_role("critic", x_amx_critic)

    def root_role(x_amx_root: str | None = Header(default=None)) -> None:
        learning_role("root", x_amx_root)

    def learning():
        from backend.security import local_grants
        from overdrive.evidence_learning import EvidenceLearning
        return EvidenceLearning(store, local_grants(root))

    def learning_action(fn):
        try:
            return fn()
        except (ValueError, PermissionError, KeyError) as exc:
            raise HTTPException(status_code=409, detail=type(exc).__name__+": governed learning action rejected") from None

    @app.get("/api/continuity/state")
    def continuity_state() -> dict[str, Any]:
        return aggregate_state(root)["continuity"]

    @app.post("/api/assets/eligibility", dependencies=[Depends(require_admin)])
    def assets_eligibility(payload: dict[str, Any]) -> dict[str, Any]:
        from .assets import asset_eligibility
        try:
            return asset_eligibility(payload)
        except ValueError:
            raise HTTPException(status_code=422, detail="asset classification required") from None

    @app.get("/api/workers/bounty-reaper/capability", dependencies=[Depends(require_admin)])
    def reaper_capability() -> dict[str, Any]:
        return learning().capability()

    @app.post("/api/workers/bounty-reaper/outcomes", dependencies=[Depends(reaper_role)])
    def reaper_outcome(payload: LearningOutcomePayload) -> dict[str, Any]:
        from .continuity import relative
        try:
            source = root / relative(payload.source)
        except ValueError:
            raise HTTPException(status_code=400, detail="invalid source reference") from None
        if not source.is_file() or source.is_symlink() or source.resolve().parent != (root / "CONTINUITY").resolve():
            raise HTTPException(status_code=400, detail="only enrolled continuity evidence sources are accepted")
        return learning_action(lambda: learning().outcome(payload.outcome_id, payload.action, payload.result, source))

    @app.post("/api/workers/bounty-reaper/lessons", dependencies=[Depends(reaper_role)])
    def reaper_lesson(payload: LessonPayload) -> dict[str, Any]:
        return learning_action(lambda: learning().lesson(payload.lesson_id, payload.outcome_id, payload.kind, payload.statement))

    @app.post("/api/workers/bounty-reaper/candidates", dependencies=[Depends(reaper_role)])
    def reaper_candidate(payload: CandidatePayload) -> dict[str, Any]:
        return learning_action(lambda: learning().candidate(payload.candidate_id, payload.lesson_id, payload.changes))

    @app.post("/api/workers/bounty-reaper/candidates/{candidate_id}/test", dependencies=[Depends(critic_role)])
    def critic_test(candidate_id: str) -> dict[str, Any]:
        return learning_action(lambda: learning().test_candidate(candidate_id, "Critic"))

    @app.post("/api/workers/bounty-reaper/candidates/{candidate_id}/promote", dependencies=[Depends(root_role)])
    def root_promote(candidate_id: str, payload: PromotionPayload) -> dict[str, Any]:
        return learning_action(lambda: learning().promote(candidate_id, payload.expected_version, "Root"))

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

    @app.get("/api/t10")
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

    @app.get("/api/evidence/{evidence_id}/versions")
    def get_evidence_versions(evidence_id: str) -> dict[str, Any]:
        current = store.get(evidence_id)
        if current is None or not house_visible(current):
            raise HTTPException(status_code=404, detail="evidence record not found")
        versions = [v for v in store.versions(evidence_id) if house_visible(v["payload"])]
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

    @app.get("/api/operator/state")
    def operator_state() -> dict[str, Any]:
        return aggregate_state(root)

    @app.get("/api/opportunities")
    def opportunities() -> dict[str, Any]:
        return aggregate_state(root)["opportunities"]

    @app.get("/api/opportunities/{record_key:path}")
    def opportunity(record_key: str) -> dict[str, Any]:
        import json
        path = root / "overdrive/opportunities.json"
        payload = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {"records": {}}
        record = payload.get("records", {}).get(record_key)
        if record is None:
            raise HTTPException(status_code=404, detail="opportunity not found")

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
            "operator": state,
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
        app.mount("/house/assets", StaticFiles(directory=house_dir), name="house-assets")

        @app.get("/house")
        @app.get("/house/")
        def house_index():
            return FileResponse(house_dir / "index.html")

    return app


app = create_app()
