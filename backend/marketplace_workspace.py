from __future__ import annotations

import json
from typing import Any
from urllib.parse import urlparse

from fastapi import APIRouter, FastAPI, Header, HTTPException
from pydantic import BaseModel, Field

from .marketplace import MarketplaceStore, actor_ref, iso, public_id

PROJECT_STATES = {"DRAFT", "ACTIVE", "READY", "DELIVERED", "ARCHIVED"}
MEDIA_TYPES = {"IMAGE", "VIDEO", "AUDIO", "DOCUMENT", "LISTING_PACKAGE"}
GENERATIVE_ACTIONS = {"CREATE_IMAGE", "CREATE_SHORT_VIDEO", "CREATE_AUDIO", "CREATE_LISTING_PACKAGE"}


class ProjectCreate(BaseModel):
    title: str = Field(min_length=1, max_length=120)
    description: str = Field(default="", max_length=2000)
    linked_search_session_id: str | None = Field(default=None, max_length=200)
    linked_marketplace_entity_ids: list[str] = Field(default_factory=list, max_length=20)


class ProjectUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=120)
    description: str | None = Field(default=None, max_length=2000)
    lifecycle_state: str | None = None
    linked_search_session_id: str | None = Field(default=None, max_length=200)
    linked_marketplace_entity_ids: list[str] | None = Field(default=None, max_length=20)


class MediaActionRequest(BaseModel):
    action_type: str = Field(pattern="^(ATTACH_REFERENCE|CREATE_IMAGE|CREATE_SHORT_VIDEO|CREATE_AUDIO|CREATE_LISTING_PACKAGE)$")
    project_id: str | None = Field(default=None, max_length=80)
    source_artifact_ids: list[str] = Field(default_factory=list, max_length=20)
    user_brief: str = Field(default="", max_length=2000)
    constraints: dict[str, Any] = Field(default_factory=dict)
    target_format: str | None = Field(default=None, max_length=80)
    authorized_context: str = Field(default="USER_REQUESTED", max_length=120)
    storage_mode: str = Field(default="REFERENCE_ONLY", pattern="^(REFERENCE_ONLY|CARBON_HOSTED|BYO_STORAGE|LOCAL_MINIMAL)$")


