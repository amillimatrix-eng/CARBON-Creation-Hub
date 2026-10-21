from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import pytest

from scripts.matrix_recovery_control import (
    ControlError,
    build_manifest,
    PLAN_A_SCHEDULE_CRON,
    PLAN_B_WATCHDOG_CRON,
    PLAN_A_ANCHOR_SCHEMA,
    read_plan_a_anchor,
    registry_root,
    select_plan,
)


NOW = datetime(2026, 10, 20, 15, 0, tzinfo=timezone.utc)
ROOT_HASH = "96c0beb3328ebefc16286d93a7baadc0ff4be0a17c1e6a8718b89de94f58df1a"


def write_json(path: Path, obj: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2) + "\n", encoding="utf-8")


def make_repo(tmp_path: Path) -> Path:
    registry = {
        "version": "test-1",
        "effective_date": "2026-10-20",
        "entries": [
            {"role_key": "BETA", "sha256": "bbb"},
            {"role_key": "ALPHA", "sha256": "aaa"},
        ],
    }
    registry["registry_root_sha256"] = registry_root(registry)
    write_json(tmp_path / "AMX/ROOT/BLUE_STATE/MANDATE_REGISTRY_V1.json", registry)

    for relative in (
        "AMX/ROOT/INTAKE/INTAKE_INDEX.md",
        "CONTINUITY.md",
        "ACCESS_CONTINUITY.md",
        "AMX/ROOT/INTAKE/CHATGPT_AUTOMATION_PLAN_CAPACITY_LIVENESS_FAULT_20261019.md",
    ):
        path = tmp_path / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("test source; existing owner and next action remain canonical.\n", encoding="utf-8")

    write_json(tmp_path / "overdrive/state.json", {
        "adapter_status": "OPERATIONAL",
        "last_tick": "2026-10-20T14:30:00Z",
    })
    write_json(tmp_path / "overdrive/opportunities.json", {
        "record_count": 2,
        "records": {"OPP-1": {"state": "OFFERED"}, "OPP-2": {"state": "WAITING"}},
    })
    write_json(tmp_path / "overdrive/claims.json", {
        "claims": {
            "PRI|OPP-1": {"status": "READY", "external_action_ready": False},
            "PRI|OPP-2": {"status": "WAITING", "external_action_ready": False},
            "PRI|OPP-3": {"status": "READY", "external_action_ready": True},
        }
    })
    write_json(tmp_path / "overdrive/payment_rails.json", {"schema": "test", "rails": []})
    return tmp_path


def test_registry_root_is_order_independent_and_matches_sorted_lines() -> None:
    first = {"entries": [
        {"role_key": "BETA", "sha256": "bbb"},
        {"role_key": "ALPHA", "sha256": "aaa"},
    ]}
    second = {"entries": list(reversed(first["entries"]))}
    assert registry_root(first) == registry_root(second)


def test_registry_root_rejects_duplicate_role_keys() -> None:
    with pytest.raises(ControlError, match="duplicate mandate role key"):
        registry_root({"entries": [
            {"role_key": "ALPHA", "sha256": "aaa"},
            {"role_key": "ALPHA", "sha256": "bbb"},
        ]})


def test_plan_a_selected_only_for_actual_schedule_event() -> None:
    hourly = select_plan(
        event="schedule", fallback_requested=False, run_worker="paused",
        last_plan_a_success_at=None, schedule_expression=PLAN_A_SCHEDULE_CRON, now=NOW,
    )
    legacy_local = select_plan(
        event="schedule", fallback_requested=False, run_worker="paused",
        last_plan_a_success_at=None, now=NOW,
    )
    push = select_plan(
        event="push", fallback_requested=True, run_worker="paused",
        last_plan_a_success_at=None, now=NOW,
    )
    assert hourly == ("A", "HOURLY_PLAN_A_SCHEDULE_SELECTED")
    assert legacy_local[0] == "A"
    assert push[0] == "VALIDATION_ONLY"
    with pytest.raises(ControlError, match="unrecognized or inconsistent scheduled trigger"):
        select_plan(
            event="schedule", fallback_requested=False, run_worker="paused",
            schedule_expression="*/5 * * * *", now=NOW,
        )


def test_plan_b_requires_explicit_request_and_paused_worker() -> None:
    no_request = select_plan(
        event="workflow_dispatch", fallback_requested=False, run_worker="paused",
        last_plan_a_success_at=None, now=NOW,
    )
    worker_not_paused = select_plan(
        event="workflow_dispatch", fallback_requested=True, run_worker="run",
        last_plan_a_success_at=None, now=NOW,
    )
    assert no_request[0] == "VALIDATION_ONLY"
    assert worker_not_paused == ("VALIDATION_ONLY", "PLAN_B_REJECTED_WORKER_MUST_REMAIN_PAUSED")


