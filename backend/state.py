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

T10_SCHEMA = "AMX_BLUE_STATE_T10_OUTCOME_TRUTH_V1_0"


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def t10_packet(job: str, actual: str, evidence: str, change: str, gap: str, passed: str) -> dict[str, str]:
    state = str(passed).strip().upper()
    if state not in {"PASS", "HOLD", "FAIL", "UNKNOWN"}:
        state = "UNKNOWN"
    return {
        "T10_JOB": job,
        "T10_ACTUAL": actual,
        "T10_EVIDENCE": evidence,
        "T10_CHANGE": change,
        "T10_REMAINING_GAP": gap,
        "T10_PASS": state,
    }


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
        headers = {"User-Agent": "amx-evidence-house/2.0"}

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
    gap = (
        "No execution-acceptance gap is asserted by this projection; narrower durable receipt gaps may still exist."
        if execution_proven
        else f"Execution acceptance remains unresolved: {acceptance}."
    )
    return {
        "configured_status": status,
        "runtime_enabled": enabled,
        "acceptance_state": acceptance,
        "execution_truth": truth,
        "display_state": display,
        "t10": t10_packet(
            "Run the commercial reasoning executor within mandate and prove consequential work with attributable durable evidence.",
            truth,
            "overdrive/worker_contract.json::execution/current_evidence/acceptance_v2",
            "This operator projection is read-only and does not promote scheduler/configuration activity into an execution outcome.",
            gap,
            "PASS" if execution_proven else "HOLD",
        ),
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
    total = len(records)
    return {
        "total_records": total,
        "state_counts": counts,
        "due_or_actionable": due,
        "paid_record_count": len(paid),
        "paid_record_keys": paid,
        "realized_revenue_evidence": {
            "present": bool(paid),
            "rule": "PAID requires payment evidence; no PAID record means realized revenue remains unproven.",
        },
        "t10": t10_packet(
            "Represent the full commercial ledger and current actionable outcomes without silently collapsing it into a routing subset.",
            f"{total} full-ledger record(s); {len(due)} due/actionable projection(s); {len(paid)} PAID state record(s).",
            "overdrive/opportunities.json",
            "The aggregator exposes current ledger state only; counts do not prove conversion, acceptance, or payment.",
            "Per-record material outcome and payment evidence remain authoritative; projection counts cannot close those gaps.",
            "PASS" if isinstance(records, dict) else "HOLD",
        ),
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

    source_label = reader.source_label
    adapter_gap = (
        "No adapter read failure was recorded for this projection."
        if source_label == "GITHUB_LIVE"
        else f"Live authoritative read is not fully proven for this projection: {source_label}; adapter errors={reader.errors or 'none recorded'}."
    )

    inventory = str(rails.get("inventory_completeness", "UNKNOWN"))
    rails_list = rails.get("rails", []) if isinstance(rails, dict) else []
    rails_pass = "PASS" if inventory.upper().startswith("COMPLETE") else "HOLD"

    native_truth_t10 = truth_screen.get("t10") or truth_screen.get("T10") if isinstance(truth_screen, dict) else None
    if native_truth_t10:
        truth_t10 = native_truth_t10
    else:
        truth_t10 = t10_packet(
            "Expose Matrix truth with native outcome fields rather than treating technical status labels as closure.",
            f"{truth_screen.get('schema', 'UNKNOWN')} loaded without native T10 outcome fields." if isinstance(truth_screen, dict) else "Truth screen unavailable.",
            "CONTINUITY/MATRIX_TRUTH_SCREEN.json",
            "The Evidence House preserves the legacy snapshot but marks the missing T10 translation instead of silently upgrading it.",
            "The truth-screen producer must emit native T10_JOB/T10_ACTUAL/T10_EVIDENCE/T10_CHANGE/T10_REMAINING_GAP/T10_PASS fields on its next consequential rewrite.",
            "HOLD",
        )

    return {
        "state_source": source_label,
        "source_ref": reader.github_ref if reader.github_repo else None,
        "adapter_errors": reader.errors,
        "refreshed_at": utcnow().isoformat(),
        "t10": t10_packet(
            "Read consequential Matrix state from durable sources without confusing transport, scheduler activity, or configuration with outcome.",
            f"State source={source_label}; full ledger={opportunity_summary['total_records']}; routing claims={routing_counts['claim_count']}.",
            "overdrive/worker_contract.json + overdrive/opportunities.json + overdrive/signals.json + overdrive/claims.json + overdrive/payment_rails.json + CONTINUITY/MATRIX_TRUTH_SCREEN.json",
            "A read-only bounded projection was produced; no worker outcome was invented by the backend.",
            adapter_gap,
            "PASS" if source_label == "GITHUB_LIVE" else "HOLD",
        ),
        "worker": worker_display_state(worker),
        "opportunities": opportunity_summary,
        "routing": {
            **routing_counts,
            "invariant": "FULL_LEDGER != ROUTING_SUBSET",
            "full_ledger_count": opportunity_summary["total_records"],
            "t10": t10_packet(
                "Expose routing signals/claims as a subset while preserving the full opportunity ledger as the authoritative inventory.",
                f"Full ledger={opportunity_summary['total_records']}; claims={routing_counts['claim_count']}; PRI signals={routing_counts['PRI_signals']}; iSCOPE signals={routing_counts['iSCOPE_signals']}.",
                "overdrive/opportunities.json + overdrive/signals.json + overdrive/claims.json",
                "Routing counts are reported beside, not instead of, full-ledger count.",
                "Routing or claim presence does not prove ownership, execution, resolution, conversion, or payment.",
                "PASS",
            ),
        },
        "system_truth": truth_screen,
        "system_truth_t10": truth_t10,
        "payment_rails": {
            "inventory_completeness": inventory,
            "rails": rails_list,
            "known_unmaterialized_payment_evidence": rails.get("known_unmaterialized_payment_evidence", []) if isinstance(rails, dict) else [],
            "rule": rails.get("inventory_rule", "Unlisted rail is not proof of absence.") if isinstance(rails, dict) else "Unlisted rail is not proof of absence.",
            "t10": t10_packet(
                "Represent receiving-rail inventory without turning PARTIAL inventory into false payment incompatibility.",
                f"Inventory completeness={inventory}; recovered rail records={len(rails_list)}.",
                "overdrive/payment_rails.json",
                "Recovered rails are exposed as inventory evidence only; unlisted rails are not treated as absent.",
                "Inventory remains incomplete or uncertain until the durable payment-rail source explicitly proves COMPLETE." if rails_pass != "PASS" else "No inventory-completeness gap is asserted by the current payment-rail source.",
                rails_pass,
            ),
        },
    }
