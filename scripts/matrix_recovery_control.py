#!/usr/bin/env python3
"""Read-only AMX recovery-control preflight.

Projects canonical repository state into an attributable receipt. It is not the
commercial worker, does not call external providers, and never mutates source
ledgers. Plan A is the hourly GitHub Actions trigger. An independent, offset
15-minute watchdog selects repository-only Plan B if no successful Plan A
receipt has been read for 75 minutes. A new successful Plan A receipt returns
the selector to A; fallback does not become sticky. The commercial writer
remains separately paused/manual-only.
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
PLAN_A_SCHEDULE_CRON = "0 * * * *"
PLAN_B_WATCHDOG_CRON = "5,20,35,50 * * * *"
PLAN_A_ANCHOR_PATH = Path("overdrive/recovery-control/plan-a-anchor.json")
PLAN_A_ANCHOR_SCHEMA = "AMX_PLAN_A_LIVENESS_ANCHOR_V1"
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


def read_plan_a_anchor(path: Path) -> dict[str, Any] | None:
    """Read the durable Plan-A liveness anchor; malformed state fails closed."""
    if not path.is_file():
        return None
    try:
        anchor = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ControlError(f"cannot read valid Plan A anchor {path}") from exc
    if not isinstance(anchor, dict) or anchor.get("schema") != PLAN_A_ANCHOR_SCHEMA:
        raise ControlError("Plan A anchor schema missing or invalid")
    activated = anchor.get("activated_at")
    if not isinstance(activated, str) or parse_time(activated) is None:
        raise ControlError("Plan A anchor activation timestamp missing or invalid")
    success = anchor.get("last_successful_plan_a")
    if success is not None:
        if not isinstance(success, dict):
            raise ControlError("Plan A success anchor must be an object or null")
        completed = success.get("completed_at")
        if not isinstance(completed, str) or parse_time(completed) is None:
            raise ControlError("Plan A success anchor timestamp missing or invalid")
        if success.get("run_id") in (None, "") or success.get("commit_sha") in (None, ""):
            raise ControlError("Plan A success anchor run identity missing")
    return anchor


def select_plan(
    *, event: str, fallback_requested: bool, run_worker: str,
    last_plan_a_success_at: str | None = None, activation_started_at: str | None = None,
    schedule_expression: str = "", now: datetime,
) -> tuple[str, str]:
    """Return plan + reason; a scheduled watchdog may automatically select B."""
    def fallback_decision(*, automatic_watchdog: bool) -> tuple[str, str]:
        if run_worker != "paused":
            return "VALIDATION_ONLY", "PLAN_B_REJECTED_WORKER_MUST_REMAIN_PAUSED"

        if last_plan_a_success_at:
            last_success = parse_time(last_plan_a_success_at)
            if last_success is None:
                raise ControlError("Plan A success timestamp cannot be empty")
            age = now.astimezone(timezone.utc) - last_success
            if age < timedelta(0):
                raise ControlError("Plan A success timestamp is in the future; refusing fallback on clock skew")
            if age < timedelta(minutes=PLAN_A_MAX_AGE_MINUTES):
                if automatic_watchdog:
                    return "A", "PLAN_A_RECENT_WATCHDOG_NO_FALLBACK"
                return "VALIDATION_ONLY", "PLAN_B_REJECTED_PLAN_A_RECENT"
            return "B", "PLAN_B_AUTOMATIC_WATCHDOG_PLAN_A_STALE" if automatic_watchdog else "PLAN_B_ALLOWED_PLAN_A_STALE"

        if not activation_started_at:
            raise ControlError("no Plan A success exists and activation timestamp is missing")
        activation = parse_time(activation_started_at)
        if activation is None:
            raise ControlError("Plan A activation timestamp cannot be empty")
        age = now.astimezone(timezone.utc) - activation
        if age < timedelta(0):
            raise ControlError("Plan A activation timestamp is in the future; refusing fallback on clock skew")
        if age < timedelta(minutes=PLAN_A_MAX_AGE_MINUTES):
            if automatic_watchdog:
                return "A", "PLAN_A_STARTUP_WINDOW_WATCHDOG_NO_FALLBACK"
            return "VALIDATION_ONLY", "PLAN_B_REJECTED_STARTUP_WINDOW"
        return "B", "PLAN_B_AUTOMATIC_WATCHDOG_NO_SUCCESSFUL_PLAN_A" if automatic_watchdog else "PLAN_B_ALLOWED_NO_SUCCESSFUL_PLAN_A_RUN"

    if event == "schedule":
        if schedule_expression == PLAN_A_SCHEDULE_CRON and not fallback_requested:
            return "A", "HOURLY_PLAN_A_SCHEDULE_SELECTED"
        # Preserve local/unit preflights that omit GitHub's schedule expression.
        if not schedule_expression and not fallback_requested:
            return "A", "SCHEDULE_EVENT_SELECTED_PLAN_A"
        if schedule_expression == PLAN_B_WATCHDOG_CRON and fallback_requested:
            return fallback_decision(automatic_watchdog=True)
        raise ControlError(f"unrecognized or inconsistent scheduled trigger: {schedule_expression!r}")

    if event != "workflow_dispatch" or not fallback_requested:
        return "VALIDATION_ONLY", "NO_AUTHORIZED_RUNTIME_PLAN_REQUESTED"
    return fallback_decision(automatic_watchdog=False)


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
    last_plan_a_success_at: str | None = None, activation_started_at: str | None = None,
    schedule_expression: str = "",
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

    anchor_path = root / PLAN_A_ANCHOR_PATH
    anchor = read_plan_a_anchor(anchor_path)
    anchor_status = "PRESENT" if anchor else "MISSING"
    if anchor:
        activation_started_at = activation_started_at or str(anchor.get("activated_at"))
        last_success = anchor.get("last_successful_plan_a")
        if last_plan_a_success_at is None and isinstance(last_success, dict):
            last_plan_a_success_at = str(last_success.get("completed_at"))
    elif event == "schedule" and schedule_expression == PLAN_B_WATCHDOG_CRON:
        # First watchdog after installation starts the recovery grace window; it
        # must not invoke fallback immediately merely because no anchor exists.
        activation_started_at = activation_started_at or now_utc.isoformat().replace("+00:00", "Z")
        anchor_status = "INITIALIZE_AFTER_SUCCESSFUL_WATCHDOG"

    selected_plan, plan_reason = select_plan(
        event=event, fallback_requested=fallback_requested, run_worker=run_worker,
        last_plan_a_success_at=last_plan_a_success_at, activation_started_at=activation_started_at,
        schedule_expression=schedule_expression, now=now_utc,
    )
    source_hashes = {
        str(path.relative_to(root)): sha256_text(path.read_text(encoding="utf-8"))
        for path in required
    }
    if anchor_path.is_file():
        source_hashes[str(PLAN_A_ANCHOR_PATH)] = sha256_text(anchor_path.read_text(encoding="utf-8"))
    return {
        "schema": SCHEMA,
        "receipt_type": "REPOSITORY_RECOVERY_CONTROL_PREFLIGHT",
        "generated_at": now_utc.isoformat().replace("+00:00", "Z"),
        "run": {
            "workflow": "AMX OVERDRIVE Worker", "event": event,
            "run_id": run_id, "run_attempt": run_attempt, "run_number": run_number,
            "ref": ref, "commit_sha": commit_sha, "actor": actor,
            "schedule_expression": schedule_expression,
        },
        "control": {
            "selected_plan": selected_plan, "selection_reason": plan_reason,
            "trigger_role": (
                "PLAN_A_HOURLY" if event == "schedule" and schedule_expression == PLAN_A_SCHEDULE_CRON
                else "PLAN_B_AUTOMATIC_WATCHDOG" if event == "schedule" and schedule_expression == PLAN_B_WATCHDOG_CRON
                else "PLAN_B_MANUAL_GUARDED" if event == "workflow_dispatch" and fallback_requested
                else "VALIDATION_ONLY_OR_MANUAL"
            ),
            "liveness_anchor_path": str(PLAN_A_ANCHOR_PATH), "liveness_anchor_status": anchor_status,
            "plan_a_last_success_at": last_plan_a_success_at,
            "plan_a_activation_started_at": activation_started_at,
            "plan_a_cadence_minutes": 60, "plan_b_watchdog_cadence_minutes": 15,
            "plan_b_max_plan_a_age_minutes": PLAN_A_MAX_AGE_MINUTES,
            "plan_b_automatic_watchdog_enabled": True,
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
            "freshness": (
                "UNKNOWN" if tick_age is None
                else "CLOCK_SKEW" if tick_age < 0
                else "FRESH" if tick_age <= PLAN_A_MAX_AGE_MINUTES
                else "STALE"
            ),
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
    parser.add_argument("--schedule-expression", default=os.environ.get("GITHUB_EVENT_SCHEDULE", ""))
    parser.add_argument("--last-plan-a-success-at", default=os.environ.get("PLAN_A_LAST_SUCCESS_AT") or None)
    parser.add_argument("--activation-started-at", default=os.environ.get("PLAN_A_ACTIVATION_STARTED_AT") or None)
    args = parser.parse_args(argv)
    now = parse_time(args.now) if args.now else datetime.now(timezone.utc)
    assert now is not None
    out = Path(args.out)
    metadata = {key: value for key, value in {
        "event": args.event, "run_id": args.run_id, "run_attempt": args.run_attempt,
        "run_number": args.run_number, "ref": args.ref, "commit_sha": args.commit_sha, "actor": args.actor,
        "schedule_expression": args.schedule_expression,
    }.items()}
    try:
        receipt = build_manifest(
            repo_root=Path(args.repo_root), event=args.event, now=now, run_id=args.run_id,
            run_attempt=args.run_attempt, run_number=args.run_number, ref=args.ref,
            commit_sha=args.commit_sha, actor=args.actor, fallback_requested=args.fallback_requested,
            run_worker=args.run_worker, last_plan_a_success_at=args.last_plan_a_success_at,
            activation_started_at=args.activation_started_at, schedule_expression=args.schedule_expression,
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