def test_plan_b_is_denied_when_plan_a_is_recent_and_allowed_when_stale() -> None:
    recent = select_plan(
        event="workflow_dispatch", fallback_requested=True, run_worker="paused",
        last_plan_a_success_at="2026-10-20T14:20:00Z",
        activation_started_at="2026-10-20T13:00:00Z", now=NOW,
    )
    stale = select_plan(
        event="workflow_dispatch", fallback_requested=True, run_worker="paused",
        last_plan_a_success_at="2026-10-20T13:40:00Z",
        activation_started_at="2026-10-20T13:00:00Z", now=NOW,
    )
    never_ran = select_plan(
        event="workflow_dispatch", fallback_requested=True, run_worker="paused",
        last_plan_a_success_at=None, activation_started_at="2026-10-20T13:40:00Z", now=NOW,
    )
    startup_grace = select_plan(
        event="workflow_dispatch", fallback_requested=True, run_worker="paused",
        last_plan_a_success_at=None, activation_started_at="2026-10-20T14:20:00Z", now=NOW,
    )
    assert recent == ("VALIDATION_ONLY", "PLAN_B_REJECTED_PLAN_A_RECENT")
    assert stale == ("B", "PLAN_B_ALLOWED_PLAN_A_STALE")
    assert never_ran == ("B", "PLAN_B_ALLOWED_NO_SUCCESSFUL_PLAN_A_RUN")
    assert startup_grace == ("VALIDATION_ONLY", "PLAN_B_REJECTED_STARTUP_WINDOW")


def test_manifest_projects_state_without_claiming_external_execution(tmp_path: Path) -> None:
    root = make_repo(tmp_path)
    before = {
        str(path.relative_to(root)): path.read_bytes()
        for path in root.rglob("*") if path.is_file()
    }
    manifest = build_manifest(
        repo_root=root,
        event="schedule",
        now=NOW,
        run_id="123",
        run_attempt="1",
        run_number="7",
        ref="refs/heads/main",
        commit_sha="abc123",
        actor="test",
    )
    after = {
        str(path.relative_to(root)): path.read_bytes()
        for path in root.rglob("*") if path.is_file()
    }
    assert before == after
    assert manifest["control"]["selected_plan"] == "A"
    assert manifest["canonical_registry"]["hash_status"] == "PASS"
    assert manifest["overdrive_projection"]["record_count_status"] == "PASS"
    assert manifest["overdrive_projection"]["ready_claims"] == 2
    assert manifest["overdrive_projection"]["externally_ready_claims"] == 1
    assert manifest["overdrive_projection"]["work_conservation"] == "OPEN_WORK_PRESERVED; NO_AUTO_CLOSURE"
    assert manifest["control"]["commercial_worker_run"] is False
    assert manifest["control"]["external_writes_attempted"] is False
    assert manifest["acceptance_boundary"]["status"] == "PASS_REPOSITORY_PREFLIGHT_ONLY"


def test_manifest_fails_closed_on_registry_root_mismatch(tmp_path: Path) -> None:
    root = make_repo(tmp_path)
    path = root / "AMX/ROOT/BLUE_STATE/MANDATE_REGISTRY_V1.json"
    registry = json.loads(path.read_text())
    registry["registry_root_sha256"] = "0" * 64
    write_json(path, registry)
    with pytest.raises(ControlError, match="mandate registry root mismatch"):
        build_manifest(repo_root=root, event="schedule", now=NOW)


def test_manifest_fails_closed_on_ledger_count_mismatch(tmp_path: Path) -> None:
    root = make_repo(tmp_path)
    path = root / "overdrive/opportunities.json"
    ledger = json.loads(path.read_text())
    ledger["record_count"] = 9
    write_json(path, ledger)
    with pytest.raises(ControlError, match="opportunities ledger count mismatch"):
        build_manifest(repo_root=root, event="schedule", now=NOW)


def test_manifest_marks_future_dated_runtime_tick_as_clock_skew(tmp_path: Path) -> None:
    root = make_repo(tmp_path)
    state_path = root / "overdrive/state.json"
    state = json.loads(state_path.read_text())
    state["last_tick"] = "2026-10-20T15:20:00Z"
    write_json(state_path, state)

    manifest = build_manifest(repo_root=root, event="schedule", now=NOW)

    assert manifest["overdrive_projection"]["last_tick_age_minutes"] < 0
    assert manifest["overdrive_projection"]["freshness"] == "CLOCK_SKEW"


