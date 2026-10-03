"""Evidence learning for existing workers; no daemon, submission or mandate change.

The reference adapter belongs to Bounty Reaper, independent of commercial routing.
EvidenceStore supplies the existing SQLite transaction/backup boundary.
"""
from __future__ import annotations

import hashlib
import json
import re
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit

from backend.security import authorize, fingerprint
from backend.store import EvidenceStore, canonical_json, utcnow

WORKER = "Bounty Reaper"
MANDATE = "Independent crypto-centric bounty/reward evidence and authorized execution; no iSCOPE/PRI subordination; no payout without evidence."
KINDS = {"FACT", "HYPOTHESIS", "HEURISTIC", "FAILURE_MODE", "PROVEN_IMPROVEMENT"}
BASE_CONFIG = {"max_source_age_hours": 168, "normalize_source_url": False}


def source_key(url: str, normalize: bool) -> str:
    p = urlsplit(url)
    if p.scheme not in {"http", "https"} or not p.hostname or p.username or p.password:
        raise ValueError("INVALID_PUBLIC_SOURCE_URL")
    if not normalize:
        return url
    # URL paths/query are case-sensitive; only scheme/host and fragments normalize.
    host = p.hostname.lower()
    port = p.port
    if port and not (p.scheme == "https" and port == 443 or p.scheme == "http" and port == 80):
        host += ":" + str(port)
    return urlunsplit((p.scheme.lower(), host, p.path or "/", p.query, ""))


def filter_opportunity(item: dict, config: dict, seen: set[str], at: datetime) -> dict:
    """Bounded filtering only. Every rejected/held capability remains attributable."""
    key = fingerprint({"source": source_key(item["source_url"], config["normalize_source_url"]),
                       "opportunity_id": item["opportunity_id"]})
    result = {"opportunity_id": item["opportunity_id"], "worker_id": WORKER,
              "mandate_sha256": fingerprint(MANDATE), "payout_state": "UNPROVEN",
              "external_action": "NONE", "state": "HOLD", "reason": "UNKNOWN_FIT"}
    if item.get("payout_receipt_sha256"):
        # A supplied digest alone cannot establish a payment, even during learning.
        result["payout_state"] = "PAYMENT_EVIDENCE_REQUIRES_READBACK"
    if key in seen:
        result.update(state="REJECT", reason="DUPLICATE_SOURCE")
        return result
    if item.get("domain") != "crypto" or not item.get("chain_protocol"):
        result["reason"] = "MANDATE_FIT_NOT_PROVEN_PRESERVE_SOURCE"
        return result
    if item.get("pay_to_work"):
        result.update(state="REJECT", reason="PAY_TO_WORK")
        return result
    observed = datetime.fromisoformat(item["observed_at"].replace("Z", "+00:00"))
    age = (at - observed).total_seconds() / 3600
    if age < 0 or age > config["max_source_age_hours"]:
        result["reason"] = "STALE_OR_FUTURE_SOURCE_REVALIDATE"
        return result
    if item.get("security_work") and (not item.get("authorized_scope_sha256") or not item.get("safe_harbor_source")):
        result["reason"] = "LAWFUL_SECURITY_SCOPE_REQUIRED"
        return result
    if item.get("technical_fit") != "EVIDENCED" or item.get("reward_economics") != "EVIDENCED":
        result["reason"] = "TECHNICAL_OR_ECONOMIC_FIT_REQUIRED"
        return result
    seen.add(key)
    result.update(state="QUALIFIED_FOR_REAPER_REVIEW", reason="BOUNDED_FILTER_PASS")
    return result


