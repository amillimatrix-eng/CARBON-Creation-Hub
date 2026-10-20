import json
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from overdrive.cadence_controller import (
    PLAN_A_CRON, PLAN_B_CRON, load_control, refresh_phase, record_success, select_action,
)

NOW = datetime(2026, 10, 20, 14, 0, tzinfo=timezone.utc)


def control_fixture():
    return {
        "schema": "AMX_RUNTIME_CADENCE_CONTROL_V1",
        "version": 1,
        "phase": "ACTIVE",
        "current_mode": "PLAN_A",
        "owner_pause": {"active": False},
        "plan_a": {"cron": PLAN_A_CRON},
        "plan_b": {"cron": PLAN_B_CRON, "stale_after_minutes": 70},
        "last_plan_a_success_at": "2026-10-20T13:20:00Z",
        "resume_gates": {"one": {"pass": True}},
        "transition_log": [],
        "rules": {"no_plan_c": True},
    }


class CadenceControllerTests(unittest.TestCase):
    def test_owner_pause_wins_over_both_triggers(self):
        c = control_fixture()
        c["phase"] = "PAUSED_INFRASTRUCTURE"
        c["owner_pause"]["active"] = True
        for schedule in (PLAN_A_CRON, PLAN_B_CRON):
            self.assertEqual(select_action(c, "schedule", schedule, now=NOW)["action"], "pause")

    def test_plan_a_uses_hourly_window(self):
        c = control_fixture()
        self.assertEqual(select_action(c, "schedule", PLAN_A_CRON, now=NOW)["action"], "plan_a")

    def test_plan_b_skips_while_plan_a_is_fresh(self):
        c = control_fixture()
        self.assertEqual(select_action(c, "schedule", PLAN_B_CRON, now=NOW)["action"], "skip")

    def test_plan_b_recovers_when_plan_a_is_stale(self):
        c = control_fixture()
        c["last_plan_a_success_at"] = "2026-10-20T12:45:00Z"
        result = select_action(c, "schedule", PLAN_B_CRON, now=NOW)
        self.assertEqual(result["action"], "plan_b")
        self.assertIn("STALE", result["reason"])

    def test_plan_b_recovers_when_no_plan_a_receipt_exists(self):
        c = control_fixture()
        c["last_plan_a_success_at"] = None
        self.assertEqual(select_action(c, "schedule", PLAN_B_CRON, now=NOW)["action"], "plan_b")

    def test_unknown_schedule_is_not_plan_c(self):
        c = control_fixture()
        result = select_action(c, "schedule", "13 * * * *", now=NOW)
        self.assertEqual(result["action"], "skip")
        self.assertEqual(result["reason"], "NO_MATCHING_DEFINED_PLAN")

    def test_manual_run_respects_infrastructure_pause(self):
        c = control_fixture()
        c["phase"] = "PAUSED_INFRASTRUCTURE"
        c["owner_pause"]["active"] = True
        self.assertEqual(select_action(c, "workflow_dispatch", manual_input="run", now=NOW)["action"], "pause")

    def test_recovery_to_plan_a_is_durable(self):
        c = control_fixture()
        c["current_mode"] = "PLAN_B"
        self.assertTrue(record_success(c, "plan_a", NOW))
        self.assertEqual(c["current_mode"], "PLAN_A")
        self.assertEqual(c["last_plan_a_success_at"], "2026-10-20T14:00:00Z")
        self.assertEqual(c["transition_log"][-1]["reason"], "PLAN_A_WINDOW_COMPLETED_AND_READBACK_PASSED")

    def test_pause_auto_releases_only_when_every_gate_passes(self):
        c = control_fixture()
        c["phase"] = "PAUSED_INFRASTRUCTURE"
        c["owner_pause"]["active"] = True
        c["resume_gates"] = {"one": {"pass": True}, "two": {"pass": False}}
        self.assertFalse(refresh_phase(c, NOW))
        c["resume_gates"]["two"]["pass"] = True
        self.assertTrue(refresh_phase(c, NOW))
        self.assertEqual(c["phase"], "ACTIVE")
        self.assertFalse(c["owner_pause"]["active"])

    def test_loader_rejects_undefined_plan_c(self):
        c = control_fixture()
        c["rules"]["no_plan_c"] = False
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "control.json"
            p.write_text(json.dumps(c), encoding="utf-8")
            with self.assertRaises(ValueError):
                load_control(p)


if __name__ == "__main__":
    unittest.main()
