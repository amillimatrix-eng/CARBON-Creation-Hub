#!/usr/bin/env python3
"""Read-only AMX recovery-control preflight.

Projects canonical repository state into one receipt. It is not the commercial
worker, does not call external providers, and never mutates source ledgers.
Plan A is the scheduled GitHub Actions trigger. Plan B is a manual, repo-only
fallback allowed only when the latest successful Plan A run is at least 75
minutes old and the commercial worker remains paused. A future scheduled
trigger always selects Plan A; fallback mode is never sticky.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

REGISTRY_PATH = Path("AMX/ROOT/BLUE_STATE/MANDATE_REGISTRY_V1.json")
REQUIRED_PATHS = (
    Path("AMX/ROOT/INTAKE/INTAKE_INDEX.md"),
    Path("CONTINUITY.md"),
    Path("ACCESS_CONTINUITY.md"),
    Path("overdrive/state.json"),
    Path("overdrive/opportunities.json"),
    Path("overdrive/claims.json"),
    Path("overdrive/payment_rails.json"),
)
PLAN_A_MAX_AGE_MINUTES = 75
SCHEMA = "AMX_MATRIX_RECOVERY_CONTROL_RECEIPT_V1"


class ControlError(RuntimeError):
    """Fail-closed source or control error."""


def parse_time(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ControlError(f"invalid timestamp: {value!r}") from exc
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def registry_root(registry: dict[str, Any]) -> str:
    entries = registry.get("entries")
    if not isinstance(entries, list) or not entries:
        raise ControlError("mandate registry entries missing or invalid")
    lines: list[str] = []
    seen: set[str] = set()
    for entry in entries:
        if not isinstance(entry, dict):
            raise ControlError("mandate registry entry is not an object")
        role, digest = entry.get("role_key"), entry.get("sha256")
        if not isinstance(role, str) or not role or not isinstance(digest, str) or not digest:
            raise ControlError("mandate registry entry is missing role_key or sha256")
        if role in seen:
            raise ControlError(f"duplicate mandate role key: {role}")
        seen.add(role)
        lines.append(f"{role}={digest}")
    return sha256_text("".join(line + "\n" for line in sorted(lines)))


def select_plan(
    *, event: str, fallback_requested: bool, run_worker: str,
    last_plan_a_success_at: str | None, now: datetime,
) -> tuple[str, str]:
    """Return plan + reason; never starts the commercial worker."""
    if event == "schedule":
        return "A", "SCHEDULE_EVENT_SELECTED_PLAN_A"
    if event != "workflow_dispatch" or not fallback_requested:
        return "VALIDATION_ONLY", "NO_AUTHORIZED_RUNTIME_PLAN_REQUESTED"
    if run_worker != "paused":
        return "VALIDATION_ONLY", "PLAN_B_REJECTED_WORKER_MUST_REMAIN_PAUSED"

    if last_plan_a_success_at:
        last_success = parse_time(last_plan_a_success_at)
        assert last_success is not None
        age = now.astimezone(timezone.utc) - last_success
        if age < timedelta(minutes=PLAN_A_MAX_AGE_MINUTES):
            return "VALIDATION_ONLY", "PLAN_B_REJECTED_PLAN_A_RECENT"
        return "B", "PLAN_B_ALLOWED_PLAN_A_STALE"
    # None is permitted only after the caller successfully queried the Actions
    # API and established that there is no successful schedule run. API errors
    # must fail the workflow step rather than being translated to None.
    return "B", "PLAN_B_ALLOWED_NO_SUCCESSFUL_PLAN_A_RUN"


def read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ControlError(f"cannot read valid JSON source {path}") from exc
    if not isinstance(value, dict):
        raise ControlError(f"JSON source must be an object: {path}")
    return value


def build_manifest(
    *, repo_root: Path, event: str, now: datetime,
    run_id: str = "", run_attempt: str = "", run_number: str = "",
    ref: str = "", commit_sha: str = "", actor: str = "",
    fallback_requested: bool = False, run_worker: str = "paused",
    last_plan_a_success_at: str | None = None,
) -> dict[str, Any]:
    root = repo_root.resolve()
    required = [root / path for path in REQUIRED_PATHS] + [root / REGISTRY_PATH]
    missing = [str(path.relative_to(root)) for path in required if not path.is_file()]
    if missing:
        raise ControlError("required canonical source(s) missing: " + ", ".join(missing))

    registry_path = root / REGISTRY_PATH
    registry = read_json(registry_path)
    computed_root = registry_root(registry)
    declared_root = registry.get("registry_root_sha256")
    if computed_root != declared_root:
        raise ControlError(f"mandate registry root mismatch: computed={computed_root}, declared={declared_root}")
    version = str(registry.get("version") or "")
    if not version:
        raise ControlError("mandate registry version missing")

    opportunities = read_json(root / "overdrive/opportunities.json")
    records = opportunities.get("records")
    if not isinstance(records, dict):
        raise ControlError("opportunities ledger records object missing")
    actual_record_count = len(records)
    declared_record_count = opportunities.get("record_count")
    if declared_record_count != actual_record_count:
        raise ControlError(f"opportunities ledger count mismatch: declared={declared_record_count}, actual={actual_record_count}")

    claims_doc = read_json(root / "overdrive/claims.json")
    claims = claims_doc.get("claims")
    if not isinstance(claims, dict):
        raise ControlError("claims object missing")
    ready = [(key, value) for key, value in claims.items()
             if isinstance(value, dict) and str(value.get("status", "")).upper() == "READY"]
    externally_ready = [(key, value) for key, value in ready if value.get("external_action_ready") is True]

    state = read_json(root / "overdrive/state.json")
    last_tick = state.get("last_tick")
    last_tick_at = parse_time(str(last_tick)) if last_tick else None
    now_utc = now.astimezone(timezone.utc)
    tick_age = round((now_utc - last_tick_at).total_seconds() / 60, 2) if last_tick_at else None

    selected_plan, plan_reason = select_plan(
        event=event, fallback_requested=fallback_requested, run_worker=run_worker,
        last_plan_a_success_at=last_plan_a_success_at, now=now_utc,
    )
    source_hashes = {
        str(path.relative_to(root)): sha256_text(path.read_text(encoding="utf-8"))
        for path in required
    }
    return {
        "schema": SCHEMA,
        "receipt_type": "REPOSITORY_RECOVERY_CONTROL_PREFLIGHT",
        "generated_at": now_utc.isoformat().replace("+00:00", "Z"),
        "run": {
            "workflow": "AMX OVERDRIVE Worker", "event": event,
            "run_id": run_id, "run_attempt": run_attempt, "run_number": run_number,
            "ref": ref, "commit_sha": commit_sha, "actor": actor,
        },
        "control": {
            "selected_plan": selected_plan, "selection_reason": plan_reason,
            "plan_a_cadence_minutes": 60, "plan_b_max_plan_a_age_minutes": PLAN_A_MAX_AGE_MINUTES,
            "plan_b_is_sticky": False, "next_successful_schedule_selects": "A",
            "commercial_worker_run": False, "external_reads_attempted": False,
            "external_writes_attempted": False, "scope": "REPOSITORY_READ_ONLY_CONTINUITY_CONTROL",
        },
        "canonical_registry": {
            "path": str(REGISTRY_PATH), "version": version,
            "effective_date": registry.get("effective_date"),
            "entry_count": len(registry["entries"]), "declared_root_sha256": declared_root,
            "computed_root_sha256": computed_root, "hash_status": "PASS",
        },
        "root_intake": {
            "issue": 31, "index_path": "AMX/ROOT/INTAKE/INTAKE_INDEX.md",
            "disposition": "OPEN_NOT_CLEARED",
        },
        "overdrive_projection": {
            "state_path": "overdrive/state.json", "adapter_status": state.get("adapter_status", "UNKNOWN"),
            "last_tick": last_tick, "last_tick_age_minutes": tick_age,
            "freshness": "UNKNOWN" if tick_age is None else "FRESH" if tick_age <= PLAN_A_MAX_AGE_MINUTES else "STALE",
            "opportunities_path": "overdrive/opportunities.json",
            "record_count_declared": declared_record_count, "record_count_actual": actual_record_count,
            "record_count_status": "PASS", "claims_path": "overdrive/claims.json",
            "claims_total": len(claims), "ready_claims": len(ready),
            "externally_ready_claims": len(externally_ready),
            "work_conservation": "OPEN_WORK_PRESERVED; NO_AUTO_CLOSURE" if ready else "NO_READY_CLAIM_OBSERVED; NOT_ROOT_QUEUE_CLEARANCE",
        },
        "source_hashes_sha256": source_hashes,
        "acceptance_boundary": {
            "status": "PASS_REPOSITORY_PREFLIGHT_ONLY",
            "not_proven": [
                "Root Intake item-level clearance",
                "external inbox/CRM/Render/bank/Stripe/Metricool access",
                "commercial worker execution",
                "buyer response, acceptance, invoice, award, or settlement",
                "hourly Plan A liveness until a real successful scheduled run is read back",
                "Plan B usefulness until an authorized fallback trigger and receipt are observed",
            ],
            "next_action": "Keep eligible work open. Reconcile the existing Root queue and executor prompts; only resume consolidated outcome execution after governing control and prompt readback passes.",
        },
    }


def write_failure_receipt(out: Path, exc: Exception, metadata: dict[str, str]) -> None:
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({
        "schema": SCHEMA, "receipt_type": "REPOSITORY_RECOVERY_CONTROL_PREFLIGHT",
        "status": "FAIL_CLOSED", "generated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "error": str(exc), "run": metadata, "commercial_worker_run": False,
        "external_reads_attempted": False, "external_writes_attempted": False,
    }, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--out", default="artifacts/matrix-recovery-control/receipt.json")
    parser.add_argument("--event", default=os.environ.get("GITHUB_EVENT_NAME", "local"))
    parser.add_argument("--run-id", default=os.environ.get("GITHUB_RUN_ID", ""))
    parser.add_argument("--run-attempt", default=os.environ.get("GITHUB_RUN_ATTEMPT", ""))
    parser.add_argument("--run-number", default=os.environ.get("GITHUB_RUN_NUMBER", ""))
    parser.add_argument("--ref", default=os.environ.get("GITHUB_REF", ""))
    parser.add_argument("--commit-sha", default=os.environ.get("GITHUB_SHA", ""))
    parser.add_argument("--actor", default=os.environ.get("GITHUB_ACTOR", ""))
    parser.add_argument("--now", default=None)
    parser.add_argument("--fallback-requested", action="store_true")
    parser.add_argument("--run-worker", default=os.environ.get("AMX_RUN_WORKER", "paused"))
    parser.add_argument("--last-plan-a-success-at", default=os.environ.get("PLAN_A_LAST_SUCCESS_AT") or None)
    args = parser.parse_args(argv)
    now = parse_time(args.now) if args.now else datetime.now(timezone.utc)
    assert now is not None
    out = Path(args.out)
    metadata = {key: value for key, value in {
        "event": args.event, "run_id": args.run_id, "run_attempt": args.run_attempt,
        "run_number": args.run_number, "ref": args.ref, "commit_sha": args.commit_sha, "actor": args.actor,
    }.items()}
    try:
        receipt = build_manifest(
            repo_root=Path(args.repo_root), event=args.event, now=now, run_id=args.run_id,
            run_attempt=args.run_attempt, run_number=args.run_number, ref=args.ref,
            commit_sha=args.commit_sha, actor=args.actor, fallback_requested=args.fallback_requested,
            run_worker=args.run_worker, last_plan_a_success_at=args.last_plan_a_success_at,
        )
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(json.dumps({
            "status": receipt["acceptance_boundary"]["status"],
            "selected_plan": receipt["control"]["selected_plan"],
            "registry_root_sha256": receipt["canonical_registry"]["computed_root_sha256"],
            "ledger_records": receipt["overdrive_projection"]["record_count_actual"],
            "ready_claims": receipt["overdrive_projection"]["ready_claims"],
            "receipt_path": str(out),
        }, sort_keys=True))
        summary_path = os.environ.get("GITHUB_STEP_SUMMARY")
        if summary_path:
            with open(summary_path, "a", encoding="utf-8") as summary:
                summary.write("## AMX Recovery Control Preflight\n\n")
                summary.write(f"- Plan: **{receipt['control']['selected_plan']}** — {receipt['control']['selection_reason']}\n")
                summary.write(f"- Registry: **PASS** v{receipt['canonical_registry']['version']} / {receipt['canonical_registry']['computed_root_sha256']}\n")
                summary.write(f"- Ledger: {receipt['overdrive_projection']['record_count_actual']} source records / {receipt['overdrive_projection']['ready_claims']} READY claims observed\n")
                summary.write("- External actions: **not attempted**\n- Result: **repository preflight only**; Matrix-wide execution/clearance not claimed\n")
        return 0
    except Exception as exc:
        write_failure_receipt(out, exc, metadata)
        print(f"Recovery control failed closed: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
