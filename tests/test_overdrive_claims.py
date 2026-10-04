"""Regression coverage for durable claims reconciled against the current ledger."""
import importlib.util
import json
from pathlib import Path
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

if __name__ == "__main__":
    unittest.main()