class EvidenceLearning:
    def __init__(self, store: EvidenceStore, grants: dict):
        self.store = store
        self.grants = grants
        with store.connect() as con:
            con.executescript("""
              CREATE TABLE IF NOT EXISTS amx_learning_receipts(seq INTEGER PRIMARY KEY, digest TEXT UNIQUE NOT NULL, payload TEXT NOT NULL);
              CREATE TABLE IF NOT EXISTS amx_outcomes(id TEXT PRIMARY KEY, worker TEXT NOT NULL, digest TEXT NOT NULL, payload TEXT NOT NULL);
              CREATE TABLE IF NOT EXISTS amx_lessons(id TEXT PRIMARY KEY, worker TEXT NOT NULL, kind TEXT NOT NULL, outcome_id TEXT NOT NULL, payload TEXT NOT NULL);
              CREATE TABLE IF NOT EXISTS amx_candidates(id TEXT PRIMARY KEY, worker TEXT NOT NULL, base_version INTEGER NOT NULL, changes TEXT NOT NULL, lesson_id TEXT NOT NULL, state TEXT NOT NULL, test_receipt TEXT);
              CREATE TABLE IF NOT EXISTS amx_capabilities(worker TEXT PRIMARY KEY, version INTEGER NOT NULL, mandate_hash TEXT NOT NULL, payload TEXT NOT NULL);
              CREATE TABLE IF NOT EXISTS amx_capability_versions(worker TEXT NOT NULL, version INTEGER NOT NULL, payload TEXT NOT NULL, receipt TEXT NOT NULL, PRIMARY KEY(worker,version));
            """)
            if not con.execute("SELECT 1 FROM amx_capabilities WHERE worker=?", (WORKER,)).fetchone():
                record = {"schema": "AMX.WORKER.CAPABILITY.v1", "worker_id": WORKER,
                    "mandate": MANDATE, "mandate_sha256": fingerprint(MANDATE),
                    "owned_scope": ["crypto bounty/reward"], "version": 1,
                    "current_capabilities": ["bounded evidence filtering", "governed learning"],
                    "config": BASE_CONFIG, "successful_actions": [], "failed_actions": [],
                    "failure_classes": [], "known_constraints": ["no live target execution", "no payout inference", "no submission/spend/signing grant", "original v0.2.0 package custody unresolved"],
                    "tested_improvements": [], "rejected_improvements": [], "competency_evidence": [],
                    "last_verified_version": None, "last_material_receipt": None,
                    "next_justified_experiment": "Normalize public source identity without weakening scope checks."}
                con.execute("INSERT INTO amx_capabilities VALUES(?,?,?,?)", (WORKER, 1, fingerprint(MANDATE), canonical_json(record)))
                r = self._receipt(con, "CAPABILITY_REGISTER", "PASS", {"worker": WORKER, "mandate_sha256": fingerprint(MANDATE)})
                con.execute("INSERT INTO amx_capability_versions VALUES(?,?,?,?)", (WORKER,1,canonical_json(record),r["sha256"]))

    @staticmethod
    def _receipt(con: sqlite3.Connection, action: str, state: str, evidence: dict) -> dict:
        old = con.execute("SELECT seq,digest FROM amx_learning_receipts ORDER BY seq DESC LIMIT 1").fetchone()
        body = {"schema": "AMX.LEARNING.RECEIPT.v1", "sequence": old[0]+1 if old else 1,
                "previous_sha256": old[1] if old else None, "action": action, "state": state,
                "at": utcnow(), "evidence": evidence}
        h = fingerprint(body)
        con.execute("INSERT INTO amx_learning_receipts VALUES(?,?,?)", (body["sequence"],h,canonical_json(body)))
        return {**body, "sha256": h}

    def receipts(self) -> list[dict]:
        with self.store.connect() as con:
            rows = con.execute("SELECT digest,payload FROM amx_learning_receipts ORDER BY seq").fetchall()
        chain = []
        for h, raw in rows:
            body = json.loads(raw)
            if fingerprint(body) != h or body["sequence"] != len(chain)+1 or body["previous_sha256"] != (chain[-1]["sha256"] if chain else None):
                raise ValueError("LEARNING_RECEIPT_CHAIN_CORRUPT")
            chain.append({**body, "sha256": h})
        return chain

    def capability(self) -> dict:
        with self.store.connect() as con:
            r = con.execute("SELECT payload FROM amx_capabilities WHERE worker=?",(WORKER,)).fetchone()
            return json.loads(r[0])

    def outcome(self, outcome_id: str, action: str, result: dict, source: Path, worker: str = WORKER) -> dict:
        authorize(self.grants, worker, "write_receipts", "bounty-learning")
        if worker != WORKER or not re.fullmatch(r"[A-Za-z0-9_-]{1,100}", outcome_id):
            raise ValueError("INVALID_WORKER_OR_OUTCOME")
        body = {"outcome_id": outcome_id, "worker_id": worker, "action": action,
                "result": result, "source_reference": source.name, "source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
                "mandate_sha256": fingerprint(MANDATE), "classification": "FACT"}
        h = fingerprint(body)
        with self.store.connect() as con:
            old = con.execute("SELECT digest,payload FROM amx_outcomes WHERE id=?",(outcome_id,)).fetchone()
            if old:
                if old[0] != h:
                    raise ValueError("OUTCOME_ID_CONFLICT")
                return json.loads(old[1])
            r = self._receipt(con,"ACTION_OUTCOME","PASS",body)
            body["receipt_sha256"] = r["sha256"]
            con.execute("INSERT INTO amx_outcomes VALUES(?,?,?,?)",(outcome_id,worker,h,canonical_json(body)))
            return body

    def lesson(self, lesson_id: str, outcome_id: str, kind: str, statement: str) -> dict:
        if kind not in KINDS or kind == "PROVEN_IMPROVEMENT":
            raise ValueError("PROVEN_IMPROVEMENT_REQUIRES_TESTED_PROMOTION")
        with self.store.connect() as con:
            row = con.execute("SELECT payload FROM amx_outcomes WHERE id=?",(outcome_id,)).fetchone()
            if not row:
                raise ValueError("NO_RECEIPT_NO_LESSON")
            body = {"lesson_id":lesson_id,"worker_id":WORKER,"kind":kind,"statement":statement,
                    "outcome_id":outcome_id,"outcome_receipt":json.loads(row[0])["receipt_sha256"]}
            old = con.execute("SELECT payload FROM amx_lessons WHERE id=?",(lesson_id,)).fetchone()
            if old:
                if json.loads(old[0]) != body:
                    raise ValueError("LESSON_ID_CONFLICT")
                return body
            con.execute("INSERT INTO amx_lessons VALUES(?,?,?,?,?)",(lesson_id,WORKER,kind,outcome_id,canonical_json(body)))
            self._receipt(con,"LESSON","PASS",body)
            return body

    def candidate(self, candidate_id: str, lesson_id: str, changes: dict) -> dict:
        if not changes or not set(changes) <= set(BASE_CONFIG):
            raise ValueError("CANDIDATE_CANNOT_ALTER_MANDATE_OR_GRANTS")
        current = self.capability()
        config = {**current["config"], **changes}
        if type(config["max_source_age_hours"]) is not int or not 1 <= config["max_source_age_hours"] <= 168 or type(config["normalize_source_url"]) is not bool:
            raise ValueError("CANDIDATE_CONFIG_OUTSIDE_GOVERNED_BOUNDS")
        with self.store.connect() as con:
            if not con.execute("SELECT 1 FROM amx_lessons WHERE id=?",(lesson_id,)).fetchone():
                raise ValueError("LESSON_REQUIRED")
            old = con.execute("SELECT base_version,changes,lesson_id FROM amx_candidates WHERE id=?",(candidate_id,)).fetchone()
            if old:
                if old[1] != canonical_json(changes) or old[2] != lesson_id:
                    raise ValueError("CANDIDATE_ID_CONFLICT")
                return {"candidate_id":candidate_id,"state":"ALREADY_RECORDED"}
            con.execute("INSERT INTO amx_candidates VALUES(?,?,?,?,?,?,?)",(candidate_id,WORKER,current["version"],canonical_json(changes),lesson_id,"PROPOSED",None))
            self._receipt(con,"CANDIDATE","HOLD",{"candidate_id":candidate_id,"base_version":current["version"],"changes":changes})
            return {"candidate_id":candidate_id,"state":"PROPOSED"}

    def test_candidate(self, candidate_id: str, actor: str) -> dict:
        authorize(self.grants,actor,"read_governance","bounty-learning-test")
        with self.store.connect() as con:
            row = con.execute("SELECT * FROM amx_candidates WHERE id=?",(candidate_id,)).fetchone()
            if not row or row[5] not in {"PROPOSED","TESTED_PASS","TESTED_FAIL"}:
                raise ValueError("CANDIDATE_NOT_TESTABLE")
            current = self.capability()
            if row[2] != current["version"]:
                raise ValueError("STALE_CANDIDATE_REBASE_REQUIRED")
            config = {**current["config"], **json.loads(row[3])}
            at = datetime(2026,10,3,12,tzinfo=timezone.utc)
            base = {"opportunity_id":"CRITIC-PUBLIC-FIXTURE", "source_url":"https://example.org/bounty",
                    "observed_at":"2026-10-03T11:00:00Z","domain":"crypto","chain_protocol":"EVM",
                    "security_work":True,"authorized_scope_sha256":"a"*64,"safe_harbor_source":"governed-public-scope",
                    "technical_fit":"EVIDENCED","reward_economics":"EVIDENCED"}
            first = filter_opportunity(base,config,set(),at)
            checks = {"lawful_fresh_fit_preserved":first["state"]=="QUALIFIED_FOR_REAPER_REVIEW",
                "noncrypto_cannot_route_or_qualify":filter_opportunity({**base,"domain":"commercial"},config,set(),at)["state"]=="HOLD",
                "scope_required":filter_opportunity({**base,"authorized_scope_sha256":None},config,set(),at)["state"]=="HOLD",
                "stale_held":filter_opportunity({**base,"observed_at":"2026-09-01T00:00:00Z"},config,set(),at)["state"]=="HOLD",
                "no_payout_inference":filter_opportunity({**base,"payout_receipt_sha256":"b"*64},config,set(),at)["payout_state"]!="PAID"}
            seen = set()
            filter_opportunity(base,config,seen,at)
            duplicate = filter_opportunity({**base,"source_url":"https://EXAMPLE.org/bounty#overview"},config,seen,at)
            checks["source_alias_duplicate_detected"] = duplicate["state"]=="REJECT"
            checks["case_sensitive_paths_preserved"] = source_key("https://example.org/Bounty", True)!=source_key(base["source_url"],True)
            checks["mandate_unchanged"] = current["mandate_sha256"]==fingerprint(MANDATE)
            passed = all(checks.values())
            r = self._receipt(con,"CRITIC_TEST","PASS" if passed else "FAIL",{"candidate_id":candidate_id,"checks":checks,"test_suite":"bounty-filter-invariants-v1","config_sha256":fingerprint(config),"actor":actor})
            con.execute("UPDATE amx_candidates SET state=?,test_receipt=? WHERE id=?",("TESTED_PASS" if passed else "TESTED_FAIL",r["sha256"],candidate_id))
            return {"state":"PASS" if passed else "FAIL","checks":checks,"receipt_sha256":r["sha256"]}

    def promote(self, candidate_id: str, expected_version: int, actor: str) -> dict:
        authorize(self.grants,actor,"write_governance","bounty-learning-promotion")
        self.receipts()  # reject tampered evidence, not just an ACCEPT label
        with self.store.connect() as con:
            con.execute("BEGIN IMMEDIATE")
            row = con.execute("SELECT * FROM amx_candidates WHERE id=?",(candidate_id,)).fetchone()
            cap = con.execute("SELECT version,mandate_hash,payload FROM amx_capabilities WHERE worker=?",(WORKER,)).fetchone()
            if not row or row[5] != "TESTED_PASS" or not row[6]:
                raise ValueError("UNTESTED_LESSON_CANNOT_BECOME_RULE")
            if cap[0] != expected_version or row[2] != expected_version:
                raise ValueError("CAPABILITY_VERSION_CONFLICT")
            if cap[1] != fingerprint(MANDATE):
                raise ValueError("MANDATE_DRIFT")
            test = con.execute("SELECT payload FROM amx_learning_receipts WHERE digest=?",(row[6],)).fetchone()
            body = json.loads(test[0]) if test else {}
            record = json.loads(cap[2]); config = {**record["config"], **json.loads(row[3])}
            if body.get("action") != "CRITIC_TEST" or body.get("state") != "PASS" or body.get("evidence",{}).get("config_sha256") != fingerprint(config):
                raise ValueError("TEST_ATTRIBUTION_MISMATCH")
            r = self._receipt(con,"VERSIONED_PROMOTION","PASS",{"candidate_id":candidate_id,"worker":WORKER,"from":expected_version,"to":expected_version+1,"actor":actor,"test_receipt":row[6],"classification":"PROVEN_IMPROVEMENT","mandate_sha256":cap[1]})
            record.update(version=expected_version+1,config=config,last_verified_version=expected_version+1,last_material_receipt=r["sha256"])
            record["tested_improvements"].append({"candidate_id":candidate_id,"test_receipt":row[6],"promotion_receipt":r["sha256"]})
            record["competency_evidence"].append(row[6])
            con.execute("UPDATE amx_capabilities SET version=?,payload=? WHERE worker=?",(record["version"],canonical_json(record),WORKER))
            con.execute("INSERT INTO amx_capability_versions VALUES(?,?,?,?)",(WORKER,record["version"],canonical_json(record),r["sha256"]))
            con.execute("UPDATE amx_candidates SET state='ACCEPTED' WHERE id=?",(candidate_id,))
            return record

    def reject(self, candidate_id: str, reason: str, actor: str) -> dict:
        authorize(self.grants,actor,"write_governance","bounty-learning-promotion")
        with self.store.connect() as con:
            row = con.execute("SELECT state FROM amx_candidates WHERE id=?",(candidate_id,)).fetchone()
            if not row or row[0] == "ACCEPTED":
                raise ValueError("ACCEPTED_CHANGE_REQUIRES_VERSIONED_ROLLBACK")
            r = self._receipt(con,"CANDIDATE_REJECT","PASS",{"candidate_id":candidate_id,"reason":reason,"actor":actor})
            con.execute("UPDATE amx_candidates SET state='REJECTED' WHERE id=?",(candidate_id,))
            return r

    def rollback(self, to_version: int, expected_version: int, actor: str) -> dict:
        authorize(self.grants,actor,"write_governance","bounty-learning-promotion")
        self.receipts()
        with self.store.connect() as con:
            con.execute("BEGIN IMMEDIATE")
            current = con.execute("SELECT version,mandate_hash,payload FROM amx_capabilities WHERE worker=?",(WORKER,)).fetchone()
            old = con.execute("SELECT payload FROM amx_capability_versions WHERE worker=? AND version=?",(WORKER,to_version)).fetchone()
            if not old or current[0] != expected_version:
                raise ValueError("ROLLBACK_VERSION_CONFLICT")
            record = json.loads(current[2]); previous = json.loads(old[0])
            if previous["mandate_sha256"] != current[1]:
                raise ValueError("ROLLBACK_MANDATE_DRIFT")
            r = self._receipt(con,"VERSIONED_ROLLBACK","PASS",{"to_prior_version":to_version,"new_version":expected_version+1,"actor":actor})
            record.update(config=previous["config"],version=expected_version+1,last_material_receipt=r["sha256"],last_verified_version=None)
            con.execute("UPDATE amx_capabilities SET version=?,payload=? WHERE worker=?",(record["version"],canonical_json(record),WORKER))
            con.execute("INSERT INTO amx_capability_versions VALUES(?,?,?,?)",(WORKER,record["version"],canonical_json(record),r["sha256"]))
            return record


