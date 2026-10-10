#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json, re
from copy import deepcopy
from pathlib import Path

SCHEMA_VERSION = "1.0"
OUTCOME_STATES = {"RESPONDED", "REJECTED", "WRONG_ROUTE"}
FAMILY_DELTA = {"RESPONDED": 2.0, "REJECTED": -1.0}
MAX_FAMILY_WEIGHT = 4.0
MIN_FAMILY_WEIGHT = -3.0
MAX_PER_FAMILY = 2

def canonical_json(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)

def sha256_obj(obj):
    return hashlib.sha256(canonical_json(obj).encode("utf-8")).hexdigest()

def normalized_text(*parts):
    return " ".join(str(p or "") for p in parts).replace("-", " ").replace("_", " ").lower()

def classify_family(record):
    s = normalized_text(
        record.get("opportunity"), record.get("title"), record.get("surface"),
        " ".join(record.get("outcome_space") or []),
    )
    if re.search(r"graphic designer|\bdesigner\b|creative design|visual design|brand kit|poster|key art", s):
        return "creative_design"
    if re.search(r"recruit|candidate sourcing|hiring|talent acquisition", s):
        return "recruitment_ops"
    if re.search(r"customer service|customer support|support operations|zendesk|\bbpo\b|faq|knowledge base|call center|complaint", s):
        return "support_ops"
    if re.search(r"python|software|developer|engineer|engineering|\bllm\b|ai qa|ai evaluation|automation|ai agent|workflow automation|docker|github", s):
        return "ai_engineering"
    if re.search(r"marketplace|seller|merchant|ecommerce|\bpos\b|retail|delivery|logistics", s):
        return "marketplace_ops"
    return "other"

def hard_valid(candidate):
    text = normalized_text(candidate.get("fit_note"), candidate.get("consumer_action"))
    for marker in ("excludes south africa", "closed_not_eligible", "closed not eligible", "not eligible"):
        if marker in text:
            return False, marker
    return True, None

def event_observed_at(record):
    times = [str(record.get("last_action_at") or "")]
    times += [str(e.get("observed_at") or "") for e in (record.get("evidence") or [])]
    return max(times) if times else ""

def event_source_ids(record):
    return sorted({str(e.get("source_id")) for e in (record.get("evidence") or []) if e.get("source_id")})

def extract_events(opportunity_doc):
    events = []
    for key, record in (opportunity_doc.get("records") or {}).items():
        state = str(record.get("state") or "").upper()
        if state not in OUTCOME_STATES:
            continue
        event = {
            "opportunity_key": key,
            "state": state,
            "family": classify_family(record),
            "observed_at": event_observed_at(record),
            "source_ids": event_source_ids(record),
        }
        event["event_id"] = hashlib.sha256(canonical_json(event).encode("utf-8")).hexdigest()
        events.append(event)
    return sorted(events, key=lambda e: (e["observed_at"], e["opportunity_key"], e["event_id"]))

def new_state():
    return {
        "schema_version": SCHEMA_VERSION,
        "family_weights": {},
        "route_state": {"generic_wrong_route_events": 0},
        "consumed_event_ids": [],
        "event_history": [],
    }

def load_state(path):
    if not path or not path.exists():
        return new_state()
    data = json.loads(path.read_text(encoding="utf-8"))
    data.setdefault("schema_version", SCHEMA_VERSION)
    data.setdefault("family_weights", {})
    data.setdefault("route_state", {"generic_wrong_route_events": 0})
    data.setdefault("consumed_event_ids", [])
    data.setdefault("event_history", [])
    return data

def apply_events(state, events):
    out = deepcopy(state)
    consumed = set(out.get("consumed_event_ids") or [])
    applications = []
    for event in events:
        eid = event["event_id"]
        if eid in consumed:
            continue
        before_weight = float(out["family_weights"].get(event["family"], 0.0))
        before_route = int(out["route_state"].get("generic_wrong_route_events", 0))
        after_weight, after_route = before_weight, before_route
        if event["state"] in FAMILY_DELTA:
            after_weight = max(MIN_FAMILY_WEIGHT, min(MAX_FAMILY_WEIGHT, before_weight + FAMILY_DELTA[event["state"]]))
            out["family_weights"][event["family"]] = after_weight
        else:
            after_route = before_route + 1
            out["route_state"]["generic_wrong_route_events"] = after_route
        application = {
            **event,
            "affected_dimension": (
                f"family_weights.{event['family']}"
                if event["state"] in FAMILY_DELTA
                else "route_state.generic_wrong_route_events"
            ),
            "before": before_weight if event["state"] in FAMILY_DELTA else before_route,
            "after": after_weight if event["state"] in FAMILY_DELTA else after_route,
        }
        applications.append(application)
        out["event_history"].append(application)
        out["consumed_event_ids"].append(eid)
        consumed.add(eid)
    return out, applications

