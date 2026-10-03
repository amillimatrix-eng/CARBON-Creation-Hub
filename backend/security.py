"""Scoped capabilities for existing workers. A queue is not a grant."""
from __future__ import annotations

import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

CAPABILITIES = (
    "read_governance", "write_governance", "read_commercial_data",
    "send_external_communication", "execute_shell", "access_network",
    "access_credentials", "modify_production_code", "deploy",
    "access_financial_rails", "spend_funds", "sign_transactions",
    "read_private_assets", "write_receipts", "alter_worker_mandate",
)


def fingerprint(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def authorize(grants: dict[str, Any], worker: str, capability: str, scope: str) -> str:
    if capability not in CAPABILITIES or not scope:
        raise PermissionError("UNKNOWN_OR_UNSCOPED_CAPABILITY")
    for g in grants.get("grants", []):
        if g.get("worker_id") != worker or g.get("capability") != capability or g.get("state") != "ACTIVE":
            continue
        if scope not in g.get("scopes", []) or not g.get("authority_receipt") or not g.get("grant_id"):
            continue
        if g.get("expires_at") and datetime.fromisoformat(g["expires_at"].replace("Z", "+00:00")) <= datetime.now(timezone.utc):
            continue
        return g["grant_id"]
    raise PermissionError("CAPABILITY_HOLD_EXPLICIT_GRANT_REQUIRED")


def local_grants(repo: Path) -> dict[str, Any]:
    # The installed service pins policy. Public queue changes cannot expand it.
    path = Path(os.environ.get("BLACK_GRANTS_FILE", repo / "CONTINUITY/capability-grants.json"))
    if "BLACK_GRANTS_FILE" in os.environ:
        from .continuity import private_file
        private_file(path)
    raw = path.read_bytes()
    expected = os.environ.get("BLACK_GRANTS_SHA256")
    if expected and hashlib.sha256(raw).hexdigest() != expected:
        raise PermissionError("GRANT_POLICY_HASH_MISMATCH")
    policy = json.loads(raw)
    if policy.get("schema") != "AMX.CAPABILITY.GRANTS.v1":
        raise PermissionError("UNSUPPORTED_GRANT_POLICY")
    return policy


def authorized_job(job: dict[str, Any], grants: dict[str, Any]) -> dict[str, str]:
    if job.get("worker", "BLACK") != "BLACK":
        raise PermissionError("WRONG_WORKER_OWNER")
    adapter = job.get("adapter")
    if adapter in {"continuity_sync", "continuity_verify", "continuity_restore_test", "continuity_health"}:
        grant = authorize(grants, "BLACK", "read_governance", adapter)
        authorize(grants, "BLACK", "write_receipts", "continuity")
        if adapter == "continuity_sync":
            authorize(grants, "BLACK", "access_credentials", "continuity-key-and-drive-read-only")
        return {"adapter": adapter, "grant_id": grant}
    command = job.get("command")
    if not isinstance(command, list) or not command or any(not isinstance(a, str) or "\0" in a for a in command):
        raise PermissionError("UNSUPPORTED_JOB_REQUIRES_CAPABILITY_REMEDIATION")
    # Legacy shell capability remains discoverable. An exact argv digest is required,
    # never a wildcard command, global shell access or a public queue-only approval.
    scope = fingerprint(command)
    grant = authorize(grants, "BLACK", "execute_shell", scope)
    authorize(grants, "BLACK", "write_receipts", "black-jobs")
    return {"adapter": "scoped_command", "grant_id": grant, "command_sha256": scope}