def reference_cycle(repo: Path, db: Path, grants: dict) -> dict:
    """Run a real local evidence audit, then test a bounded filtering improvement.

    The source is an existing durable Reaper run. Critic edge cases are fixtures,
    explicitly distinct from an actual bounty submission/acceptance/payment.
    """
    learning = EvidenceLearning(EvidenceStore(db), grants)
    if learning.capability()["version"] > 1:
        return {"state":"PASS","idempotent":True,"capability":learning.capability(),"receipts":learning.receipts()}
    source = repo / "CONTINUITY/BOUNTY_REAPER_RUN_2026-10-02T1421_SAST.md"
    text = source.read_text()
    urls = re.findall(r"https://www\.opentrain\.ai/[^\s]+", text)
    if not urls:
        raise ValueError("REFERENCE_SOURCE_NOT_RECOVERED")
    item = {"opportunity_id":"BR-20261002-019","source_url":urls[0],
            "observed_at":"2026-10-02T12:21:00Z","domain":"commercial","chain_protocol":None}
    result = filter_opportunity(item,learning.capability()["config"],set(),datetime.now(timezone.utc))
    action = learning.outcome("BR-LOCAL-MANDATE-AUDIT-20261003","Audit existing specialist outcome against current independent crypto mandate",result,source)
    learning.lesson("BR-SOURCE-IDENTITY-LESSON-v1",action["outcome_id"],"HYPOTHESIS","Normalize public source references to improve duplicate detection, while keeping non-crypto evidence on explicit scope HOLD.")
    learning.candidate("BR-SOURCE-IDENTITY-v1","BR-SOURCE-IDENTITY-LESSON-v1",{"normalize_source_url":True})
    test = learning.test_candidate("BR-SOURCE-IDENTITY-v1", "Critic")
    if test["state"] != "PASS":
        learning.reject("BR-SOURCE-IDENTITY-v1","Critic invariants failed", "Root")
        return {"state":"FAIL","test":test,"receipts":learning.receipts()}
    cap = learning.promote("BR-SOURCE-IDENTITY-v1",1, "Root")
    return {"state":"PASS","action_outcome":action,"test":test,"capability":cap,
            "receipts":learning.receipts(),"execution_scope":"LOCAL_EVIDENCE_AUDIT_AND_FILTER_TEST; LIVE_RUNTIME_NOT_CLAIMED"}
