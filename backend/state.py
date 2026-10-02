from __future__ import annotations

import base64
import json
import os
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class StateReader:
    """Optional live GitHub adapter with local durable-state fallback."""

    def __init__(self, repo_root: Path):
        self.repo_root = Path(repo_root)
        self.github_repo = os.getenv("AMX_GITHUB_REPO", "").strip()
        self.github_ref = os.getenv("AMX_GITHUB_REF", "main").strip() or "main"
        self.github_token = os.getenv("AMX_GITHUB_TOKEN", "").strip()
        self.errors: list[str] = []
        self.used_live = False

    def _github_json(self, relative: str) -> Any:
        path = urllib.parse.quote(relative, safe="/")
        ref = urllib.parse.quote(self.github_ref, safe="")
        headers = {"User-Agent": "amx-evidence-house/1.0"}

        # Public repositories do not need the authenticated Contents API.
        # Prefer raw GitHub when no token is configured so live readback is not
        # coupled to API auth/rate-limit behavior. Private repos still use the
        # authenticated Contents API path.
        if not self.github_token:
            url = f"https://raw.githubusercontent.com/{self.github_repo}/{ref}/{path}"
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=10) as response:
                raw = response.read()
            self.used_live = True
            return json.loads(raw.decode("utf-8"))

        url = f"https://api.github.com/repos/{self.github_repo}/contents/{path}?ref={ref}"
        headers["Accept"] = "application/vnd.github+json"
        headers["Authorization"] = f"Bearer {self.github_token}"
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as response:
            body = json.loads(response.read().decode("utf-8"))
        if body.get("encoding") != "base64" or "content" not in body:
            raise ValueError("GitHub contents response did not contain base64 file content")
        raw = base64.b64decode(body["content"])
        self.used_live = True
        return json.loads(raw.decode("utf-8"))

    def read_json(self, relative: str, default: Any = None) -> Any:
        if self.github_repo:
            try:
                return self._github_json(relative)
            except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, ValueError, json.JSONDecodeError) as exc:
                self.errors.append(f"{relative}: {type(exc).__name__}")
        path = self.repo_root / relative
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except (FileNotFoundError, json.JSONDecodeError):
            return default

    @property
    def source_label(self) -> str:
        if self.github_repo and self.used_live and not self.errors:
            return "GITHUB_LIVE"
        if self.github_repo and self.used_live:
            return "MIXED_GITHUB_LIVE_AND_LOCAL_FALLBACK"
        if self.github_repo and self.errors:
            return "LOCAL_SNAPSHOT_AFTER_GITHUB_READ_FAILURE"
        return "LOCAL_SNAPSHOT"


def worker_display_state(contract: dict[str, Any]) -> dict[str, Any]:
    status = str(contract.get("status", "UNKNOWN"))
    runtime = (((contract.get("execution") or {}).get("decision_runtime")) or {})
    acceptance = str(runtime.get("acceptance_state") or ((contract.get("acceptance_v2") or {}).get("state")) or "UNKNOWN")
    enabled = str(runtime.get("state", "UNKNOWN")).upper() == "ENABLED"
    truth = (((contract.get("current_evidence") or {}).get("truth")) or "UNKNOWN")
    execution_proven = (
        "EXECUTING" in truth.upper()
        and "NOT PROVEN" not in truth.upper()
        and "NOT_RECOVERED" not in truth.upper()
        and "PENDING" not in acceptance.upper()
    )
    display = "EXECUTING" if execution_proven else ("ENABLED / EXECUTION_NOT_PROVEN" if enabled else "UNAVAILABLE_OR_UNKNOWN")
    return {
        "configured_status": status,
        "runtime_enabled": enabled,
        "acceptance_state": acceptance,
        "execution_truth": truth,
        "display_state": display,
    }


def summarize_opportunities(opps: dict[str, Any]) -> dict[str, Any]:
    records = opps.get("records", {}) if isinstance(opps, dict) else {}
    counts: dict[str, int] = {}
    due: list[dict[str, Any]] = []
    now = utcnow()
    for key, record in records.items():
        state = str(record.get("state", "UNKNOWN"))
        counts[state] = counts.get(state, 0) + 1
        due_at = record.get("due_at")
        is_due = False
        if due_at:
            try:
                dt = datetime.fromisoformat(due_at.replace("Z", "+00:00"))
                is_due = dt <= now
            except ValueError:
                pass
        if is_due or state in {"QUALIFIED", "RESPONDED", "DELIVERY_FAILED"}:
            due.append({
                "record_key": key,
                "organization": record.get("organization"),
                "state": state,
                "due_at": due_at,
                "next_action": record.get("next_action"),
                "execution_owner": record.get("execution_owner"),
            })
    paid = [k for k, r in records.items() if str(r.get("state", "")).upper() == "PAID"]
    return {
        "total_records": len(records),
        "state_counts": counts,
        "due_or_actionable": due,
        "paid_record_count": len(paid),
        "paid_record_keys": paid,
        "realized_revenue_evidence": {"present": bool(paid), "rule": "PAID requires payment evidence; no PAID record means realized revenue remains unproven."},
    }


def aggregate_state(repo_root: Path) -> dict[str, Any]:
    reader = StateReader(repo_root)
    worker = reader.read_json("overdrive/worker_contract.json", {})
    opps = reader.read_json("overdrive/opportunities.json", {"records": {}})
    signals = reader.read_json("overdrive/signals.json", {})
    claims = reader.read_json("overdrive/claims.json", {})
    rails = reader.read_json("overdrive/payment_rails.json", {})
    truth_screen = reader.read_json("CONTINUITY/MATRIX_TRUTH_SCREEN.json", {})
    opportunity_summary = summarize_opportunities(opps)
    routing_counts = {
        "PRI_signals": len(signals.get("PRI", [])) if isinstance(signals, dict) else 0,
        "iSCOPE_signals": len(signals.get("iSCOPE", [])) if isinstance(signals, dict) else 0,
        "claim_count": len(claims.get("claims", {})) if isinstance(claims, dict) else 0,
        "ready_count": claims.get("ready_count") if isinstance(claims, dict) else None,
    }
    return {
        "state_source": reader.source_label,
        "source_ref": reader.github_ref if reader.github_repo else None,
        "adapter_errors": reader.errors,
        "refreshed_at": utcnow().isoformat(),
        "worker": worker_display_state(worker),
        "opportunities": opportunity_summary,
        "routing": {
            **routing_counts,
            "invariant": "FULL_LEDGER != ROUTING_SUBSET",
            "full_ledger_count": opportunity_summary["total_records"],
        },
        "system_truth": truth_screen,
        "payment_rails": {
            "inventory_completeness": rails.get("inventory_completeness", "UNKNOWN"),
            "rails": rails.get("rails", []),
            "known_unmaterialized_payment_evidence": rails.get("known_unmaterialized_payment_evidence", []),
            "rule": rails.get("inventory_rule", "Unlisted rail is not proof of absence."),
        },
    }
