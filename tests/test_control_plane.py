"""Recovery and governance adversarial tests, runnable without a test plugin."""
import copy
import io
import json
import os
import sqlite3
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch

from cryptography.fernet import Fernet, InvalidToken
from fastapi import HTTPException

from backend.continuity import RecoveryStore, load_registry, canonical, digest, CHUNK, safe_health, relative
from backend.security import authorized_job, authorize, fingerprint
from backend.store import EvidenceStore
from overdrive.evidence_learning import EvidenceLearning, reference_cycle, MANDATE, WORKER, filter_opportunity
from BLACK.worker import Worker

ROOT = Path(__file__).resolve().parents[1]
GRANTS = json.loads((ROOT / "CONTINUITY/capability-grants.json").read_text())


class RecoveryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.p = Path(self.temp.name)
        self.key = self.p / "recovery.key"
        self.key.write_bytes(Fernet.generate_key())
        self.key.chmod(0o600)
        self.source = self.p / "governance.json"
        self.source.write_text('{"authority":"GOVERNED_SOURCE","payload":"private fixture evidence"}\n')
        seed = json.loads((ROOT / "CONTINUITY/source-registry.json").read_text())
        row = seed["sources"][1]
        row.update(source_id="fixture-source", source_system="local", path=str(self.source), allowed_root=str(self.p))
        self.registry_path = self.p / "registry.json"
        self.registry_path.write_text(json.dumps({**seed, "sources": [row]}))
        self.registry = load_registry(self.registry_path, ROOT)
        self.store = RecoveryStore(self.p / "encrypted", self.key, ROOT)

    def tearDown(self):
        self.temp.cleanup()

    def sync(self):
        return self.store.sync(self.registry)

    def test_offline_restore_and_authority_distinction(self):
        result = self.sync()
        expected = self.source.read_bytes()
        self.source.unlink()  # provider/source loss, no network in the restore path
        target = self.p / "restored"
        receipt = self.store.restore(target)
        self.assertTrue(receipt["compared"])
        self.assertEqual((target / "fixture-source/governance.json").read_bytes(), expected)
        marker = json.loads((target / ".amx-restoration.json").read_text())
        self.assertEqual(marker["role"], "MIRROR_RECOVERY")
        self.assertFalse(marker["automatic_authority_promotion"])
        self.assertEqual(result["snapshot"], self.store.latest_verified())

    def test_encryption_of_payload_manifests_receipts_and_observations(self):
        self.sync()
        for p in self.store.root.rglob("*.enc"):
            data = p.read_bytes()
            self.assertNotIn(b"private fixture evidence", data)
            self.assertNotIn(b"GOVERNED_SOURCE", data)
            self.assertNotIn(b"fixture-source", data)
            self.assertEqual(p.stat().st_mode & 0o077, 0)

    def test_idempotent_snapshot_and_dedup(self):
        a = self.sync(); chunks = set((self.store.root / "chunks").glob("*.enc"))
        b = self.sync()
        self.assertEqual(a["snapshot"], b["snapshot"])
        self.assertEqual(chunks, set((self.store.root / "chunks").glob("*.enc")))
        self.assertEqual(len(list((self.store.root / "snapshots").glob("*.enc"))), 1)

    def test_versions_and_prior_restore(self):
        a = self.sync()
        expected = self.source.read_bytes()
        self.source.write_bytes(b"new governed generation")
        b = self.sync()
        self.assertNotEqual(a["snapshot"], b["snapshot"])
        self.store.restore(self.p / "prior", a["snapshot"])
        self.assertEqual((self.p / "prior/fixture-source/governance.json").read_bytes(), expected)

    def test_partial_sync_does_not_replace_latest_and_preserves_observations(self):
        a = self.sync()
        self.source.unlink()
        b = self.sync()
        self.assertEqual(b["state"], "HOLD")
        self.assertFalse(b["promoted"])
        self.assertEqual(self.store.latest_verified(), a["snapshot"])
        o = self.store._read(self.store.root / "observations.enc")["sources"][0]
        self.assertIsNotNone(o["last_successful_mirror_at"])
        self.assertEqual(o["integrity_result"], "HOLD")

    def test_corrupted_chunk_is_detected_and_not_repaired_silently(self):
        self.sync()
        p = next((self.store.root / "chunks").glob("*.enc"))
        p.write_bytes(b"corruption")
        with self.assertRaises(InvalidToken):
            self.store.verify()
        self.assertEqual(self.store.health()["state"], "HOLD")
        self.assertEqual(self.store.health()["integrity_failures"], 1)
        self.assertFalse(self.sync()["promoted"])
        self.assertEqual(p.read_bytes(), b"corruption")

    def test_corrupted_manifest_rejected(self):
        a = self.sync()
        (self.store.root / "snapshots" / (a["snapshot"] + ".enc")).write_bytes(b"broken")
        with self.assertRaises(InvalidToken):
            self.store.restore(self.p / "target")
        self.assertFalse((self.p / "target").exists())

    def test_wrong_key_cannot_read(self):
        self.sync()
        other = self.p / "other.key"; other.write_bytes(Fernet.generate_key()); other.chmod(0o600)
        with self.assertRaises(InvalidToken):
            RecoveryStore(self.store.root, other, ROOT).latest_verified()

    def test_chunked_large_asset_and_dedup(self):
        content = b"x" * CHUNK + b"x" * CHUNK + b"tail"
        self.source.write_bytes(content)
        self.sync()
        self.assertEqual(len(list((self.store.root / "chunks").glob("*.enc"))), 2)
        self.store.restore(self.p / "large")
        self.assertEqual((self.p / "large/fixture-source/governance.json").read_bytes(), content)

    def test_interrupted_publication_converges_and_preserves_prior(self):
        first = self.sync()
        self.source.write_bytes(b"second generation")
        original = self.store._write
        def interrupt(path, *a, **kw):
            if path.name == "latest.enc":
                raise RuntimeError("simulated interruption")
            return original(path, *a, **kw)
        with patch.object(self.store, "_write", interrupt):
            with self.assertRaises(RuntimeError):
                self.sync()
        self.assertEqual(self.store.latest_verified(), first["snapshot"])
        self.assertTrue(self.sync()["promoted"])
        self.assertEqual(len(list((self.store.root / "snapshots").glob("*.enc"))), 2)

    def test_conflicting_sync_lock(self):
        with self.store.lock():
            with self.assertRaises(BlockingIOError):
                self.sync()

    def test_authority_hash_pin(self):
        self.registry["sources"][0]["expected_sha256"] = "0" * 64
        self.assertFalse(self.sync()["promoted"])
        with self.assertRaises(ValueError):
            load_registry(self.registry_path, ROOT, "0" * 64)

    def test_registry_rejects_plaintext_duplicate_and_unknown_adapter(self):
        for mutation in ["plaintext", "duplicate", "adapter"]:
            d = json.loads(self.registry_path.read_text())
            if mutation == "plaintext": d["sources"][0]["encryption_required"] = False
            if mutation == "duplicate": d["sources"].append(d["sources"][0])
            if mutation == "adapter": d["sources"][0]["adapter"] = "arbitrary_shell"
            self.registry_path.write_text(json.dumps(d))
            with self.assertRaises(Exception): load_registry(self.registry_path, ROOT)
            self.registry_path.write_text(json.dumps({k:v for k,v in self.registry.items() if k != "registry_sha256"}))

    def test_path_traversal_and_live_target_refused(self):
        self.sync()
        for name in ["../secrets", "/etc/passwd", "a/../../b", "a\\b", "a/./b"]:
            with self.assertRaises(ValueError): relative(name)
        with self.assertRaises(ValueError): self.store.restore(self.p)
        with self.assertRaises(ValueError): self.store.restore(ROOT / "authority-overwrite")

    def test_symlink_source_refused(self):
        target = self.p / "linked"; target.symlink_to(self.source)
        self.registry["sources"][0]["path"] = str(target)
        self.assertFalse(self.sync()["promoted"])

    def test_secret_permissions_and_key_separation(self):
        self.key.chmod(0o644)
        with self.assertRaises(PermissionError): RecoveryStore(self.p / "bad", self.key, ROOT)
        self.key.chmod(0o600)
        inside = self.store.root / "nested.key"; inside.write_bytes(Fernet.generate_key()); inside.chmod(0o600)
        with self.assertRaises(ValueError): RecoveryStore(self.store.root, inside, ROOT)

    def test_receipt_chain_detects_truncation(self):
        self.sync(); self.store.verify()
        p = sorted((self.store.root / "receipts").glob("*.enc"))[-1]; p.unlink()
        with self.assertRaises(ValueError): self.store.read_receipts()

    def test_sqlite_backup_includes_committed_state(self):
        db = self.p / "live.db"
        with sqlite3.connect(db) as con:
            con.execute("CREATE TABLE durable(value TEXT)"); con.execute("INSERT INTO durable VALUES('accepted')")
        self.registry["sources"][0].update(path=str(db), adapter="sqlite_backup", source_system="sqlite")
        self.sync(); self.store.restore(self.p / "sqlite-restore")
        with sqlite3.connect(self.p / "sqlite-restore/fixture-source/live.db") as con:
            self.assertEqual(con.execute("SELECT value FROM durable").fetchone()[0], "accepted")

    def test_no_independent_disk_claim_on_same_device(self):
        self.sync()
        with self.assertRaises(ValueError): self.store.replicate(self.p / "replica")
        self.store.replicate(self.p / "test-replica", require_independent_device=False)
        clone = RecoveryStore(self.p / "test-replica", self.key, ROOT)
        clone.restore(self.p / "from-replica")
        self.assertEqual((self.p / "from-replica/fixture-source/governance.json").read_bytes(), self.source.read_bytes())

    def test_health_staleness_and_private_fields(self):
        self.sync()
        data = self.store.health(); data["private_inventory"] = "must not expose"; data["observed_at"] = "2020-01-01T00:00:00+00:00"
        health = self.p / "health.json"; health.write_text(json.dumps(data))
        public = safe_health(health)
        self.assertEqual(public["state"], "HOLD")
        self.assertNotIn("private_inventory", public)
        self.assertEqual(safe_health(None)["state"], "HOLD")


class LearningTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(); self.p = Path(self.temp.name)
        self.learning = EvidenceLearning(EvidenceStore(self.p / "evidence.db"), copy.deepcopy(GRANTS))
        self.source = ROOT / "CONTINUITY/BOUNTY_REAPER_RUN_2026-10-02T1421_SAST.md"

    def tearDown(self): self.temp.cleanup()

    def candidate(self, changes=None):
        self.learning.outcome("test-action", "Inspect existing evidence", {"state":"HOLD"}, self.source)
        self.learning.lesson("test-lesson", "test-action", "HYPOTHESIS", "Source aliases may hide duplicates")
        return self.learning.candidate("test-candidate", "test-lesson", changes or {"normalize_source_url":True})

    def test_full_real_local_cycle_and_repeat(self):
        result = reference_cycle(ROOT, self.p / "cycle.db", GRANTS)
        self.assertEqual(result["state"], "PASS")
        self.assertEqual(result["capability"]["version"], 2)
        self.assertEqual(result["capability"]["mandate_sha256"], fingerprint(MANDATE))
        self.assertEqual(result["action_outcome"]["result"]["payout_state"], "UNPROVEN")
        self.assertEqual(reference_cycle(ROOT, self.p / "cycle.db", GRANTS)["capability"]["version"], 2)

    def test_unproven_lesson_cannot_be_promoted(self):
        self.candidate()
        with self.assertRaises(ValueError): self.learning.promote("test-candidate", 1, "Root")
        self.assertEqual(self.learning.capability()["version"], 1)

    def test_worker_cannot_test_or_promote_itself(self):
        self.candidate()
        with self.assertRaises(PermissionError): self.learning.test_candidate("test-candidate", WORKER)
        self.learning.test_candidate("test-candidate", "Critic")
        with self.assertRaises(PermissionError): self.learning.promote("test-candidate", 1, WORKER)

    def test_mandate_and_grant_changes_rejected(self):
        for changes in [{"mandate":"commercial"},{"spend_funds":True},{"max_source_age_hours":999}]:
            with self.assertRaises(ValueError): self.candidate(changes)

    def test_failed_test_cannot_promote_and_rejection_receipted(self):
        self.candidate({"max_source_age_hours":72})
        result=self.learning.test_candidate("test-candidate", "Critic")
        self.assertEqual(result["state"], "FAIL")
        with self.assertRaises(ValueError): self.learning.promote("test-candidate", 1, "Root")
        self.assertEqual(self.learning.reject("test-candidate", "No measured duplicate improvement", "Root")["state"], "PASS")

    def test_compare_and_swap_and_versioned_rollback(self):
        self.candidate(); self.learning.test_candidate("test-candidate", "Critic")
        with self.assertRaises(ValueError): self.learning.promote("test-candidate", 2, "Root")
        self.learning.promote("test-candidate", 1, "Root")
        rolled = self.learning.rollback(1,2,"Root")
        self.assertEqual(rolled["version"], 3)
        self.assertFalse(rolled["config"]["normalize_source_url"])
        self.assertEqual(rolled["mandate_sha256"],fingerprint(MANDATE))

    def test_outcome_id_conflict_and_no_source_no_lesson(self):
        self.learning.outcome("unique","inspect",{"state":"PASS"},self.source)
        with self.assertRaises(ValueError): self.learning.outcome("unique","changed",{"state":"PASS"},self.source)
        with self.assertRaises(ValueError): self.learning.lesson("absent","missing","FACT","unsupported")
        with self.assertRaises(ValueError): self.learning.lesson("proven","unique","PROVEN_IMPROVEMENT","untested")

    def test_tampered_learning_evidence_blocks_promotion(self):
        self.candidate(); self.learning.test_candidate("test-candidate", "Critic")
        with self.learning.store.connect() as con: con.execute("UPDATE amx_learning_receipts SET payload='{}' WHERE seq=1")
        with self.assertRaises((ValueError,KeyError)): self.learning.promote("test-candidate",1,"Root")


