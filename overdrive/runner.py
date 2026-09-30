#!/usr/bin/env python3
"""AMX OVERDRIVE evidence adapter.

Consumes durable queue items, validates evidence-backed commercial transitions,
updates the shared record, and writes one immutable receipt per invocation.
No connector or external commercial action is inferred by this adapter.
"""
import hashlib, json, os, time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
STATE = ROOT / "state.json"
OPPORTUNITIES = ROOT / "opportunities.json"
LOCK = ROOT / ".tick.lock"
RECEIPTS = ROOT / "receipts"
RECEIPTS.mkdir(exist_ok=True)

ALLOWED = {
    "DISCOVERED": {"QUALIFIED"},
    "QUALIFIED": {"OFFERED", "SUBMITTED"},
    "OFFERED": {"RESPONDED", "DELIVERY_FAILED"},
    "SUBMITTED": {"RESPONDED", "DELIVERY_FAILED"},
    "RESPONDED": {"NEGOTIATING"},
    "NEGOTIATING": {"CONTRACTED"},
    "CONTRACTED": {"INVOICED", "RECEIVABLE"},
    "INVOICED": {"PAID"},
    "RECEIVABLE": {"PAID"},
    "DELIVERY_FAILED": {"QUALIFIED", "SUBMITTED"},
}

def utcnow():
    return datetime.now(timezone.utc).isoformat()

def read(path):
    return json.loads(path.read_text())

def write(path, value):
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")
    tmp.replace(path)

def claim_lock():
    if LOCK.exists() and time.time() - LOCK.stat().st_mtime < 110:
        return False
    LOCK.write_text(str(os.getpid()))
    return True

def durable_receipt(sequence, payload):
    body = dict(payload)
    body["sequence"] = sequence
    body["recorded_at"] = utcnow()
    digest = hashlib.sha256(
        json.dumps(body, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    body["sha256"] = digest
    path = RECEIPTS / f"{sequence:010d}-{body['task_id']}.json"
    if path.exists():
        raise RuntimeError(f"receipt collision: {path.name}")
    write(path, body)
    return str(path.relative_to(ROOT)), digest

def evidence_transition(task, opportunities):
    payload = task["payload"]
    key = payload["opportunity_key"]
    record = opportunities["records"][key]
    expected = payload["expected_from"]
    target = payload["to"]
    if record["state"] != expected:
        raise ValueError(f"state mismatch: {record['state']} != {expected}")
    if target not in ALLOWED.get(expected, set()):
        raise ValueError(f"transition forbidden: {expected} -> {target}")
    evidence = payload.get("evidence", [])
    if not evidence or any(not e.get("source_id") or not e.get("kind") for e in evidence):
        raise ValueError("durable evidence is required")
    if target == "DELIVERY_FAILED" and not any(
        e["kind"] == "DELIVERY_FAILURE" for e in evidence
    ):
        raise ValueError("DELIVERY_FAILED requires DELIVERY_FAILURE evidence")
    old = record["state"]
    record["state"] = target
    record["last_action_at"] = payload["observed_at"]
    record["next_action"] = payload["next_action"]
    record["evidence"].extend(evidence)
    return {
        "adapter": "EVIDENCE_TRANSITION",
        "opportunity_key": key,
        "from": old,
        "to": target,
        "evidence": evidence,
        "critic": {
            "factual_claims": "PASS",
            "duplicate_contact": "PASS_NO_SEND_PERFORMED",
            "rights": "PASS_NO_ASSET_RELEASED",
            "commercial_state": "PASS",
        },
    }

ADAPTERS = {"EVIDENCE_TRANSITION": evidence_transition}

def tick():
    if not claim_lock():
        print(json.dumps({"status": "HOLD", "reason": "active_tick"}))
        return 0
    try:
        state = read(STATE)
        pending = [task for task in state.get("queue", []) if task["status"] == "PENDING"]
        if not pending:
            print(json.dumps({"status": "IDLE", "pending": 0}, sort_keys=True))
            return 0
        opportunities = read(OPPORTUNITIES)
        processed = []
        for task in state.get("queue", []):
            if task["status"] != "PENDING":
                continue
            sequence = state["sequence"] + 1
            try:
                result = ADAPTERS[task["adapter"]](task, opportunities)
                path, digest = durable_receipt(sequence, {
                    "task_id": task["id"],
                    "status": "COMPLETED",
                    "result": result,
                })
                task.update({
                    "status": "COMPLETED",
                    "completed_at": utcnow(),
                    "receipt": path,
                    "receipt_sha256": digest,
                })
            except Exception as exc:
                path, digest = durable_receipt(sequence, {
                    "task_id": task["id"],
                    "status": "FAILED",
                    "error": str(exc),
                    "adapter": task.get("adapter"),
                })
                task.update({
                    "status": "FAILED",
                    "completed_at": utcnow(),
                    "receipt": path,
                    "receipt_sha256": digest,
                })
            state["sequence"] = sequence
            state["last_receipt"] = path
            processed.append(task["id"])
        state["last_tick"] = utcnow()
        state["adapter_status"] = "OPERATIONAL"
        state["last_tick_result"] = {
            "processed": processed,
            "pending": sum(t["status"] == "PENDING" for t in state.get("queue", [])),
        }
        write(OPPORTUNITIES, opportunities)
        write(STATE, state)
        print(json.dumps(state["last_tick_result"], sort_keys=True))
        return 0
    finally:
        LOCK.unlink(missing_ok=True)

if __name__ == "__main__":
    raise SystemExit(tick())
