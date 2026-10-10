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

    def test_waiting_claim_clears_stale_external_ready_flag(self):
        records = {
            "crowdgen": {
                "state": "QUALIFIED",
                "execution_owner": "PRI",
                "execution_readiness": "HOLD_AUTHENTICATED_ROUTE",
                "next_action": "HOLD automated execution until an authenticated route is restored.",
            }
        }
        prior_claim = {
            "PRI|crowdgen": {
                "opportunity_key": "crowdgen",
                "state": "QUALIFIED",
                "status": "READY",
                "action_class": "EXTERNAL_APPLICATION",
                "external_action_ready": True,
                "attempts": 0,
            }
        }
        runner.write(runner.CLAIMS, {
            "version": 1,
            "claims": prior_claim,
            "ready_count": 1,
            "external_ready_count": 1,
            "executable_order": ["PRI|crowdgen"],
        })
        signals = runner.detect_work({"records": records})
        result = runner.claim_work(signals, {"records": records})
        claim = result["claims"]["PRI|crowdgen"]

        self.assertEqual(claim["status"], "WAITING")
        self.assertFalse(claim["external_action_ready"])
        self.assertEqual(result["ready_count"], 0)
        self.assertEqual(result["external_ready_count"], 0)
        self.assertEqual(result["executable_order"], [])

    def test_completed_claim_cannot_retain_external_ready_flag(self):
        runner.write(runner.CLAIMS, {
            "version": 1,
            "ready_count": 0,
            "external_ready_count": 1,
            "executable_order": [],
            "claims": {
                "PRI|done": {
                    "opportunity_key": "done",
                    "status": "COMPLETED",
                    "receipt": "immutable-receipt",
                    "external_action_ready": True,
                }
            },
        })
        result = runner.claim_work({"PRI": [], "iSCOPE": []}, {"records": {}})
        claim = result["claims"]["PRI|done"]

        self.assertEqual(claim["status"], "COMPLETED")
        self.assertEqual(claim["receipt"], "immutable-receipt")
        self.assertFalse(claim["external_action_ready"])
        self.assertEqual(result["external_ready_count"], 0)
        self.assertEqual(result["ready_count"], 0)
        self.assertEqual(result["executable_order"], [])

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

    def test_delivery_delay_is_nonterminal_evidence_gated_and_waiting(self):
        opportunities = self.records("SUBMITTED")
        runner.evidence_transition(
            self.make_task("SUBMITTED", "DELAYED", "DELIVERY_DELAY", next_action="Wait for provider retry result."),
            opportunities,
        )
        record = opportunities["records"]["opp"]
        routed = runner.commercial_action("opp", record, datetime.now(timezone.utc))
        self.assertEqual((record["state"], routed["status"], routed["routing_reason"]), ("DELAYED", "WAITING", "DELAYED"))
        with self.assertRaisesRegex(ValueError, "DELAYED requires attributable"):
            runner.evidence_transition(
                self.make_task("SUBMITTED", "DELAYED", "DELIVERY_FAILURE"),
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


class MissingRecordUpsertTest(unittest.TestCase):
    def task(self, key="new-opp", target="SUBMITTED", kind="GMAIL_SENT", **extra):
        payload = {
            "opportunity_key": key,
            "identity": {
                "organization": "Example Buyer",
                "opportunity": "Bounded pilot",
                "domain": "example.com",
            },
            "execution_owner": "PRI",
            "to": target,
            "evidence": [{"kind": kind, "source_id": "gmail-message-1"}],
            "observed_at": "2026-10-10T04:45:00Z",
            "next_action": "Read the existing thread and progress only if due.",
            "thread_id": "thread-1",
            "recipient": "buyer@example.com",
        }
        payload.update(extra)
        return {"payload": payload}

    def test_missing_record_upsert_creates_canonical_record(self):
        opportunities = {"records": {}}
        result = runner.missing_record_upsert(self.task(), opportunities)
        record = opportunities["records"]["new-opp"]
        self.assertEqual(result["adapter"], "MISSING_RECORD_UPSERT")
        self.assertEqual(record["state"], "SUBMITTED")
        self.assertEqual(record["execution_owner"], "PRI")
        self.assertEqual(record["thread_id"], "thread-1")
        self.assertEqual(record["evidence"][0]["source_id"], "gmail-message-1")
        self.assertEqual(record["canonical_ingest"]["kind"], "MISSING_RECORD_RECOVERY")

    def test_missing_record_upsert_supports_nonterminal_delay(self):
        opportunities = {"records": {}}
        result = runner.missing_record_upsert(
            self.task(target="DELAYED", kind="DELIVERY_DELAY", next_action="Wait for provider retry result."),
            opportunities,
        )
        record = opportunities["records"]["new-opp"]
        self.assertEqual((result["to"], record["state"]), ("DELAYED", "DELAYED"))
        routed = runner.commercial_action("new-opp", record, datetime.now(timezone.utc))
        self.assertEqual((routed["status"], routed["routing_reason"]), ("WAITING", "DELAYED"))

    def test_missing_record_upsert_refuses_existing_key(self):
        opportunities = {"records": {"new-opp": {"state": "SUBMITTED"}}}
        with self.assertRaisesRegex(ValueError, "already exists"):
            runner.missing_record_upsert(self.task(), opportunities)

    def test_missing_record_upsert_refuses_duplicate_identity(self):
        opportunities = {"records": {
            "existing": {
                "state": "QUALIFIED",
                "organization": "Example Buyer",
                "opportunity": "Bounded pilot",
                "domain": "example.com",
            }
        }}
        with self.assertRaisesRegex(ValueError, "possible duplicate canonical identity"):
            runner.missing_record_upsert(self.task(key="another-key"), opportunities)

    def test_missing_record_upsert_is_evidence_gated(self):
        opportunities = {"records": {}}
        with self.assertRaisesRegex(ValueError, "requires attributable evidence"):
            runner.missing_record_upsert(
                self.task(target="WRONG_ROUTE", kind="GMAIL_SENT"),
                opportunities,
            )

    def test_missing_record_upsert_cannot_skip_to_accepted(self):
        opportunities = {"records": {}}
        with self.assertRaisesRegex(ValueError, "cannot initialize state ACCEPTED"):
            runner.missing_record_upsert(
                self.task(target="ACCEPTED", kind="SCOPE_PRICE_ACCEPTANCE"),
                opportunities,
            )



class SemanticNoOpPersistenceTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        base = Path(self.tmp.name)
        runner.STATE = base / "state.json"
        runner.OPPORTUNITIES = base / "opportunities.json"
        runner.SIGNALS = base / "signals.json"
        runner.CLAIMS = base / "claims.json"
        runner.LOCK = base / ".tick.lock"
        runner.RECEIPTS = base / "receipts"
        runner.RECEIPTS.mkdir()
        runner.REQUESTS = base / "missing-requests.jsonl"

    def test_semantic_projection_ignores_scan_timestamps_only(self):
        a = {"generated_at": "one", "claims": {"x": {"status": "READY", "last_seen_at": "one"}}}
        b = {"generated_at": "two", "claims": {"x": {"status": "READY", "last_seen_at": "two"}}}
        self.assertEqual(runner.semantic_projection(a), runner.semantic_projection(b))
        b["claims"]["x"]["status"] = "WAITING"
        self.assertNotEqual(runner.semantic_projection(a), runner.semantic_projection(b))

    def test_second_identical_noop_tick_keeps_tracked_bytes_identical(self):
        runner.write(runner.STATE, {
            "version": 2,
            "adapter_status": "OPERATIONAL",
            "sequence": 0,
            "queue": [],
        })
        runner.write(runner.OPPORTUNITIES, {
            "records": {
                "opp": {
                    "state": "QUALIFIED",
                    "execution_owner": "PRI",
                    "next_action": "prepare bounded offer",
                    "evidence": [{"kind": "SOURCE", "source_id": "source-1"}],
                }
            }
        })

        self.assertEqual(runner.tick(), 0)
        first = {
            "state": runner.STATE.read_bytes(),
            "signals": runner.SIGNALS.read_bytes(),
            "claims": runner.CLAIMS.read_bytes(),
            "opportunities": runner.OPPORTUNITIES.read_bytes(),
        }

        self.assertEqual(runner.tick(), 0)
        second = {
            "state": runner.STATE.read_bytes(),
            "signals": runner.SIGNALS.read_bytes(),
            "claims": runner.CLAIMS.read_bytes(),
            "opportunities": runner.OPPORTUNITIES.read_bytes(),
        }
        self.assertEqual(first, second)


if __name__ == "__main__":
    unittest.main()