class CapabilityTests(unittest.TestCase):
    def test_drive_inventory_converges_and_preserves_lost_sources(self):
        from backend.sources import drive_inventory
        registry=json.loads((ROOT/"CONTINUITY/source-registry.json").read_text())
        records=[{"ID":"stable-provider-id","Path":"Governance.txt","ModTime":"2026-10-03T00:00:00Z"}]
        first=drive_inventory(registry,records,"amx_drive:")
        row=next(s for s in first["sources"] if s["source_id"].startswith("drive-"))
        self.assertEqual(row["authority_level"],"REFERENCE")
        self.assertEqual(row["classification_state"],"UNKNOWN")
        second=drive_inventory(registry,records,"amx_drive:",first["sources"])
        self.assertEqual(first["registry_sha256"],second["registry_sha256"])
        third=drive_inventory(registry,[{"ID":"another-id","Path":"Other.txt","ModTime":"2026-10-03T00:00:00Z"}],"amx_drive:",first["sources"])
        self.assertIn(row["source_id"],{s["source_id"] for s in third["sources"]})
        with self.assertRaises(ValueError):drive_inventory(registry,[],"amx_drive:",first["sources"])

    def test_asset_provider_output_cannot_become_market_master(self):
        from backend.assets import asset_eligibility
        asset={"asset_id":"reference-one","project":"DRAGON","lifecycle_class":"PROVIDER_OUTPUT_QUARANTINE","provider_rendered":True,"watermark_or_branding":True,"rights_state":"ACCEPTED","rights_receipt":"source","critic_receipt":"critic","carbon_rebuild_receipt":"rebuild"}
        result=asset_eligibility(asset)
        self.assertFalse(result["market_master_eligible"])
        self.assertFalse(result["automatic_canon_promotion"])
        self.assertTrue(result["attribution_must_be_preserved"])

    def test_deny_default_and_exact_command_grant(self):
        command=["/bin/true"]
        with self.assertRaises(PermissionError): authorized_job({"command":command},GRANTS)
        grants=copy.deepcopy(GRANTS)
        grants["grants"].append({"grant_id":"bounded-test","worker_id":"BLACK","capability":"execute_shell","scopes":[fingerprint(command)],"state":"ACTIVE","authority_receipt":"local test fixture"})
        self.assertEqual(authorized_job({"command":command},grants)["adapter"],"scoped_command")
        with self.assertRaises(PermissionError): authorized_job({"command":["/bin/sh","-c","true"]},grants)
        with self.assertRaises(PermissionError): authorize(grants,"BLACK","sign_transactions","all")

    def test_credential_and_network_grants_are_required(self):
        for capability in ["access_credentials", "access_network", "read_private_assets"]:
            grants=copy.deepcopy(GRANTS)
            grants['grants']=[g for g in grants['grants'] if g['capability']!=capability]
            with self.assertRaises(PermissionError):authorized_job({'adapter':'continuity_sync'},grants)

    def test_worker_no_secret_output_duplicate_or_job_reuse(self):
        with tempfile.TemporaryDirectory() as t:
            calls=[]
            worker=Worker(Path(t)/"state",GRANTS,lambda job,auth: calls.append(job) or {"exit_code":0,"result":{"state":"PASS"}},lambda r:True)
            job={"worker":"BLACK","adapter":"continuity_verify"}
            worker.process("job-one",job); worker.process("job-one",job)
            self.assertEqual(len(calls),1)
            self.assertEqual(worker.flush_outbox(),1)
            with self.assertRaises(ValueError): worker.process("job-one",{**job,"adapter":"continuity_sync"})
            hold=worker.process("legacy-command",{"command":["/bin/sh","-c","echo private"]})
            self.assertEqual(hold["state"],"HOLD")
            self.assertNotIn("stdout",hold)
            self.assertEqual(len(calls),1)

    def test_interrupted_command_not_replayed(self):
        with tempfile.TemporaryDirectory() as t:
            worker=Worker(Path(t)/"state",GRANTS,lambda *x:self.fail("must not execute"),lambda r:True)
            job={"command":["/bin/true"]}
            journal=worker.state/"journal/sensitive.json"
            journal.write_text(json.dumps({"state":"RUNNING","adapter":"scoped_command","attempt":1,"job_sha256":fingerprint(job)}))
            r=worker.process("sensitive",job)
            self.assertEqual(r["reason"],"INTERRUPTED_CONSEQUENTIAL_COMMAND_REQUIRES_RECONCILIATION")
            self.assertEqual(worker.flush_outbox(), 1)

    def test_installer_preserves_enrollment_and_scopes_refresh_writes(self):
        import subprocess
        with tempfile.TemporaryDirectory() as t:
            stage=Path(t)/"staged"
            command=["bash",str(ROOT/"BLACK/install-continuity.sh"),"--stage",str(stage)]
            subprocess.run(command,check=True,capture_output=True,timeout=20)
            config=stage/"etc/amx-black-continuity"
            env=config/"environment"
            env.write_text(env.read_text()+"AMX_DRIVE_DISCOVERY_REMOTE=approved_scope:matrix\n")
            grants=config/"grants.json"
            policy=json.loads(grants.read_text());policy["preserved_test_scope"]=True
            grants.write_text(json.dumps(policy));grants.chmod(0o600)
            subprocess.run(command,check=True,capture_output=True,timeout=20)
            self.assertIn("AMX_DRIVE_DISCOVERY_REMOTE=approved_scope:matrix",env.read_text())
            self.assertTrue(json.loads(grants.read_text())["preserved_test_scope"])
            self.assertIn("BLACK_GRANTS_SHA256="+digest(grants.read_bytes()),env.read_text())
            self.assertEqual(env.stat().st_mode & 0o077,0)
            unit=(stage/"etc/systemd/system/amx-black-continuity.service").read_text()
            writes=next(line for line in unit.splitlines() if line.startswith("ReadWritePaths="))
            self.assertIn("/var/lib/amx-black-credentials",writes)
            self.assertNotIn("/etc/amx-black-continuity",writes)

    def test_existing_house_reports_unenrolled_hold(self):
        from backend.state import aggregate_state
        with patch.dict(os.environ,{"AMX_GITHUB_REPO":""},clear=False):
            self.assertEqual(aggregate_state(ROOT)["continuity"]["state"],"HOLD")

    def test_private_versions_and_separate_role_credentials(self):
        from backend.app import create_app
        with tempfile.TemporaryDirectory() as t:
            app=create_app(ROOT,Path(t)/"db")
            record=dict(app.state.store.list()[0]);record.update(evidence_id="privacy-regression",visibility="PRIVATE")
            app.state.store.upsert(record)
            record.update(visibility="HOUSE");app.state.store.upsert(record)
            route=next(r for r in app.routes if getattr(r,"path",None)=="/api/evidence/{evidence_id}/versions")
            self.assertEqual(route.endpoint("privacy-regression")["count"],0)
            record.update(visibility="SECRET");app.state.store.upsert(record)
            with self.assertRaises(HTTPException): route.endpoint("privacy-regression")
            promote=next(r for r in app.routes if getattr(r,"path",None).endswith("/promote") if getattr(r,"path",None))
            auth=promote.dependant.dependencies[0].call
            with patch.dict(os.environ,{"AMX_LEARNING_DURABLE_STORAGE":"accepted","AMX_ROOT_TOKEN":"root-test","AMX_REAPER_TOKEN":"reaper-test"}):
                with self.assertRaises(HTTPException): auth("reaper-test")
                auth("root-test")
            with patch.dict(os.environ,{"AMX_LEARNING_DURABLE_STORAGE":"accepted","AMX_ROOT_TOKEN":"shared-test","AMX_REAPER_TOKEN":"shared-test"}):
                with self.assertRaises(HTTPException) as denied: auth("shared-test")
                self.assertEqual(denied.exception.status_code,503)


if __name__ == "__main__":
    unittest.main()
