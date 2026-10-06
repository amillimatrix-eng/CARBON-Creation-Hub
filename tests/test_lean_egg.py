"""Bounded issue #8 regression tests; no external action or live worker loop."""
import copy
import hashlib
import hmac
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from backend.app import create_app
from backend.state import summarize_opportunities
from backend.store import EvidenceStore
from fastapi.testclient import TestClient
from overdrive import runner
from overdrive.payment_truth import payment_state, verified_payment
from overdrive.payment_verifier import attest_stripe_settlement, SettlementVerificationError

spec = importlib.util.spec_from_file_location("black_worker", Path(__file__).resolve().parents[1] / "BLACK/worker.py")
black = importlib.util.module_from_spec(spec)
spec.loader.exec_module(black)
KEY = "test-only-independent-verifier-key-123456789"


def receivable():
    return {"state": "RECEIVABLE", "amount_due": "100.00", "currency": "USD",
            "payer_id": "buyer-1", "payee_account": "amx-bank", "evidence": []}


def settlement(**changes):
    facts = {"kind": "PAYMENT_SETTLED", "source": "BANK", "source_id": "bank-tx-001",
             "source_reference": "bank://statement/transaction-001", "status": "SETTLED",
             "direction": "INBOUND", "independently_verified": True, "opportunity_key": "buyer",
             "amount": "100.00", "currency": "USD", "payer_id": "buyer-1",
             "payee_account": "amx-bank", "settled_at": "2026-10-01T12:00:00Z"}
    facts.update(changes)
    facts["verification_hmac"] = hmac.new(KEY.encode(), json.dumps(facts, sort_keys=True, separators=(",", ":")).encode(), hashlib.sha256).hexdigest()
    return facts


class PaymentTruth(unittest.TestCase):
    def setUp(self):
        self.env = patch.dict(os.environ, {"AMX_PAYMENT_VERIFICATION_KEY": KEY})
        self.env.start(); self.addCleanup(self.env.stop)

    def transition(self, evidence):
        record = receivable()
        task = {"payload": {"opportunity_key": "buyer", "expected_from": "RECEIVABLE", "to": "PAID",
                            "evidence": evidence, "observed_at": "2026-10-01T12:00:00Z", "next_action": "reconcile"}}
        result = runner.evidence_transition(task, {"records": {"buyer": record}})
        return record, result

    def test_false_evidence_cannot_create_or_project_paid(self):
        false = [{"kind": kind, "source_id": "internal-label"} for kind in
                 ("GMAIL_SENT", "BUYER_RESPONSE", "INVOICE", "INTERNAL_RECEIPT", "PAID", "PAYMENT_SETTLED")]
        forged = settlement(); forged["amount"] = "200.00"
        false.extend([forged, settlement(source="GMAIL"), settlement(opportunity_key="other"),
                      settlement(amount="99"), settlement(currency="ZAR"), settlement(payee_account="other"),
                      settlement(payer_id="other"), settlement(status="PENDING"), settlement(direction="OUTBOUND"),
                      settlement(independently_verified=False), settlement(amount="NaN")])
        for evidence in false:
            with self.subTest(evidence=evidence):
                record = receivable(); before = copy.deepcopy(record)
                with self.assertRaises(ValueError):
                    task = {"payload": {"opportunity_key": "buyer", "expected_from": "RECEIVABLE", "to": "PAID", "evidence": [evidence]}}
                    runner.evidence_transition(task, {"records": {"buyer": record}})
                self.assertEqual(record, before)
                record.update(state="PAID", evidence=[evidence])
                summary = summarize_opportunities({"records": {"buyer": record}})
                self.assertEqual(summary["paid_record_count"], 0)
                self.assertFalse(summary["realized_revenue_evidence"]["present"])
                self.assertEqual(payment_state(record, "buyer"), "PAYMENT_UNVERIFIED")

    def test_valid_independent_settlement_creates_and_projects_paid(self):
        record, result = self.transition([settlement()])
        self.assertEqual(result["to"], "PAID")
        self.assertTrue(verified_payment(record, "buyer"))
        self.assertEqual(summarize_opportunities({"records": {"buyer": record}})["paid_record_keys"], ["buyer"])
        with patch.dict(os.environ, {"AMX_PAYMENT_VERIFICATION_KEY": ""}):
            self.assertEqual(payment_state(record, "buyer"), "PAYMENT_UNVERIFIED")

    def test_commercial_states_remain_distinct(self):
        states = ["SUBMITTED", "RESPONDED", "CONTRACTED", "INVOICED", "RECEIVABLE"]
        summary = summarize_opportunities({"records": {x: {"state": x} for x in states}})
        self.assertEqual(set(summary["state_counts"]), set(states))


