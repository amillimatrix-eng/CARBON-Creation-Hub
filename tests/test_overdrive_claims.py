"""Regression coverage for durable claims reconciled against the current ledger."""
import importlib.util
import json
from pathlib import Path
from datetime import datetime, timezone
import tempfile
import unittest

spec = importlib.util.spec_from_file_location("overdrive_runner", Path(__file__).parents[1] / "overdrive" / "runner.py")
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)

class RoutingReconciliationTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        runner.CLAIMS = Path(self.tmp.name) / "claims.json"
        runner.SIGNALS = Path(self.tmp.name) / "signals.json"

    def seed(self, records, claims):
        runner.write(runner.CLAIMS, {"version": 1, "claims": claims})
        signals = runner.detect_work({"records": records})
        return runner.claim_work(signals, {"records": records})

    def test_submitted_future_due_cannot_stay_ready_or_resend(self):
        result = self.seed({"jojo": {"state": "SUBMITTED", "execution_owner": "PRI", "next_action": "monitor existing thread", "due_at": "2099-10-08T08:00:00Z"}},
                           {"PRI|jojo": {"opportunity_key": "jojo", "state": "QUALIFIED", "status": "READY", "attempts": 2, "receipt": "sent-proof"}})
        claim = result["claims"]["PRI|jojo"]
        self.assertEqual((claim["state"], claim["status"], claim["next_action"]), ("SUBMITTED", "WAITING", "monitor existing thread"))
        self.assertEqual((claim["attempts"], claim["receipt"], result["ready_count"]), (2, "sent-proof", 0))

    def test_closed_owner_is_not_routed_and_closure_keeps_evidence(self):
        result = self.seed({"alakai": {"state": "CLOSED_NO_FIT", "execution_owner": "iSCOPE", "evidence": [{"kind": "BUYER_RESPONSE", "source_id": "real-message"}]}},
                           {"iSCOPE|alakai": {"opportunity_key": "alakai", "status": "READY"}})
        self.assertEqual(runner.read(runner.SIGNALS)["iSCOPE"], [])
        self.assertEqual(result["claims"]["iSCOPE|alakai"]["status"], "CLOSED")
        self.assertEqual(result["claims"]["iSCOPE|alakai"]["closure_evidence"][0]["source_id"], "real-message")

    def test_missing_or_unevidenced_record_is_preserved_without_closure(self):
        result = self.seed({"unproven": {"state": "CLOSED_NO_FIT", "execution_owner": "PRI"}},
                           {"PRI|missing": {"opportunity_key": "missing", "status": "READY"},
                            "PRI|unproven": {"opportunity_key": "unproven", "status": "READY"}})
        self.assertEqual(len(result["claims"]), 2)
        self.assertTrue(all(c["status"] == "WAITING" for c in result["claims"].values()))

    def test_active_claim_and_completed_receipt_survive_reconciliation(self):
        records = {"active": {"state": "QUALIFIED", "execution_owner": "PRI", "next_action": "prepare"},
                   "done": {"state": "SUBMITTED", "execution_owner": "PRI"}}
        result = self.seed(records, {"PRI|active": {"opportunity_key": "active", "attempts": 3, "status": "READY"},
                                     "PRI|done": {"opportunity_key": "done", "status": "COMPLETED", "receipt": "immutable"}})
        self.assertEqual(result["ready_count"], 1)
        self.assertEqual(result["claims"]["PRI|active"]["attempts"], 3)
        self.assertEqual(result["claims"]["PRI|done"]["receipt"], "immutable")
        again = runner.claim_work(runner.detect_work({"records": records}), {"records": records})
        self.assertEqual(again["ready_count"], result["ready_count"])
        self.assertEqual(again["claims"]["PRI|done"], result["claims"]["PRI|done"])
        self.assertEqual(again["claims"]["PRI|active"]["attempts"], 3)