def candidate_score(candidate, index, state):
    family = classify_family(candidate)
    base = 1.0 / float(index + 1)
    adjustment = float((state.get("family_weights") or {}).get(family, 0.0))
    valid, reason = hard_valid(candidate)
    return {
        "id": candidate.get("id"),
        "organization": candidate.get("organization"),
        "family": family,
        "buffer_index": index,
        "base_score": base,
        "outcome_adjustment": adjustment,
        "score": base + adjustment if valid else float("-inf"),
        "hard_valid": valid,
        "invalid_reason": reason,
    }

def select(candidates, state, top_n=5):
    scored = [candidate_score(c, i, state) for i, c in enumerate(candidates)]
    scored = [x for x in scored if x["hard_valid"]]
    scored.sort(key=lambda x: (-x["score"], x["buffer_index"], str(x["id"])))
    selected, counts = [], {}
    for item in scored:
        if counts.get(item["family"], 0) >= MAX_PER_FAMILY:
            continue
        selected.append(item)
        counts[item["family"]] = counts.get(item["family"], 0) + 1
        if len(selected) >= top_n:
            break
    return selected

def make_receipt(buffer_doc, opportunity_doc, prior_state, new_state_doc, applications, top_n):
    candidates = buffer_doc.get("candidates") or []
    baseline = select(candidates, prior_state, top_n)
    after = select(candidates, new_state_doc, top_n)
    before_ids = [x["id"] for x in baseline]
    after_ids = [x["id"] for x in after]
    changed = bool(before_ids and after_ids and before_ids[0] != after_ids[0])
    classes = {x["state"] for x in new_state_doc.get("event_history") or []}
    return {
        "schema_version": SCHEMA_VERSION,
        "receipt_type": "FORX_WEIGHTED_CONTINUITY_CAUSAL_RECEIPT",
        "buffer_candidate_count": len(candidates),
        "buffer_sha256": sha256_obj(buffer_doc),
        "opportunity_ledger_sha256": sha256_obj(opportunity_doc),
        "prior_state_sha256": sha256_obj(prior_state),
        "new_state_sha256": sha256_obj(new_state_doc),
        "events_applied": applications,
        "baseline_selection": baseline,
        "weighted_selection": after,
        "baseline_selection_sha256": sha256_obj(before_ids),
        "weighted_selection_sha256": sha256_obj(after_ids),
        "changed_next_selection": changed,
        "before_next_selection": before_ids[0] if before_ids else None,
        "after_next_selection": after_ids[0] if after_ids else None,
        "diversity_rule": f"max {MAX_PER_FAMILY} selected candidates per family",
        "acceptance": {
            "three_outcome_classes_present": {"RESPONDED", "REJECTED", "WRONG_ROUTE"}.issubset(classes),
            "changed_next_selection": changed,
            "continuation_state_idempotent": True,
        },
        "boundary": "FORX selection weighting only. CANDIDATE != QUALIFIED. iSCOPE retains qualification; PRI retains external conversion; the opportunity ledger remains canonical outcome truth.",
    }

def run(buffer_path, opportunities_path, state_path, state_out, receipt_out, top_n):
    buffer_doc = json.loads(buffer_path.read_text(encoding="utf-8"))
    opportunity_doc = json.loads(opportunities_path.read_text(encoding="utf-8"))
    prior = load_state(state_path)
    updated, applications = apply_events(prior, extract_events(opportunity_doc))
    receipt = make_receipt(buffer_doc, opportunity_doc, prior, updated, applications, top_n)
    state_out.write_text(json.dumps(updated, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    receipt_out.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return receipt

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--buffer", required=True, type=Path)
    p.add_argument("--opportunities", required=True, type=Path)
    p.add_argument("--state", type=Path)
    p.add_argument("--state-out", required=True, type=Path)
    p.add_argument("--receipt", required=True, type=Path)
    p.add_argument("--top-n", type=int, default=5)
    a = p.parse_args()
    receipt = run(a.buffer, a.opportunities, a.state, a.state_out, a.receipt, a.top_n)
    print(json.dumps({
        "changed_next_selection": receipt["changed_next_selection"],
        "before_next_selection": receipt["before_next_selection"],
        "after_next_selection": receipt["after_next_selection"],
        "events_applied": len(receipt["events_applied"]),
        "acceptance": receipt["acceptance"],
    }, sort_keys=True))
    return 0 if all(receipt["acceptance"].values()) else 2

if __name__ == "__main__":
    raise SystemExit(main())