class StripeSettlementVerifier(unittest.TestCase):
    def setUp(self):
        self.env = patch.dict(os.environ, {
            "AMX_PAYMENT_VERIFICATION_KEY": KEY,
            "STRIPE_SECRET_KEY": "sk_live_test_only",
        })
        self.env.start(); self.addCleanup(self.env.stop)
        self.record = {
            "state": "RECEIVABLE",
            "amount_due": "100.00",
            "currency": "USD",
            "payer_id": "buyer-1",
            "payee_account": "amx-stripe",
            "evidence": [],
        }
        self.intent = {
            "id": "pi_verified_001",
            "status": "succeeded",
            "currency": "usd",
            "amount_received": 10000,
            "metadata": {
                "opportunity_key": "buyer",
                "payer_id": "buyer-1",
                "payee_account": "amx-stripe",
            },
            "latest_charge": {"paid": True, "created": 1790000000},
        }

    @patch("overdrive.payment_verifier.fetch_stripe_payment_intent")
    def test_processor_read_creates_valid_settlement_and_paid_transition(self, fetch):
        fetch.return_value = copy.deepcopy(self.intent)
        evidence = attest_stripe_settlement(self.record, "buyer", "pi_verified_001")
        self.assertTrue(verified_payment(self.record, "buyer", [evidence]))
        ledger = {"records": {"buyer": copy.deepcopy(self.record)}}
        result = runner.stripe_payment_settlement(
            {"payload": {
                "opportunity_key": "buyer",
                "expected_from": "RECEIVABLE",
                "payment_intent_id": "pi_verified_001",
            }},
            ledger,
        )
        self.assertEqual(result["to"], "PAID")
        self.assertEqual(result["adapter"], "STRIPE_PAYMENT_SETTLEMENT")
        self.assertEqual(ledger["records"]["buyer"]["state"], "PAID")
        self.assertTrue(verified_payment(ledger["records"]["buyer"], "buyer"))

    @patch("overdrive.payment_verifier.fetch_stripe_payment_intent")
    def test_processor_mismatch_or_unsettled_payment_fails_closed(self, fetch):
        for change in (
            {"status": "processing"},
            {"amount_received": 9999},
            {"currency": "zar"},
            {"metadata": {"opportunity_key": "other", "payer_id": "buyer-1", "payee_account": "amx-stripe"}},
            {"latest_charge": {"paid": False, "created": 1790000000}},
        ):
            with self.subTest(change=change):
                payload = copy.deepcopy(self.intent)
                payload.update(change)
                fetch.return_value = payload
                with self.assertRaises(SettlementVerificationError):
                    attest_stripe_settlement(self.record, "buyer", "pi_verified_001")

    @patch("overdrive.payment_verifier.fetch_stripe_payment_intent")
    def test_settlement_cannot_be_signed_without_independent_verifier_key(self, fetch):
        fetch.return_value = copy.deepcopy(self.intent)
        with patch.dict(os.environ, {"AMX_PAYMENT_VERIFICATION_KEY": ""}):
            with self.assertRaises(SettlementVerificationError):
                attest_stripe_settlement(self.record, "buyer", "pi_verified_001")


