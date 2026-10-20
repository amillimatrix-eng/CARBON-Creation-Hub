#!/usr/bin/env python3
"""Deterministic Plan A / Plan B selector for the existing AMX OVERDRIVE runtime.

Plan A is an hourly work-conserving execution window. Plan B is the existing
five-minute watchdog's bounded recovery tick when the last accepted Plan A
window is stale. The infrastructure pause wins until every persisted resume
gate is accepted. This script creates no scheduler, queue, identity, or worker.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
CONTROL_PATH = ROOT / "runtime_cadence.json"
PLAN_A_CRON = "7 * * * *"
PLAN_B_CRON = "*/5 * * * *"
DEFAULT_STALE_MINUTES = 70


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def iso(dt: datetime | None = None) -> str:
    return (dt or utcnow()).astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def parse_time(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (TypeError, ValueError):
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def load_control(path: Path = CONTROL_PATH) -> dict[str, Any]:
    control = json.loads(path.read_text(encoding="utf-8"))
    if control.get("schema") != "AMX_RUNTIME_CADENCE_CONTROL_V1":
        raise ValueError("unsupported cadence control schema")
    if control.get("rules", {}).get("no_plan_c") is not True:
        raise ValueError("invalid control: an undefined Plan C is prohibited")
    if control.get("phase") not in {"PAUSED_INFRASTRUCTURE", "ACTIVE"}:
        raise ValueError("invalid phase")
    if control.get("current_mode") not in {"PLAN_A", "PLAN_B"}:
        raise ValueError("invalid current_mode")
    return control


def write_control(control: dict[str, Any], path: Path = CONTROL_PATH) -> None:
    path.write_text(json.dumps(control, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def all_resume_gates_pass(control: dict[str, Any]) -> bool:
    gates = control.get("resume_gates", {})
    return bool(gates) and all(isinstance(g, dict) and g.get("pass") is True for g in gates.values())


def refresh_phase(control: dict[str, Any], now: datetime | None = None) -> bool:
    """Auto-release the infrastructure pause only after all persisted acceptance gates pass."""
    if control["phase"] != "PAUSED_INFRASTRUCTURE" or not all_resume_gates_pass(control):
        return False
    stamp = iso(now)
    control["phase"] = "ACTIVE"
    control.setdefault("owner_pause", {})["active"] = False
    control["owner_pause"]["released_at"] = stamp
    control.setdefault("transition_log", []).append({
        "at": stamp,
        "from": "PAUSED_INFRASTRUCTURE",
        "to": "ACTIVE",
        "reason": "ALL_PERSISTED_RESUME_GATES_PASSED",
    })
    control["transition_log"] = control["transition_log"][-20:]
    return True


def select_action(
    control: dict[str, Any],
    event_name: str,
    schedule: str = "",
    manual_input: str = "paused",
    now: datetime | None = None,
) -> dict[str, str]:
    """Return PAUSE / PLAN_A / PLAN_B / MANUAL_TICK / SKIP without inventing a third plan."""
    now = now or utcnow()
    if refresh_phase(control, now):
        return {"action": "pause", "reason": "RESUME_GATES_PASSED; persisted activation first, execute on next trigger"}
    if control["phase"] != "ACTIVE" or control.get("owner_pause", {}).get("active", False):
        return {"action": "pause", "reason": "OWNER_INFRASTRUCTURE_PAUSE_OR_ACCEPTANCE_GATE_OPEN"}

    if event_name == "schedule" and schedule == PLAN_A_CRON:
        return {"action": "plan_a", "reason": "INTENDED_HOURLY_WINDOW"}
    if event_name == "schedule" and schedule == PLAN_B_CRON:
        last_a = parse_time(control.get("last_plan_a_success_at"))
        stale_minutes = int(control.get("plan_b", {}).get("stale_after_minutes", DEFAULT_STALE_MINUTES))
        if last_a is None:
            return {"action": "plan_b", "reason": "NO_ACCEPTED_PLAN_A_RECEIPT"}
        age_minutes = (now - last_a).total_seconds() / 60
        if age_minutes > stale_minutes:
            return {"action": "plan_b", "reason": f"PLAN_A_STALE_{int(age_minutes)}M"}
        return {"action": "skip", "reason": f"PLAN_A_FRESH_{int(age_minutes)}M"}
    if event_name == "workflow_dispatch" and manual_input == "run":
        return {"action": "manual_tick", "reason": "EXPLICIT_MANUAL_RUN_REQUEST"}
    return {"action": "skip", "reason": "NO_MATCHING_DEFINED_PLAN"}


def record_success(control: dict[str, Any], mode: str, now: datetime | None = None) -> bool:
    """Persist plan transitions; every run remains separately visible in GitHub Actions logs."""
    stamp = iso(now)
    old_mode = control["current_mode"]
    changed = False
    if mode == "plan_a":
        control["last_plan_a_success_at"] = stamp
        if old_mode != "PLAN_A":
            control.setdefault("transition_log", []).append({
                "at": stamp, "from": old_mode, "to": "PLAN_A",
                "reason": "PLAN_A_WINDOW_COMPLETED_AND_READBACK_PASSED",
            })
            control["current_mode"] = "PLAN_A"
        changed = True
    elif mode == "plan_b":
        if old_mode != "PLAN_B":
            control["current_mode"] = "PLAN_B"
            control["last_plan_b_entered_at"] = stamp
            control.setdefault("transition_log", []).append({
                "at": stamp, "from": old_mode, "to": "PLAN_B",
                "reason": "PLAN_A_MISSED_OR_STALE; BOUNDED_EXISTING-RUNNER_RECOVERY",
            })
            changed = True
    elif mode == "manual_tick":
        control["last_manual_success_at"] = stamp
        changed = True
    else:
        raise ValueError(f"unsupported success mode: {mode}")
    control["transition_log"] = control.get("transition_log", [])[-20:]
    return changed


def github_output(values: dict[str, str]) -> None:
    target = os.environ.get("GITHUB_OUTPUT")
    if target:
        with open(target, "a", encoding="utf-8") as handle:
            for key, value in values.items():
                handle.write(f"{key}={value}\n")


def main() -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    sel = sub.add_parser("select")
    sel.add_argument("--event-name", required=True)
    sel.add_argument("--schedule", default="")
    sel.add_argument("--manual-input", default="paused")
    sel.add_argument("--now", default=None, help="UTC ISO timestamp; used by deterministic tests")
    gate = sub.add_parser("mark-gate")
    gate.add_argument("--name", required=True)
    gate.add_argument("--evidence", required=True)
    success = sub.add_parser("record-success")
    success.add_argument("--mode", choices=["plan_a", "plan_b", "manual_tick"], required=True)
    success.add_argument("--now", default=None)
    args = parser.parse_args()

    control = load_control()
    changed = False
    if args.command == "select":
        when = parse_time(args.now) if args.now else utcnow()
        phase_before = control["phase"]
        pause_before = control.get("owner_pause", {}).get("active", False)
        result = select_action(control, args.event_name, args.schedule, args.manual_input, when)
        # Persist only a real transition; do not rewrite the control file on every trigger.
        changed = phase_before != control["phase"] or pause_before != control.get("owner_pause", {}).get("active", False)
        if changed:
            write_control(control)
        values = {
            "action": result["action"],
            "reason": result["reason"].replace("\n", " "),
            "phase": control["phase"],
        }
        github_output(values)
        print(json.dumps({**result, "phase": control["phase"], "control_changed": changed}, sort_keys=True))
    elif args.command == "mark-gate":
        gates = control.setdefault("resume_gates", {})
        gate = gates.get(args.name)
        if gate is None:
            raise SystemExit(f"unknown resume gate: {args.name}")
        if gate.get("pass") is not True or gate.get("evidence") != args.evidence:
            gate["pass"] = True
            gate["evidence"] = args.evidence
            gate["accepted_at"] = iso()
            changed = True
        if changed:
            write_control(control)
        print(json.dumps({"gate": args.name, "pass": True, "changed": changed}, sort_keys=True))
    elif args.command == "record-success":
        when = parse_time(args.now) if args.now else utcnow()
        changed = record_success(control, args.mode, when)
        if changed:
            write_control(control)
        print(json.dumps({"mode": args.mode, "changed": changed, "current_mode": control["current_mode"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