def test_automatic_watchdog_selects_plan_a_or_plan_b_from_durable_freshness() -> None:
    recent = select_plan(
        event="schedule", fallback_requested=True, run_worker="paused",
        schedule_expression=PLAN_B_WATCHDOG_CRON,
        last_plan_a_success_at="2026-10-20T14:20:00Z",
        activation_started_at="2026-10-20T13:00:00Z", now=NOW,
    )
    stale = select_plan(
        event="schedule", fallback_requested=True, run_worker="paused",
        schedule_expression=PLAN_B_WATCHDOG_CRON,
        last_plan_a_success_at="2026-10-20T13:40:00Z",
        activation_started_at="2026-10-20T13:00:00Z", now=NOW,
    )
    no_success_stale_activation = select_plan(
        event="schedule", fallback_requested=True, run_worker="paused",
        schedule_expression=PLAN_B_WATCHDOG_CRON,
        last_plan_a_success_at=None,
        activation_started_at="2026-10-20T13:40:00Z", now=NOW,
    )
    first_watchdog = select_plan(
        event="schedule", fallback_requested=True, run_worker="paused",
        schedule_expression=PLAN_B_WATCHDOG_CRON,
        last_plan_a_success_at=None,
        activation_started_at="2026-10-20T14:20:00Z", now=NOW,
    )
    assert recent == ("A", "PLAN_A_RECENT_WATCHDOG_NO_FALLBACK")
    assert stale == ("B", "PLAN_B_AUTOMATIC_WATCHDOG_PLAN_A_STALE")
    assert no_success_stale_activation == ("B", "PLAN_B_AUTOMATIC_WATCHDOG_NO_SUCCESSFUL_PLAN_A")
    assert first_watchdog == ("A", "PLAN_A_STARTUP_WINDOW_WATCHDOG_NO_FALLBACK")


def test_automatic_watchdog_requires_paused_worker_and_fails_closed_on_clock_skew() -> None:
    not_paused = select_plan(
        event="schedule", fallback_requested=True, run_worker="run",
        schedule_expression=PLAN_B_WATCHDOG_CRON,
        last_plan_a_success_at="2026-10-20T13:00:00Z",
        activation_started_at="2026-10-20T12:00:00Z", now=NOW,
    )
    assert not_paused == ("VALIDATION_ONLY", "PLAN_B_REJECTED_WORKER_MUST_REMAIN_PAUSED")
    with pytest.raises(ControlError, match="future"):
        select_plan(
            event="schedule", fallback_requested=True, run_worker="paused",
            schedule_expression=PLAN_B_WATCHDOG_CRON,
            last_plan_a_success_at="2026-10-20T15:20:00Z",
            activation_started_at="2026-10-20T12:00:00Z", now=NOW,
        )
    with pytest.raises(ControlError, match="activation timestamp"):
        select_plan(
            event="schedule", fallback_requested=True, run_worker="paused",
            schedule_expression=PLAN_B_WATCHDOG_CRON,
            last_plan_a_success_at=None, activation_started_at=None, now=NOW,
        )


def test_plan_a_anchor_validates_source_and_preserves_activation(tmp_path: Path) -> None:
    path = tmp_path / "overdrive/recovery-control/plan-a-anchor.json"
    path.parent.mkdir(parents=True)
    path.write_text(json.dumps({
        "schema": PLAN_A_ANCHOR_SCHEMA,
        "activated_at": "2026-10-20T13:00:00Z",
        "last_successful_plan_a": {
            "completed_at": "2026-10-20T14:00:00Z",
            "run_id": "1234",
            "commit_sha": "abc123",
        },
    }), encoding="utf-8")
    anchor = read_plan_a_anchor(path)
    assert anchor is not None
    assert anchor["activated_at"] == "2026-10-20T13:00:00Z"
    assert anchor["last_successful_plan_a"]["completed_at"] == "2026-10-20T14:00:00Z"


def test_plan_a_anchor_fails_closed_when_malformed(tmp_path: Path) -> None:
    path = tmp_path / "plan-a-anchor.json"
    path.write_text('{"schema":"wrong"}', encoding="utf-8")
    with pytest.raises(ControlError, match="schema"):
        read_plan_a_anchor(path)


def test_first_watchdog_build_manifest_starts_a_grace_window(tmp_path: Path) -> None:
    root = make_repo(tmp_path)
    manifest = build_manifest(
        repo_root=root, event="schedule", schedule_expression=PLAN_B_WATCHDOG_CRON,
        fallback_requested=True, run_worker="paused", now=NOW,
    )
    assert manifest["control"]["selected_plan"] == "A"
    assert manifest["control"]["liveness_anchor_status"] == "INITIALIZE_AFTER_SUCCESSFUL_WATCHDOG"
    assert manifest["control"]["plan_b_automatic_watchdog_enabled"] is True
