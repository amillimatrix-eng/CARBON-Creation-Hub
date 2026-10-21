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
        return {"records": {"opp": {
            "state": state, "evidence": [], "execution_owner": "PRI",
            "proposal_ref": "AMX-OFFER-001", "offer_version": "v1",
        }}}

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
                accepted_proposal_ref="AMX-OFFER-001",
                accepted_offer_version="v1",
                buyer_po_reference="BUYER-PO-77",
            ),
            opportunities,
        )
        record = opportunities["records"]["opp"]
        self.assertEqual(record["state"], "ACCEPTED")
        self.assertEqual(record["commercial_acceptance"]["price"], "USD 1000")
        self.assertEqual(record["commercial_acceptance"]["proposal_ref"], "AMX-OFFER-001")
        self.assertEqual(record["commercial_acceptance"]["offer_version"], "v1")
        self.assertEqual(record["commercial_acceptance"]["buyer_po_reference"], "BUYER-PO-77")
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

    def test_acceptance_requires_current_offer_id_and_version(self):
        cases = [
            ({"accepted_proposal_ref": "AMX-OFFER-001"}, "accepted_proposal_ref and accepted_offer_version"),
            ({"accepted_proposal_ref": "AMX-OFFER-OLD", "accepted_offer_version": "v1"}, "accepted proposal_ref does not match"),
            ({"accepted_proposal_ref": "AMX-OFFER-001", "accepted_offer_version": "v2"}, "accepted offer version does not match"),
        ]
        for extra, expected_error in cases:
            with self.subTest(extra=extra):
                task = self.make_task(
                    "RESPONDED", "ACCEPTED", "SCOPE_PRICE_ACCEPTANCE",
                    accepted_scope="Pilot", accepted_price="USD 100", **extra,
                )
                with self.assertRaisesRegex(ValueError, expected_error):
                    runner.evidence_transition(task, self.records("RESPONDED"))
        opportunities = self.records("RESPONDED")
        opportunities["records"]["opp"].pop("offer_version")
        with self.assertRaisesRegex(ValueError, "canonical proposal_ref and offer_version"):
            runner.evidence_transition(
                self.make_task(
                    "RESPONDED", "ACCEPTED", "SCOPE_PRICE_ACCEPTANCE",
                    accepted_scope="Pilot", accepted_price="USD 100",
                    accepted_proposal_ref="AMX-OFFER-001", accepted_offer_version="v1",
                ),
                opportunities,
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

    def test_missing_record_upsert_is_idempotent_for_exact_existing_evidence(self):
        source_evidence = {
            "kind": "GMAIL_SENT",
            "source_id": "gmail-message-1",
            "source": "GMAIL",
            "observed_at": "2026-10-10T04:45:00Z",
        }
        canonical_key = "example.com|bounded-pilot|2026-10-10"
        record = {
            "state": "SUBMITTED",
            "execution_owner": "PRI",
            "organization": "Example Buyer",
            "opportunity": "bounded-pilot",
            "domain": "example.com",
            "recipient": "buyer@example.com",
            "thread_id": "thread-1",
            "last_action_at": "2026-10-10T04:45:00Z",
            "next_action": "Wait for a substantive buyer response.",
            "evidence": [dict(source_evidence)],
            "commercial_acceptance": None,
        }
        opportunities = {"records": {canonical_key: record}}
        before = json.loads(json.dumps(opportunities))

        result = runner.missing_record_upsert(
            self.task(key=canonical_key, evidence=[dict(source_evidence)]),
            opportunities,
        )

        self.assertFalse(result["created"])
        self.assertTrue(result["idempotent"])
        self.assertEqual(result["disposition"], "ALREADY_RECORDED_EXACT_EVIDENCE_REPLAY")
        self.assertEqual(result["critic"]["external_action"], "NOT_PERFORMED_BY_ADAPTER")
        self.assertEqual(opportunities, before)

    def test_missing_record_upsert_accepts_canonical_identity_when_org_label_varies(self):
        source_evidence = {
            "kind": "OUTBOUND_SEND",
            "source_id": "outlook-item-1",
            "source": "OUTLOOK",
            "observed_at": "2026-10-20T07:48:26Z",
        }
        canonical_key = "verminator.co.za|site-visit-to-follow-up-workflow-pilot|2026-10-20"
        record = {
            "state": "OFFERED",
            "execution_owner": "PRI",
            "organization": "Verminator Pest Control",
            "opportunity": "site-visit-to-follow-up-workflow-pilot",
            "domain": "verminator.co.za",
            "recipient": "quality@verminator.co.za",
            "thread_id": None,
            "last_action_at": "2026-10-20T07:48:26Z",
            "next_action": "Wait for a substantive buyer response.",
            "evidence": [dict(source_evidence)],
        }
        opportunities = {"records": {canonical_key: record}}
        before = json.loads(json.dumps(opportunities))
        result = runner.missing_record_upsert(
            self.task(
                key=canonical_key,
                target="OFFERED",
                kind="OUTBOUND_SEND",
                identity={
                    "organization": "Verminator",
                    "opportunity": "Site-visit-to-follow-up workflow pilot",
                    "domain": "verminator.co.za",
                },
                execution_owner="PRI",
                recipient="quality@verminator.co.za",
                thread_id=None,
                evidence=[dict(source_evidence)],
                observed_at="2026-10-20T07:48:26Z",
                next_action="Wait for a substantive buyer response.",
            ),
            opportunities,
        )
        self.assertTrue(result["idempotent"])
        self.assertFalse(result["created"])
        self.assertEqual(result["critic"]["commercial_state"], "PASS_NO_LIFECYCLE_CHANGE")
        self.assertEqual(opportunities, before)

    def test_verified_source_id_correction_preserves_old_value_and_lifecycle(self):
        canonical_key = "mendazsolar.co.za|solar-service-follow-through-pilot|2026-10-20"
        actual_id = "AQMkADAwATM0MDAAMS03NTM2LTYyNzgtMDACLTAwCgBGAAADR02W6I7woU2AiDvBGiB_dgcACcuKl8g3RkyfBaEy7toItQAAAgEJAAAACcuKl8g3RkyfBaEy7toItQACLz9RvQAAAA=="
        old_id = "AQMkADAwATM0MDAAMS03NTM2LTYyNzgtMDACLTAwCgBGAAADR02W6I7woU2AiDvBGiB_dgcACcuKl8g3Rky7toItQAAAgEJAAAACcuKl8g3RkyfBaEy7toItQACLz9RvQAAAA=="
        subject = "One bounded pilot for solar service follow-through"
        observed_at = "2026-10-20T07:47:43Z"
        sent = {
            "kind": "OUTBOUND_SEND",
            "source_id": actual_id,
            "source": "OUTLOOK",
            "observed_at": observed_at,
            "subject": subject,
        }
        readback = {
            "kind": "OUTLOOK_SENT_ITEM_ID_READBACK",
            "source_id": actual_id,
            "source": "OUTLOOK_SENT_ITEMS_READBACK",
            "folder": "Sent Items",
            "subject": subject,
            "recipient": "info@mendazsolar.co.za",
            "query_filter": "sentDateTime ge 2026-10-20T00:00:00Z",
            "receipt_path": "AMX/ROOT/INTAKE/DRAIN_Q_EXECUTION_RECEIPT_20261020_FOLLOW_ON.md",
            "verification_receipt_commit": "5ba77e811c435e362566d97c2d5a954d44ef9bc9",
        }
        record = {
            "state": "OFFERED",
            "execution_owner": "PRI",
            "organization": "Mendaz Solar",
            "opportunity": "solar-service-follow-through-pilot",
            "domain": "mendazsolar.co.za",
            "recipient": "info@mendazsolar.co.za",
            "thread_id": None,
            "last_action_at": observed_at,
            "next_action": "Wait for a substantive buyer response.",
            "evidence": [
                {
                    "kind": "OUTBOUND_SEND",
                    "source_id": old_id,
                    "source": "OUTLOOK",
                    "observed_at": observed_at,
                    "subject": subject,
                },
                {
                    "kind": "POST_SEND_OFFER_CONTROL_REVIEW",
                    "source_id": old_id,
                    "source": "OUTLOOK_SENT_ITEMS_AND_ATTACHMENTS_READBACK",
                    "observed_at": "2026-10-21T02:47:35.668Z",
                    "subject": subject,
                },
            ],
        }
        opportunities = {"records": {canonical_key: record}}
        task = self.task(
            key=canonical_key,
            target="OFFERED",
            kind="OUTBOUND_SEND",
            identity={
                "organization": "Mendaz Solar",
                "opportunity": "solar-service-follow-through-pilot",
                "domain": "mendazsolar.co.za",
            },
            evidence=[sent, readback],
            recipient="info@mendazsolar.co.za",
            thread_id=None,
            observed_at=observed_at,
            next_action="Wait for a substantive buyer response.",
        )

        result = runner.missing_record_upsert(task, opportunities)
        corrected = opportunities["records"][canonical_key]
        self.assertTrue(result["source_id_corrected"])
        self.assertFalse(result["lifecycle_changed"])
        self.assertEqual(corrected["state"], "OFFERED")
        self.assertEqual(corrected["evidence"][0]["source_id"], actual_id)
        self.assertEqual(corrected["evidence"][1]["source_id"], actual_id)
        self.assertEqual(corrected["source_id_corrections"][0]["previous_source_id"], old_id)
        self.assertEqual(corrected["source_id_corrections"][0]["corrected_source_id"], actual_id)
        self.assertIn(readback, corrected["evidence"])

        # The next wake is an exact replay, not another correction or external action.
        result_again = runner.missing_record_upsert(task, opportunities)
        self.assertTrue(result_again["idempotent"])
        self.assertEqual(len(corrected["source_id_corrections"]), 1)
        self.assertEqual(corrected["state"], "OFFERED")

    def test_missing_record_upsert_refuses_same_action_with_conflicting_source_id(self):
        canonical_key = "example.com|bounded-pilot|2026-10-10"
        evidence = {
            "kind": "OUTBOUND_SEND",
            "source_id": "outlook-id-corrected",
            "source": "OUTLOOK",
            "observed_at": "2026-10-10T04:45:00Z",
            "subject": "Bounded pilot offer",
        }
        record = {
            "state": "OFFERED",
            "execution_owner": "PRI",
            "organization": "Example Buyer",
            "opportunity": "bounded-pilot",
            "domain": "example.com",
            "recipient": "buyer@example.com",
            "thread_id": None,
            "evidence": [{
                "kind": "OUTBOUND_SEND",
                "source_id": "outlook-id-old",
                "source": "OUTLOOK",
                "observed_at": "2026-10-10T04:45:00Z",
                "subject": "Bounded pilot offer",
            }],
        }
        task = self.task(
            key=canonical_key,
            target="OFFERED",
            kind="OUTBOUND_SEND",
            identity={
                "organization": "Example Buyer",
                "opportunity": "Bounded pilot",
                "domain": "example.com",
            },
            evidence=[evidence],
            recipient="buyer@example.com",
            observed_at="2026-10-10T04:45:00Z",
        )
        with self.assertRaisesRegex(ValueError, "exact evidence replay not proven"):
            runner.missing_record_upsert(task, {"records": {canonical_key: record}})

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
