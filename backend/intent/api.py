from __future__ import annotations

import hmac
import os
from pathlib import Path
from typing import Any, Callable

from fastapi import FastAPI, Header, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel

from .directory import CanonicalDirectory
from .engine import SearchEngine
from .models import (
    ActionRequest,
    CandidateInput,
    CONTRACT_VERSION,
    EntityType,
    FeedbackRequest,
    PivotRequest,
    SearchIntentRequest,
    SearchScope,
)
from .providers import FileMarketplaceProvider, JsonHttpExternalProvider
from .store import SearchSessionStore


class SearchContractResponse(BaseModel):
    contract_version: str = CONTRACT_VERSION
    product: str = "CARBON° Search"
    intelligence_layer: str = "INTELLAGENT"
    positioning: str = "Engine of Intent"
    mandatory_gates: int = 35
    max_intent_pivots: int = 2
    deterministic_evidence_endpoint_preserved: str = "/api/evidence/search"


def _secure_equal(provided: str | None, expected: str | None) -> bool:
    return bool(provided and expected and hmac.compare_digest(provided, expected))


def mount_search(
    app: FastAPI,
    root: Path,
    evidence_store: Any,
    house_visible: Callable[[dict[str, Any]], bool],
) -> SearchEngine:
    root = Path(root)
    directory = CanonicalDirectory(root / "house/search/CARBON_SEARCH_DIRECTORY_V1.json")
    sessions = SearchSessionStore(Path(os.getenv("AMX_SEARCH_DB_PATH", str(root / "data/carbon_search.db"))))

    def evidence_search(query: str, limit: int) -> list[CandidateInput]:
        out: list[CandidateInput] = []
        for record in evidence_store.search(query, limit * 2):
            if not house_visible(record):
                continue
            evidence_id = str(record.get("evidence_id") or record.get("capability") or "record")
            out.append(CandidateInput(
                candidate_id=f"evidence:{evidence_id}",
                title=str(record.get("artifact") or record.get("capability") or evidence_id),
                summary=str(record.get("interview_safe_explanation") or record.get("role_contribution") or ""),
                entity_id=f"evidence:{evidence_id}",
                entity_type=EntityType.EVIDENCE_RECORD,
                attributes={
                    "status": record.get("status_freshness"),
                    "t10_pass": record.get("T10_PASS"),
                },
                source=str(record.get("authoritative_source") or "evidence_house"),
                source_type="GOVERNED_EVIDENCE",
                visibility=SearchScope.PUBLIC,
                evidence_pointer=str(record.get("source_pointer") or evidence_id),
                action={"name": "OPEN"},
            ))
            if len(out) >= limit:
                break
        return out

    external = JsonHttpExternalProvider.from_env()
    marketplace = FileMarketplaceProvider.from_env()
    engine = SearchEngine(
        root=root,
        session_store=sessions,
        directory=directory,
        evidence_search=evidence_search,
        external_search=external.search if external else None,
        marketplace_search=marketplace.search if marketplace else None,
    )
    app.state.carbon_search_engine = engine

    def allowed_scopes(surface: str, x_amx_admin: str | None, x_carbon_client: str | None) -> set[SearchScope]:
        allowed = {SearchScope.PUBLIC, SearchScope.EXTERNAL_WEB}
        if surface in {"matrix", "internal"}:
            if not _secure_equal(x_amx_admin, os.getenv("AMX_ADMIN_TOKEN")):
                raise HTTPException(status_code=401, detail="matrix/internal Search requires AMX admin authority")
            allowed.update({
                SearchScope.CARBON_INTERNAL,
                SearchScope.CARBON_MARKETPLACE,
                SearchScope.CLIENT_SPACE,
                SearchScope.MATRIX_INTERNAL,
                SearchScope.CONNECTED_DATA,
            })
        elif surface == "client":
            if not _secure_equal(x_carbon_client, os.getenv("AMX_SEARCH_CLIENT_TOKEN")):
                raise HTTPException(status_code=401, detail="client Search requires client authority")
            allowed.update({SearchScope.CLIENT_SPACE, SearchScope.CARBON_MARKETPLACE})
        return allowed

    def authorize_session(session_id: str, x_amx_admin: str | None, x_carbon_client: str | None):
        session = engine.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="search session not found")
        if session.surface in {"matrix", "internal"} and not _secure_equal(x_amx_admin, os.getenv("AMX_ADMIN_TOKEN")):
            raise HTTPException(status_code=401, detail="session requires AMX admin authority")
        if session.surface == "client" and not _secure_equal(x_carbon_client, os.getenv("AMX_SEARCH_CLIENT_TOKEN")):
            raise HTTPException(status_code=401, detail="session requires client authority")
        return session

    @app.get("/api/search/contract", response_model=SearchContractResponse)
    def search_contract():
        return SearchContractResponse()

    @app.get("/api/search/health")
    def search_health() -> dict[str, Any]:
        return {
            "status": "CONNECTED",
            "contract_version": CONTRACT_VERSION,
            "engine": "INTELLAGENT",
            "positioning": "Engine of Intent",
            "mandatory_gates": 35,
            "external_provider": external.name if external else "UNCONFIGURED",
            "marketplace_provider": marketplace.name if marketplace else "UNCONFIGURED",
        }

    @app.post("/api/search/intent")
    def search_intent(
        request: SearchIntentRequest,
        x_amx_admin: str | None = Header(default=None),
        x_carbon_client: str | None = Header(default=None),
    ):
        allowed = allowed_scopes(request.surface, x_amx_admin, x_carbon_client)
        try:
            return engine.search(request, allowed)
        except PermissionError as exc:
            raise HTTPException(status_code=403, detail=str(exc)) from exc

    @app.get("/api/search/sessions/{session_id}")
    def get_search_session(
        session_id: str,
        x_amx_admin: str | None = Header(default=None),
        x_carbon_client: str | None = Header(default=None),
    ):
        return authorize_session(session_id, x_amx_admin, x_carbon_client)

    @app.get("/api/search/sessions/{session_id}/evidence")
    def get_search_evidence(
        session_id: str,
        x_amx_admin: str | None = Header(default=None),
        x_carbon_client: str | None = Header(default=None),
    ):
        authorize_session(session_id, x_amx_admin, x_carbon_client)
        return engine.evidence(session_id)

    @app.post("/api/search/sessions/{session_id}/pivot")
    def post_pivot(
        session_id: str,
        payload: PivotRequest,
        x_amx_admin: str | None = Header(default=None),
        x_carbon_client: str | None = Header(default=None),
    ):
        authorize_session(session_id, x_amx_admin, x_carbon_client)
        try:
            return engine.pivot(session_id, payload)
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except ValueError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc

    @app.post("/api/search/sessions/{session_id}/feedback")
    def post_feedback(
        session_id: str,
        payload: FeedbackRequest,
        x_amx_admin: str | None = Header(default=None),
        x_carbon_client: str | None = Header(default=None),
    ):
        authorize_session(session_id, x_amx_admin, x_carbon_client)
        try:
            return engine.feedback(session_id, payload)
        except PermissionError as exc:
            raise HTTPException(status_code=403, detail=str(exc)) from exc

    @app.post("/api/search/sessions/{session_id}/action")
    def post_action(
        session_id: str,
        payload: ActionRequest,
        x_amx_admin: str | None = Header(default=None),
        x_carbon_client: str | None = Header(default=None),
    ):
        authorize_session(session_id, x_amx_admin, x_carbon_client)
        try:
            return engine.action(session_id, payload)
        except PermissionError as exc:
            raise HTTPException(status_code=403, detail=str(exc)) from exc

    ui = root / "house/remediation/search.html"
    if ui.is_file():
        @app.get("/search", include_in_schema=False)
        def search_page():
            return FileResponse(ui)

    return engine