def ensure_workspace_schema(store: MarketplaceStore) -> None:
    with store._conn() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS carbon_projects (
                project_id TEXT PRIMARY KEY,
                owner_scope TEXT NOT NULL,
                title TEXT NOT NULL,
                description TEXT NOT NULL DEFAULT '',
                lifecycle_state TEXT NOT NULL DEFAULT 'DRAFT',
                linked_search_session_id TEXT,
                linked_marketplace_entity_ids_json TEXT NOT NULL DEFAULT '[]',
                media_asset_ids_json TEXT NOT NULL DEFAULT '[]',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                last_action TEXT NOT NULL,
                next_action TEXT
            );
            CREATE INDEX IF NOT EXISTS idx_carbon_projects_owner_updated
                ON carbon_projects(owner_scope, updated_at DESC);

            CREATE TABLE IF NOT EXISTS carbon_media_assets (
                artifact_id TEXT PRIMARY KEY,
                owner_scope TEXT NOT NULL,
                workspace_id TEXT NOT NULL,
                project_id TEXT REFERENCES carbon_projects(project_id),
                media_type TEXT NOT NULL,
                title TEXT NOT NULL,
                object_reference TEXT NOT NULL,
                preview_reference TEXT,
                source_type TEXT NOT NULL,
                provider TEXT,
                provider_job_id TEXT,
                version INTEGER NOT NULL DEFAULT 1,
                lifecycle_state TEXT NOT NULL,
                visibility_acl_json TEXT NOT NULL,
                rights_state TEXT NOT NULL,
                commercial_use_state TEXT NOT NULL,
                provenance_pointer TEXT NOT NULL,
                content_hash TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );
            CREATE INDEX IF NOT EXISTS idx_carbon_media_owner_updated
                ON carbon_media_assets(owner_scope, updated_at DESC);
            CREATE INDEX IF NOT EXISTS idx_carbon_media_project
                ON carbon_media_assets(project_id, updated_at DESC);

            CREATE TABLE IF NOT EXISTS carbon_media_actions (
                action_id TEXT PRIMARY KEY,
                owner_scope TEXT NOT NULL,
                project_id TEXT,
                action_type TEXT NOT NULL,
                state TEXT NOT NULL,
                provider_route TEXT NOT NULL,
                created_artifact_ids_json TEXT NOT NULL DEFAULT '[]',
                hold_reason TEXT,
                request_json TEXT NOT NULL,
                receipt_pointer TEXT NOT NULL,
                created_at TEXT NOT NULL
            );
            CREATE INDEX IF NOT EXISTS idx_carbon_media_actions_owner
                ON carbon_media_actions(owner_scope, created_at DESC);
            """
        )


def _json(value: str | None, default: Any) -> Any:
    try:
        return json.loads(value) if value else default
    except (TypeError, json.JSONDecodeError):
        return default


def _project(row: Any) -> dict[str, Any]:
    value = dict(row)
    value["linked_marketplace_entity_ids"] = _json(value.pop("linked_marketplace_entity_ids_json", "[]"), [])
    value["media_asset_ids"] = _json(value.pop("media_asset_ids_json", "[]"), [])
    return value


def _media(row: Any) -> dict[str, Any]:
    value = dict(row)
    value["visibility_acl"] = _json(value.pop("visibility_acl_json", "{}"), {})
    return value


def _action(row: Any) -> dict[str, Any]:
    value = dict(row)
    value["created_artifact_ids"] = _json(value.pop("created_artifact_ids_json", "[]"), [])
    value["request"] = _json(value.pop("request_json", "{}"), {})
    return value


def _public_reference(value: Any) -> str:
    reference = str(value or "").strip()
    if reference.startswith("/market/demo/") and ".." not in reference.split("/"):
        return reference
    parsed = urlparse(reference)
    if parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password:
        raise ValueError("reference must be an HTTPS URL or an allowlisted /market/demo/ path")
    if any(ch in reference for ch in ("\r", "\n", "\\x00")):
        raise ValueError("reference contains invalid characters")
    return reference


def mount_workspace_api(app: FastAPI, store: MarketplaceStore) -> None:
    """Mount Projects and Media on the existing CARBON° marketplace store/runtime."""
    ensure_workspace_schema(store)
    router = APIRouter()

    def current_actor(x_carbon_actor: str | None = Header(default=None)) -> str:
        if not x_carbon_actor:
            raise HTTPException(status_code=401, detail="X-CARBON-Actor is required")
        try:
            return actor_ref(x_carbon_actor)
        except ValueError as exc:
            raise HTTPException(status_code=401, detail=str(exc)) from exc

    def require_demo() -> None:
        if not bool(getattr(app.state, "carbon_marketplace_demo_enabled", False)):
            raise HTTPException(
                status_code=503,
                detail="workspace actions are fail-closed until production identity and storage providers are configured",
            )

    def owned_project(conn: Any, project_id: str, owner: str) -> Any:
        row = conn.execute(
            "SELECT * FROM carbon_projects WHERE project_id=? AND owner_scope=?",
            (project_id, owner),
        ).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="project not found")
        return row

    def owned_media(conn: Any, artifact_id: str, owner: str) -> Any:
        row = conn.execute(
            "SELECT * FROM carbon_media_assets WHERE artifact_id=? AND owner_scope=?",
            (artifact_id, owner),
        ).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="media item not found")
        return row

    @router.get("/api/carbon/projects")
    def list_projects(x_carbon_actor: str | None = Header(default=None)) -> dict[str, Any]:
        require_demo()
        owner = current_actor(x_carbon_actor)
        with store._conn() as conn:
            rows = conn.execute(
                "SELECT * FROM carbon_projects WHERE owner_scope=? ORDER BY updated_at DESC",
                (owner,),
            ).fetchall()
        records = [_project(row) for row in rows]
        return {"records": records, "count": len(records), "owner_scope": owner}

    @router.post("/api/carbon/projects")
    def create_project(payload: ProjectCreate, x_carbon_actor: str | None = Header(default=None)) -> dict[str, Any]:
        require_demo()
        owner = current_actor(x_carbon_actor)
        now = iso()
        project_id = public_id("PRJ")
        with store._conn() as conn:
            conn.execute(
                """INSERT INTO carbon_projects
                   (project_id,owner_scope,title,description,lifecycle_state,linked_search_session_id,
                    linked_marketplace_entity_ids_json,media_asset_ids_json,created_at,updated_at,last_action,next_action)
                   VALUES (?,?,?,?,?,?,?,?,?,?,?,?)""",
                (
                    project_id, owner, payload.title.strip(), payload.description.strip(), "ACTIVE",
                    payload.linked_search_session_id,
                    json.dumps(payload.linked_marketplace_entity_ids),
                    "[]", now, now, "PROJECT_CREATED",
                    "Attach a public reference or request a media action; generated media remains held until a provider route is configured.",
                ),
            )
            conn.execute(
                "INSERT INTO events(entity_kind,entity_id,actor_ref,event_type,payload_json,created_at) VALUES (?,?,?,?,?,?)",
                ("project", project_id, owner, "PROJECT_CREATED",
                 json.dumps({"title": payload.title.strip(), "lifecycle_state": "ACTIVE"}, sort_keys=True), now),
            )
            row = conn.execute("SELECT * FROM carbon_projects WHERE project_id=?", (project_id,)).fetchone()
        return {"record": _project(row), "receipt_pointer": f"/api/carbon/projects/{project_id}"}

    @router.get("/api/carbon/projects/{project_id}")
    def get_project(project_id: str, x_carbon_actor: str | None = Header(default=None)) -> dict[str, Any]:
        require_demo()
        owner = current_actor(x_carbon_actor)
        with store._conn() as conn:
            row = owned_project(conn, project_id, owner)
            project = _project(row)
            media_rows = conn.execute(
                "SELECT * FROM carbon_media_assets WHERE project_id=? AND owner_scope=? ORDER BY updated_at DESC",
                (project_id, owner),
            ).fetchall()
        project["media"] = [_media(item) for item in media_rows]
        return {"record": project, "count": len(project["media"])}

    @router.patch("/api/carbon/projects/{project_id}")
    def update_project(project_id: str, payload: ProjectUpdate, x_carbon_actor: str | None = Header(default=None)) -> dict[str, Any]:
        require_demo()
        owner = current_actor(x_carbon_actor)
        updates = payload.model_dump(exclude_unset=True)
        if "lifecycle_state" in updates and updates["lifecycle_state"] not in PROJECT_STATES:
            raise HTTPException(status_code=422, detail="unsupported project lifecycle state")
        if "linked_marketplace_entity_ids" in updates and updates["linked_marketplace_entity_ids"] is None:
            updates.pop("linked_marketplace_entity_ids")
        if "title" in updates and updates["title"] is not None:
            updates["title"] = updates["title"].strip()
        if "description" in updates and updates["description"] is not None:
            updates["description"] = updates["description"].strip()
        now = iso()
        with store._conn() as conn:
            current = owned_project(conn, project_id, owner)
            project = _project(current)
            values = {
                "title": updates.get("title", project["title"]),
                "description": updates.get("description", project["description"]),
                "lifecycle_state": updates.get("lifecycle_state", project["lifecycle_state"]),
                "linked_search_session_id": updates.get("linked_search_session_id", project["linked_search_session_id"]),
                "linked_marketplace_entity_ids_json": json.dumps(updates.get("linked_marketplace_entity_ids", project["linked_marketplace_entity_ids"])),
                "updated_at": now,
                "last_action": "PROJECT_UPDATED",
            }
            conn.execute(
                """UPDATE carbon_projects SET title=?,description=?,lifecycle_state=?,linked_search_session_id=?,
                   linked_marketplace_entity_ids_json=?,updated_at=?,last_action=? WHERE project_id=? AND owner_scope=?""",
                (values["title"], values["description"], values["lifecycle_state"], values["linked_search_session_id"],
                 values["linked_marketplace_entity_ids_json"], now, values["last_action"], project_id, owner),
            )
            conn.execute(
                "INSERT INTO events(entity_kind,entity_id,actor_ref,event_type,payload_json,created_at) VALUES (?,?,?,?,?,?)",
                ("project", project_id, owner, "PROJECT_UPDATED",
                 json.dumps({"lifecycle_state": values["lifecycle_state"]}, sort_keys=True), now),
            )
            row = conn.execute("SELECT * FROM carbon_projects WHERE project_id=?", (project_id,)).fetchone()
        return {"record": _project(row), "receipt_pointer": f"/api/carbon/projects/{project_id}"}

    @router.get("/api/carbon/media")
    def list_media(project_id: str | None = None, x_carbon_actor: str | None = Header(default=None)) -> dict[str, Any]:
        require_demo()
        owner = current_actor(x_carbon_actor)
        with store._conn() as conn:
            if project_id:
                owned_project(conn, project_id, owner)
                rows = conn.execute(
                    "SELECT * FROM carbon_media_assets WHERE owner_scope=? AND project_id=? ORDER BY updated_at DESC",
                    (owner, project_id),
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT * FROM carbon_media_assets WHERE owner_scope=? ORDER BY updated_at DESC",
                    (owner,),
                ).fetchall()
        records = [_media(row) for row in rows]
        return {"records": records, "count": len(records), "owner_scope": owner}

    @router.get("/api/carbon/media/{artifact_id}")
    def get_media(artifact_id: str, x_carbon_actor: str | None = Header(default=None)) -> dict[str, Any]:
        require_demo()
        owner = current_actor(x_carbon_actor)
        with store._conn() as conn:
            row = owned_media(conn, artifact_id, owner)
        return {"record": _media(row)}

    @router.post("/api/carbon/media/actions")
    def media_action(payload: MediaActionRequest, x_carbon_actor: str | None = Header(default=None)) -> dict[str, Any]:
        require_demo()
        owner = current_actor(x_carbon_actor)
        now = iso()
        action_id = public_id("ACT")
        request_payload = payload.model_dump()
        created_ids: list[str] = []
        state = "HOLD"
        provider_route = "UNCONFIGURED"
        hold_reason = "NO_AUTHORIZED_MEDIA_PROVIDER_ROUTE"

        with store._conn() as conn:
            if payload.project_id:
                owned_project(conn, payload.project_id, owner)

            if payload.action_type == "ATTACH_REFERENCE":
                if payload.storage_mode != "REFERENCE_ONLY":
                    hold_reason = "STORAGE_MODE_NOT_CONFIGURED"
                else:
                    existing_ids = list(dict.fromkeys(payload.source_artifact_ids))
                    if existing_ids:
                        for artifact_id in existing_ids:
                            owned_media(conn, artifact_id, owner)
                        created_ids = existing_ids
                    else:
                        try:
                            reference = _public_reference(payload.constraints.get("object_reference"))
                        except ValueError as exc:
                            raise HTTPException(status_code=422, detail=str(exc)) from exc
                        media_type = str(payload.constraints.get("media_type", "DOCUMENT")).upper()
                        if media_type not in MEDIA_TYPES:
                            raise HTTPException(status_code=422, detail="unsupported media type")
                        title = str(payload.constraints.get("title") or payload.user_brief or "External reference").strip()[:160]
                        if not title:
                            raise HTTPException(status_code=422, detail="title is required for an external reference")
                        artifact_id = public_id("MED")
                        acl = {
                            "owner_scope": owner,
                            "metadata_visibility": "OWNER_ONLY",
                            "object_access": "EXTERNAL_REFERENCE_MAY_BE_PUBLIC",
                        }
                        conn.execute(
                            """INSERT INTO carbon_media_assets
                               (artifact_id,owner_scope,workspace_id,project_id,media_type,title,object_reference,
                                preview_reference,source_type,provider,provider_job_id,version,lifecycle_state,
                                visibility_acl_json,rights_state,commercial_use_state,provenance_pointer,content_hash,
                                created_at,updated_at)
                               VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                            (artifact_id, owner, owner, payload.project_id, media_type, title, reference, reference,
                             "EXTERNAL_REFERENCE", None, None, 1, "READY_FOR_REVIEW", json.dumps(acl, sort_keys=True),
                             "UNVERIFIED", "HOLD", str(payload.source_artifact_ids[0] if payload.source_artifact_ids else reference),
                             None, now, now),
                        )
                        created_ids = [artifact_id]
                        if payload.project_id:
                            project_row = owned_project(conn, payload.project_id, owner)
                            project = _project(project_row)
                            media_ids = list(dict.fromkeys(project["media_asset_ids"] + created_ids))
                            conn.execute(
                                """UPDATE carbon_projects SET media_asset_ids_json=?,updated_at=?,last_action=?
                                   WHERE project_id=? AND owner_scope=?""",
                                (json.dumps(media_ids), now, "MEDIA_REFERENCE_ATTACHED", payload.project_id, owner),
                            )
                    state = "COMPLETED"
                    provider_route = "REFERENCE_ONLY"
                    hold_reason = None
                    conn.execute(
                        "INSERT INTO events(entity_kind,entity_id,actor_ref,event_type,payload_json,created_at) VALUES (?,?,?,?,?,?)",
                        ("media_action", action_id, owner, "MEDIA_REFERENCE_ATTACHED",
                         json.dumps({"project_id": payload.project_id, "artifact_ids": created_ids}, sort_keys=True), now),
                    )
            conn.execute(
                """INSERT INTO carbon_media_actions
                   (action_id,owner_scope,project_id,action_type,state,provider_route,created_artifact_ids_json,
                    hold_reason,request_json,receipt_pointer,created_at)
                   VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
                (action_id, owner, payload.project_id, payload.action_type, state, provider_route,
                 json.dumps(created_ids), hold_reason, json.dumps(request_payload, sort_keys=True),
                 f"/api/carbon/media/actions/{action_id}", now),
            )
            if state == "HOLD":
                conn.execute(
                    "INSERT INTO events(entity_kind,entity_id,actor_ref,event_type,payload_json,created_at) VALUES (?,?,?,?,?,?)",
                    ("media_action", action_id, owner, "MEDIA_ACTION_HELD",
                     json.dumps({"action_type": payload.action_type, "hold_reason": hold_reason}, sort_keys=True), now),
                )
            row = conn.execute("SELECT * FROM carbon_media_actions WHERE action_id=?", (action_id,)).fetchone()
        return {"record": _action(row), "receipt_pointer": f"/api/carbon/media/actions/{action_id}"}

    @router.get("/api/carbon/media/actions/{action_id}")
    def get_media_action(action_id: str, x_carbon_actor: str | None = Header(default=None)) -> dict[str, Any]:
        require_demo()
        owner = current_actor(x_carbon_actor)
        with store._conn() as conn:
            row = conn.execute(
                "SELECT * FROM carbon_media_actions WHERE action_id=? AND owner_scope=?",
                (action_id, owner),
            ).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="media action not found")
        return {"record": _action(row)}

    app.include_router(router)