class BlackTruth(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name); self.rcpt = self.root / "BLACK/receipts"; self.rcpt.mkdir(parents=True)
        self.job = self.root / "job.json"
        self.job.write_text(json.dumps({"command": ["false"], "max_attempts": 3, "retry_delay_seconds": 10}))
        self.root_patch = patch.object(black, "ROOT", self.root); self.root_patch.start(); self.addCleanup(self.root_patch.stop)
        self.receipt_patch = patch.object(black, "RCPT", self.rcpt); self.receipt_patch.start(); self.addCleanup(self.receipt_patch.stop)

    def execute(self, code):
        def run(args, timeout=120):
            return subprocess.CompletedProcess(args, code if args[0] == "timeout" else 0, "output", "error" if code else "")
        with patch.object(black, "sh", side_effect=run): return black.process_job(self.job)

    def expire(self, path):
        rec = json.loads(path.read_text()); rec["finished"] = "2026-01-01T00:00:00Z"
        path.write_text(json.dumps(rec))

    def test_failure_timeout_bounded_retries_and_success_attribution(self):
        self.assertEqual(self.execute(1)["state"], "FAILED")
        self.assertIsNone(self.execute(0))  # Retry is not due yet.
        first = self.rcpt / "job.json"; self.expire(first); historical = first.read_bytes()
        second = self.execute(124)
        self.assertEqual(second["state"], "TIMED_OUT")
        self.assertEqual(first.read_bytes(), historical)
        self.expire(self.rcpt / "job.attempt-002.json")
        last = self.execute(0)
        self.assertEqual((last["state"], last["attempt"]), ("SUCCEEDED", 3))
        self.assertEqual(last["previous_receipt"], "job.attempt-002.json")
        self.assertEqual(last["previous_receipt_sha256"], hashlib.sha256((self.rcpt / "job.attempt-002.json").read_bytes()).hexdigest())
        self.assertIsNone(self.execute(0))

    def test_legacy_false_resolved_is_preserved_and_retryable(self):
        original = b'{"state":"RESOLVED","exit_code":1,"finished":"2026-01-01T00:00:00Z"}'
        (self.rcpt / "job.json").write_bytes(original)
        result = self.execute(0)
        self.assertEqual((result["state"], result["attempt"]), ("SUCCEEDED", 2))
        self.assertEqual((self.rcpt / "job.json").read_bytes(), original)

    def test_retry_limit_and_historical_jobs_require_opt_in(self):
        self.job.write_text(json.dumps({"command": ["false"]}))
        self.execute(1); self.expire(self.rcpt / "job.json")
        self.assertIsNone(self.execute(0))
        self.assertEqual(len(list(self.rcpt.glob("*.json"))), 1)
        self.job.write_text(json.dumps({"command": ["false"], "max_attempts": 2}))
        self.assertEqual(self.execute(0)["state"], "SUCCEEDED")

    def test_timeout_is_real_failure(self):
        result = black.sh([sys.executable, "-c", "import time;time.sleep(1)"], timeout=0.02)
        self.assertEqual(result.returncode, 124)

    def test_three_failures_exhaust_the_bounded_retry_budget(self):
        for attempt in range(1, 4):
            result = self.execute(1)
            self.assertEqual((result["state"], result["attempt"]), ("FAILED", attempt))
            path = self.rcpt / ("job.json" if attempt == 1 else f"job.attempt-{attempt:03d}.json")
            self.expire(path)
        self.assertIsNone(self.execute(0))
        self.assertEqual(len(list(self.rcpt.glob("*.json"))), 3)

    def test_command_start_failure_is_truthful(self):
        with patch.object(black.subprocess, "run", side_effect=FileNotFoundError):
            self.assertEqual(black.sh(["missing"]).returncode, 127)


