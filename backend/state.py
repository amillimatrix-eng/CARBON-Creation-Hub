from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def read_json(path: Path, default: Any = None) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return default


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
    worker = read_json(repo_root / "overdrive/worker_contract.json", {})
    opps = read_json(repo_root / "overdrive/opportunities.json", {"records": {}})
    signals = read_json(repo_root / "overdrive/signals.json", {})
    claims = read_json(repo_root / "overdrive/claims.json", {})
    rails = read_json(repo_root / "overdrive/payment_rails.json", {})
    opportunity_summary = summarize_opportunities(opps)
    routing_counts = {
        "PRI_signals": len(signals.get("PRI", [])) if isinstance(signals, dict) else 0,
        "iSCOPE_signals": len(signals.get("iSCOPE", [])) if isinstance(signals, dict) else 0,
        "claim_count": len(claims.get("claims", {})) if isinstance(claims, dict) else 0,
        "ready_count": claims.get("ready_count") if isinstance(claims, dict) else None,
    }
    return {
        "state_source": "LOCAL_SNAPSHOT",
        "refreshed_at": utcnow().isoformat(),
        "worker": worker_display_state(worker),
        "opportunities": opportunity_summary,
        "routing": {
            **routing_counts,
            "invariant": "FULL_LEDGER != ROUTING_SUBSET",
            "full_ledger_count": opportunity_summary["total_records"],
        },
        "payment_rails": {
            "inventory_completeness": rails.get("inventory_completeness", "UNKNOWN"),
            "rails": rails.get("rails", []),
            "known_unmaterialized_payment_evidence": rails.get("known_unmaterialized_payment_evidence", []),
            "rule": rails.get("inventory_rule", "Unlisted rail is not proof of absence."),
        },
    }