class EvidenceTransitionTest(unittest.TestCase):
    def records(self, state):
        return {"records": {"opp": {"state": state, "evidence": [], "execution_owner": "PRI"}}}

    def make_task(self, expected, target, kind, **extra):
        payload = {
            "opportunity_key": "opp",
            "expected_from": expected,
            "to": target,
            "evidence": [{"kind": kind, "source_id": "evidence-1"}],
            "observed_at": "2026-10-10T04:30:00Z",
            "next_action": "progress the exact next commercial step",
        }
        payload.update(extra)
        return {"payload": payload}

    def test_rejection_is_representable_and_evidence_gated(self):
        opportunities = self.records("OFFERED")
        runner.evidence_transition(
            self.make_task("OFFERED", "REJECTED", "BUYER_REJECTION"),
            opportunities,
        )
        self.assertEqual(opportunities["records"]["opp"]["state"], "REJECTED")
        with self.assertRaisesRegex(ValueError, "REJECTED requires attributable"):
            runner.evidence_transition(
                self.make_task("SUBMITTED", "REJECTED", "BUYER_RESPONSE"),
                self.records("SUBMITTED"),
            )

    def test_wrong_route_waits_for_route_recovery(self):
        opportunities = self.records("SUBMITTED")
        runner.evidence_transition(
            self.make_task("SUBMITTED", "WRONG_ROUTE", "WRONG_ROUTE_RESPONSE"),
            opportunities,
        )
        record = opportunities["records"]["opp"]
        record["next_action"] = "recover a verified current route"
        routed = runner.commercial_action("opp", record, datetime.now(timezone.utc))
        self.assertEqual((routed["state"], routed["status"]), ("WRONG_ROUTE", "WAITING"))

    def test_no_contact_requires_governed_suppression(self):
        opportunities = self.records("RESPONDED")
        runner.evidence_transition(
            self.make_task("RESPONDED", "NO_CONTACT", "OWNER_NO_CONTACT_SUPERSESSION"),
            opportunities,
        )
        self.assertEqual(opportunities["records"]["opp"]["state"], "NO_CONTACT")
        with self.assertRaisesRegex(ValueError, "NO_CONTACT requires attributable"):
            runner.evidence_transition(
                self.make_task("RESPONDED", "NO_CONTACT", "BUYER_RESPONSE"),
                self.records("RESPONDED"),
            )

    def test_acceptance_requires_specific_evidence_scope_and_price(self):
        opportunities = self.records("RESPONDED")
        runner.evidence_transition(
            self.make_task(
                "RESPONDED",
                "ACCEPTED",
                "SCOPE_PRICE_ACCEPTANCE",
                accepted_scope="Two production-ready episodes",
                accepted_price="USD 1000",
                accepted_currency="USD",
            ),
            opportunities,
        )
        record = opportunities["records"]["opp"]
        self.assertEqual(record["state"], "ACCEPTED")
        self.assertEqual(record["commercial_acceptance"]["price"], "USD 1000")
        routed = runner.commercial_action("opp", record, datetime.now(timezone.utc))
        self.assertEqual((routed["status"], routed["priority"]), ("READY", 1))

        with self.assertRaisesRegex(ValueError, "ACCEPTED requires attributable"):
            runner.evidence_transition(
                self.make_task(
                    "RESPONDED",
                    "ACCEPTED",
                    "BUYER_RESPONSE",
                    accepted_scope="Pilot",
                    accepted_price="USD 100",
                ),
                self.records("RESPONDED"),
            )

        with self.assertRaisesRegex(ValueError, "accepted_scope and accepted_price"):
            runner.evidence_transition(
                self.make_task(
                    "RESPONDED",
                    "ACCEPTED",
                    "BUYER_ACCEPTANCE",
                    accepted_scope="Pilot",
                ),
                self.records("RESPONDED"),
            )

    def test_accepted_can_progress_to_contracted(self):
        opportunities = self.records("ACCEPTED")
        result = runner.evidence_transition(
            self.make_task("ACCEPTED", "CONTRACTED", "CONTRACT_RECEIPT"),
            opportunities,
        )
        self.assertEqual(result["to"], "CONTRACTED")

if __name__ == "__main__":
    unittest.main()