class CommercialTruth(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        for name, path in (("CLAIMS", self.root / "claims.json"), ("SIGNALS", self.root / "signals.json"), ("REQUESTS", self.root / "requests.jsonl")):
            p = patch.object(runner, name, path); p.start(); self.addCleanup(p.stop)

    def test_full_ledger_waiting_does_not_block_executable_and_money_order(self):
        records = {
            "hold": {"state": "HOLD_CAPABILITY_GAP", "execution_owner": "iSCOPE", "next_action": "verify"},
            "blocked": {"state": "QUALIFIED", "execution_owner": "PRI", "next_action": "recover", "active_dependencies": {"login": {"state": "ACTIVE", "next": "Owner signs in"}}},
            "no-route": {"state": "QUALIFIED", "execution_owner": "PRI", "next_action": "apply", "constraints": ["No authenticated submission surface is connected"]},
            "unverified-route": {"state": "QUALIFIED", "execution_owner": "iSCOPE", "next_action": "handoff", "submission_ready": True},
            "waiting": {"state": "SUBMITTED", "execution_owner": "PRI", "next_action": "monitor", "due_at": "2999-01-01T00:00:00Z"},
            "cash": {"state": "RECEIVABLE", "execution_owner": "PRI", "next_action": "collect", "due_at": "2026-01-01T00:00:00Z"},
            "engaged": {"state": "RESPONDED", "execution_owner": "PRI", "next_action": "answer buyer", "thread_id": "thread-1"},
            "contract": {"state": "CONTRACTED", "execution_owner": "PRI", "next_action": "issue invoice"},
            "invoice": {"state": "INVOICED", "execution_owner": "PRI", "next_action": "check invoice", "due_at": "2999-01-01T00:00:00Z"},
            "submission": {"state": "QUALIFIED", "execution_owner": "iSCOPE", "next_action": "handoff", "submission_ready": True, "route_verified_live": True, "payment": "provider"},
            "small": {"state": "QUALIFIED", "execution_owner": "iSCOPE", "next_action": "handoff", "bounded_paid_deliverable": "fix", "acceptance_criteria": "test", "payment": "bank"},
            "direct": {"state": "QUALIFIED", "execution_owner": "iSCOPE", "next_action": "handoff", "bounded_paid_deliverable": "fix", "credible_buyer": "buyer"},
        }
        ledger = {"records": records}
        signals = runner.detect_work(ledger); claims = runner.claim_work(signals, ledger)
        self.assertEqual(len(signals["ledger"]), len(records))
        for office, key in (("iSCOPE", "hold"), ("PRI", "blocked"), ("PRI", "waiting"), ("PRI", "no-route"), ("iSCOPE", "unverified-route")):
            self.assertEqual(claims["claims"][office + "|" + key]["status"], "WAITING")
        self.assertEqual([k.split("|")[1] for k in claims["executable_order"]], ["cash", "engaged", "contract", "invoice", "submission", "small", "direct"])
        self.assertEqual(claims["claims"]["PRI|engaged"]["thread_id"], "thread-1")
        self.assertTrue(all(claims["claims"][k]["smallest_next_action"] for k in claims["executable_order"]))

    def test_customer_request_deduped_nonterminal_until_attributable_action(self):
        request = {"request_id": "CPR-1", "opportunity_key": "buyer", "thread_id": "thread-1", "customer_id": "customer-1", "proposal_ref": "proposal-1", "action": "REQUEST_CALLBACK", "message": "Call tomorrow"}
        runner.REQUESTS.write_text(json.dumps(request) + "\n" + json.dumps(request) + "\n")
        ledger = {"records": {"buyer": {"state": "SUBMITTED", "execution_owner": "PRI", "thread_id": "thread-1", "next_action": "monitor"}}}
        result = runner.claim_work(runner.detect_work(ledger), ledger)
        key = "PRI|buyer|request|CPR-1"
        self.assertEqual(len([c for c in result["claims"].values() if c.get("customer_request_id")]), 1)
        claim = result["claims"][key]
        self.assertEqual((claim["status"], claim["thread_id"], claim["customer_id"]), ("READY", "thread-1", "customer-1"))
        self.assertNotIn("Call tomorrow", json.dumps(result))
        claim.update(status="COMPLETED", receipt="internal-label")
        runner.write(runner.CLAIMS, result)
        self.assertEqual(runner.claim_work(runner.detect_work(ledger), ledger)["claims"][key]["status"], "READY")
        claim["action_evidence"] = {"kind": "CUSTOMER_REQUEST_ACTIONED", "source_id": "gmail-reply", "thread_id": "thread-1"}
        runner.write(runner.CLAIMS, result)
        self.assertEqual(runner.claim_work(runner.detect_work(ledger), ledger)["claims"][key]["status"], "COMPLETED")


class ExposureAndIntake(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name) / "repo"; self.root.mkdir()
        self.house = self.root / "house/remediation"; self.house.mkdir(parents=True)
        (self.house / "index.html").write_text("public house")
        (self.house / "proposal.html").write_text("customer portal")
        (self.house / "house.css").write_text("body{}")
        (self.house / "config.js").write_text('window.PROVIDER_TOKEN="private-secret"')
        (self.house / "proposals.json").write_text('{"leaked-token":"customer secret"}')
        (self.house / ".env").write_text("PROVIDER_SECRET=secret")
        (self.root / "overdrive").mkdir()
        (self.root / "overdrive/opportunities.json").write_text(json.dumps({"records": {"buyer": {"state": "SUBMITTED", "execution_owner": "PRI", "thread_id": "thread-1", "next_action": "monitor"}}}))
        self.registry = Path(self.tmp.name) / "private-proposals.json"
        self.registry.write_text(json.dumps({"proposals": {"runtime-only-token": {"proposal_ref": "proposal-1", "status": "DRAFT", "modules": [], "customer_id": "customer-1", "opportunity_key": "buyer", "thread_id": "thread-1", "provider_secret": "do-not-project"}}}))
        env = patch.dict(os.environ, {"AMX_ADMIN_TOKEN": "admin-test", "AMX_PROPOSAL_REGISTRY_PATH": str(self.registry)})
        env.start(); self.addCleanup(env.stop)
        self.client = TestClient(create_app(self.root, self.root / "data/test.db")); self.addCleanup(self.client.close)

    def test_static_allowlist_and_private_operators(self):
        for path in ("proposals.json", ".env", "DEPLOYMENT_MANIFEST.json", "index.html", "proposal.html"):
            self.assertEqual(self.client.get("/house/assets/" + path).status_code, 404)
        self.assertEqual(self.client.get("/house/assets/house.css").status_code, 200)
        self.assertNotIn("private-secret", self.client.get("/house/assets/config.js").text)
        for endpoint in ("/api/operator/state", "/api/opportunities", "/api/opportunities/buyer", "/api/t10"):
            self.assertEqual(self.client.get(endpoint).status_code, 401)
        bootstrap = self.client.get("/api/house/bootstrap").json()
        self.assertNotIn("system_truth", bootstrap["operator"])
        self.assertNotIn("payment_rails", bootstrap["operator"])
        with patch.dict(os.environ, {"AMX_PROPOSAL_REGISTRY_PATH": ""}):
            self.assertEqual(self.client.get("/api/proposals/leaked-token").status_code, 404)

    def test_evidence_deny_by_default_and_version_history_guard(self):
        base = {"evidence_id": "private", "capability": "private", "artifact": "private-secret", "authoritative_source": "repo", "status_freshness": "CURRENT", "interview_safe_explanation": "internal", **{k: "HOLD" for k in ("T10_JOB", "T10_ACTUAL", "T10_EVIDENCE", "T10_CHANGE", "T10_REMAINING_GAP", "T10_PASS")}}
        store = self.client.app.state.store
        store.upsert(base)
        changed = {**base, "artifact": "different-private-secret", "visibility": "TYPO_PUBLIC"}; store.upsert(changed)
        self.assertEqual(self.client.get("/api/evidence/private").status_code, 404)
        self.assertEqual(self.client.get("/api/evidence/private/versions").status_code, 401)
        self.assertEqual(self.client.get("/api/evidence").json()["count"], 0)
        self.assertEqual(self.client.post("/api/evidence/search", json={"query": "private"}).json()["count"], 0)
        store.upsert({**base, "visibility": "PUBLIC", "artifact": "approved"})
        self.assertEqual(self.client.get("/api/evidence/private").status_code, 200)
        self.assertEqual(self.client.get("/api/evidence/private/versions").status_code, 401)

    def test_intake_dedupes_and_hands_off_to_existing_pri_claims(self):
        endpoint = "/api/proposals/runtime-only-token/request-change"
        payload = {"action": "REQUEST_CALLBACK", "message": "Call tomorrow", "contact": "buyer@example.com"}
        first = self.client.post(endpoint, json=payload); second = self.client.post(endpoint, json=payload)
        self.assertEqual(first.status_code, 200)
        self.assertEqual(first.json()["request_id"], second.json()["request_id"])
        request_path = self.root / "data/proposal_requests.jsonl"
        lines = request_path.read_text().splitlines(); self.assertEqual(len(lines), 1)
        request = json.loads(lines[0]); self.assertNotIn("portal_token", request)
        private_endpoint = "/api/customer-requests/" + request["request_id"]
        self.assertEqual(self.client.get(private_endpoint).status_code, 401)
        self.assertEqual(self.client.get(private_endpoint, headers={"X-AMX-Admin": "admin-test"}).json()["message"], "Call tomorrow")
        self.assertEqual((request["opportunity_key"], request["thread_id"], request["customer_id"]), ("buyer", "thread-1", "customer-1"))
        self.assertNotIn("provider_secret", self.client.get("/api/proposals/runtime-only-token").json())
        with patch.object(runner, "REQUESTS", request_path), patch.object(runner, "CLAIMS", self.root / "overdrive/claims.json"), patch.object(runner, "SIGNALS", self.root / "overdrive/signals.json"):
            ledger = json.loads((self.root / "overdrive/opportunities.json").read_text())
            result = runner.claim_work(runner.detect_work(ledger), ledger)
            claim = result["claims"]["PRI|buyer|request|" + request["request_id"]]
            self.assertEqual(claim["status"], "READY")
            self.assertEqual(claim["required_executor"], "iSCOPE PRI Field Force")
        bad = json.loads(self.registry.read_text()); bad["proposals"]["runtime-only-token"]["thread_id"] = "wrong"
        self.registry.write_text(json.dumps(bad))
        self.assertEqual(self.client.post(endpoint, json=payload).status_code, 503)
        self.assertEqual(len(request_path.read_text().splitlines()), 1)

    def test_paid_detail_projection_cannot_repeat_internal_paid_label(self):
        record = {**receivable(), "state": "PAID", "evidence": [{"kind": "INVOICE", "source_id": "invoice"}]}
        (self.root / "overdrive/opportunities.json").write_text(json.dumps({"records": {"buyer": record}}))
        detail = self.client.get("/api/opportunities/buyer", headers={"X-AMX-Admin": "admin-test"}).json()
        self.assertEqual(detail["record"]["state"], "PAYMENT_UNVERIFIED")



if __name__ == "__main__": unittest.main()
