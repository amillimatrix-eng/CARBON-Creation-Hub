#!/usr/bin/env python3
"""AMX OVERDRIVE evidence adapter.

Consumes durable queue items, validates evidence-backed commercial transitions,
updates the shared record, and writes one immutable receipt per invocation.
No connector or external commercial action is inferred by this adapter.
"""
import fcntl, hashlib, json, os, subprocess, time
from datetime import datetime, timezone
from pathlib import Path

try:
    from overdrive.payment_truth import payment_state, verified_payment
    from overdrive.payment_verifier import attest_stripe_settlement
except ImportError:  # Existing direct script/service entry point.
    from payment_truth import payment_state, verified_payment
    from payment_verifier import attest_stripe_settlement

ROOT = Path(__file__).resolve().parent
STATE = ROOT / "state.json"
OPPORTUNITIES = ROOT / "opportunities.json"
LOCK = ROOT / ".tick.lock"
RECEIPTS = ROOT / "receipts"
SIGNALS = ROOT / "signals.json"
CLAIMS = ROOT / "claims.json"
REQUESTS = Path(os.getenv("AMX_CUSTOMER_REQUEST_PATH", str(ROOT.parent / "data/proposal_requests.jsonl")))
RECEIPTS.mkdir(exist_ok=True)

ALLOWED = {
    "DISCOVERED": {"QUALIFIED"},
    "QUALIFIED": {"OFFERED", "SUBMITTED", "WRONG_ROUTE", "NO_CONTACT"},
    "OFFERED": {"RESPONDED", "DELAYED", "DELIVERY_FAILED", "REJECTED", "WRONG_ROUTE", "NO_CONTACT"},
    "SUBMITTED": {"RESPONDED", "DELAYED", "DELIVERY_FAILED", "REJECTED", "WRONG_ROUTE", "NO_CONTACT"},
    "RESPONDED": {"ACCEPTED", "NEGOTIATING", "REJECTED", "WRONG_ROUTE", "NO_CONTACT"},
    "ACCEPTED": {"CONTRACTED", "NO_CONTACT"},
    "NEGOTIATING": {"ACCEPTED", "CONTRACTED", "REJECTED", "WRONG_ROUTE", "NO_CONTACT"},
    "CONTRACTED": {"INVOICED", "RECEIVABLE"},
    "INVOICED": {"PAID"},
    "RECEIVABLE": {"PAID"},
    "DELAYED": {"SUBMITTED", "DELIVERY_FAILED", "WRONG_ROUTE", "NO_CONTACT"},
    "DELIVERY_FAILED": {"QUALIFIED", "SUBMITTED", "WRONG_ROUTE", "NO_CONTACT"},
    "WRONG_ROUTE": {"QUALIFIED", "SUBMITTED", "NO_CONTACT"},
}

EVIDENCE_KIND_GATES = {
    "RESPONDED": {"BUYER_RESPONSE", "BUYER_REFERRAL"},
    "REJECTED": {
        "BUYER_REJECTION",
        "PLATFORM_REJECTION",
        "APPLICATION_REJECTION",
        "OFFER_REJECTION",
    },
    "WRONG_ROUTE": {
        "WRONG_ROUTE_RESPONSE",
        "WRONG_ROUTE",
        "ROUTING_EVIDENCE",
        "WRONG_PERSON",
        "WRONG_MAILBOX",
    },
    "NO_CONTACT": {
        "OWNER_NO_CONTACT_SUPERSESSION",
        "GOVERNED_NO_CONTACT",
        "NO_CONTACT_DIRECTIVE",
    },
    "ACCEPTED": {
        "BUYER_ACCEPTANCE",
        "SCOPE_PRICE_ACCEPTANCE",
        "COMMERCIAL_ACCEPTANCE",
    },
    "DELAYED": {
        "DELIVERY_DELAY",
        "TEMPORARY_DELIVERY_DELAY",
        "DELIVERY_RETRY_PENDING",
    },
}

def utcnow():
    return datetime.now(timezone.utc).isoformat()

def read(path):
    return json.loads(path.read_text())

def write(path, value):
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")
    tmp.replace(path)

VOLATILE_SCAN_KEYS = {"generated_at", "last_seen_at"}

def semantic_projection(value):
    """Remove scan-only timestamps before deciding whether tracked state changed."""
    if isinstance(value, dict):
        return {
            key: semantic_projection(item)
            for key, item in value.items()
            if key not in VOLATILE_SCAN_KEYS
        }
    if isinstance(value, list):
        return [semantic_projection(item) for item in value]
    return value

def semantically_equal_raw(raw_text, value):
    if raw_text is None:
        return False
    try:
        old = json.loads(raw_text)
    except (TypeError, json.JSONDecodeError):
        return False
    return semantic_projection(old) == semantic_projection(value)

def restore_raw(path, raw_text):
    if raw_text is None:
        path.unlink(missing_ok=True)
    else:
        path.write_text(raw_text)

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
    required_kinds = EVIDENCE_KIND_GATES.get(target)
    if required_kinds and not any(str(e.get("kind", "")).upper() in required_kinds for e in evidence):
        raise ValueError(f"{target} requires attributable {target} evidence")
    if target == "ACCEPTED":
        accepted_scope = payload.get("accepted_scope")
        accepted_price = payload.get("accepted_price")
        if not accepted_scope or accepted_price in (None, ""):
            raise ValueError("ACCEPTED requires exact accepted_scope and accepted_price")
    if target == "PAID" and not verified_payment(record, key, evidence):
        raise ValueError("PAID requires independent attributable verified settlement covering the receivable")
    old = record["state"]
    record["state"] = target
    record["last_action_at"] = payload["observed_at"]
    record["next_action"] = payload["next_action"]
    record.setdefault("evidence", []).extend(evidence)
    if target == "ACCEPTED":
        acceptance = {
            "scope": payload["accepted_scope"],
            "price": payload["accepted_price"],
            "observed_at": payload["observed_at"],
            "evidence_source_ids": [e["source_id"] for e in evidence],
        }
        if payload.get("accepted_currency"):
            acceptance["currency"] = payload["accepted_currency"]
        record["commercial_acceptance"] = acceptance
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



UPSERT_INITIAL_STATES = {
    "OFFERED",
    "SUBMITTED",
    "RESPONDED",
    "DELAYED",
    "DELIVERY_FAILED",
    "REJECTED",
    "WRONG_ROUTE",
    "NO_CONTACT",
}

UPSERT_EVIDENCE_GATES = {
    "OFFERED": {"GMAIL_SENT", "OUTBOUND_SEND", "OFFER_SENT"},
    "SUBMITTED": {"GMAIL_SENT", "OUTBOUND_SEND", "SUBMISSION_RECEIPT"},
    "RESPONDED": {"BUYER_RESPONSE", "BUYER_REFERRAL"},
    "DELAYED": EVIDENCE_KIND_GATES["DELAYED"],
    "DELIVERY_FAILED": {"DELIVERY_FAILURE"},
    "REJECTED": EVIDENCE_KIND_GATES["REJECTED"],
    "WRONG_ROUTE": EVIDENCE_KIND_GATES["WRONG_ROUTE"],
    "NO_CONTACT": EVIDENCE_KIND_GATES["NO_CONTACT"],
}

def _identity_token(value):
    return " ".join(str(value or "").strip().lower().split())


def _identity_slug(value):
    """Normalize a human title or stored slug to a canonical key slug."""
    return "-".join(
        "".join(char.lower() if char.isalnum() else " " for char in str(value or "")).split()
    )


def _same_upsert_evidence_replay(
    existing, *, key, organization, opportunity, domain, owner, target, recipient, thread_id, evidence
):
    """Return True only for the same canonical key, lifecycle and persisted source evidence.

    The canonical opportunity key/domain/title slug are the identity anchors. Organization
    labels may legitimately differ (for example, a brand name versus its longer legal or
    service label); they must not overwrite the existing canonical record on a replay.
    A key/state/recipient/evidence conflict still fails closed.
    """
    key_parts = str(key or "").split("|")
    if len(key_parts) < 2:
        return False
    key_domain = _identity_token(key_parts[0])
    key_slug = _identity_slug(key_parts[1])
    if not key_domain or not key_slug:
        return False
    if str(existing.get("state") or "").upper() != target:
        return False
    existing_domain = _identity_token(existing.get("domain"))
    incoming_domain = _identity_token(domain)
    if not incoming_domain or incoming_domain != key_domain or existing_domain != key_domain:
        return False
    existing_opportunity = existing.get("opportunity") or existing.get("title") or existing.get("name")
    if _identity_slug(opportunity) != key_slug or _identity_slug(existing_opportunity) != key_slug:
        return False
    if not _identity_token(organization) or not _identity_token(existing.get("organization") or existing.get("buyer") or existing.get("company")):
        return False
    if _identity_token(existing.get("execution_owner")) != _identity_token(owner):
        return False
    if recipient and _identity_token(existing.get("recipient")) != _identity_token(recipient):
        return False
    if thread_id and _identity_token(existing.get("thread_id")) != _identity_token(thread_id):
        return False

    prior_evidence = existing.get("evidence", [])
    for incoming in evidence:
        incoming_kind = str(incoming.get("kind") or "").upper()
        incoming_source_id = str(incoming.get("source_id") or "").strip()
        if not incoming_kind or not incoming_source_id:
            return False
        matching = [
            prior for prior in prior_evidence
            if str(prior.get("kind") or "").upper() == incoming_kind
            and str(prior.get("source_id") or "").strip() == incoming_source_id
        ]
        if not matching:
            return False
        # If supplied, these fields must match too. A reused source ID with
        # different provenance is a conflict, not an idempotent replay.
        for field in ("source", "observed_at"):
            expected = incoming.get(field)
            if expected not in (None, "") and not any(
                str(prior.get(field) or "") == str(expected)
                for prior in matching
            ):
                return False
    return True



def _linked_sent_items_receipt_is_verified(
    *, commit, receipt_path, current_source_id, previous_source_id, subject, recipient, query_filter
):
    """Verify the cited source ID receipt exists in canonical main history and supports this correction."""
    expected_path = "AMX/ROOT/INTAKE/DRAIN_Q_EXECUTION_RECEIPT_20261020_FOLLOW_ON.md"
    if receipt_path != expected_path:
        return False
    commit = str(commit or "").strip().lower()
    if len(commit) != 40 or any(ch not in "0123456789abcdef" for ch in commit):
        return False
    try:
        reachable = subprocess.run(
            ["git", "merge-base", "--is-ancestor", commit, "origin/main"],
            capture_output=True, text=True, check=False, timeout=10,
        )
        if reachable.returncode != 0:
            return False
        shown = subprocess.run(
            ["git", "show", f"{commit}:{expected_path}"],
            capture_output=True, text=True, check=True, timeout=10,
        )
    except (OSError, subprocess.CalledProcessError, subprocess.TimeoutExpired):
        return False
    receipt = shown.stdout or ""
    required_evidence = (
        "SAME-RUN CONTINUATION — MENDaz SENT-ITEM SOURCE-ID DIVERGENCE",
        str(current_source_id or ""),
        str(previous_source_id or ""),
        str(subject or ""),
        str(recipient or ""),
        str(query_filter or ""),
        "queue ID == Sent Items returned ID: **true**",
        "queue ID == canonical ledger ID: **false**",
    )
    return all(token and token in receipt for token in required_evidence)


def _reconcile_verified_source_id(
    existing, *, key, organization, opportunity, domain, owner, target, recipient, thread_id, evidence
):
    """Correct a source-ID typo only with a linked independent Sent Items readback.

    The old value is retained in both per-field provenance and a record-level correction
    history. This path does not change commercial lifecycle or imply an external action.
    """
    key_parts = str(key or "").split("|")
    if len(key_parts) < 2:
        return None
    key_domain = _identity_token(key_parts[0])
    key_slug = _identity_slug(key_parts[1])
    existing_opportunity = existing.get("opportunity") or existing.get("title") or existing.get("name")
    if (
        not key_domain or not key_slug
        or _identity_token(domain) != key_domain
        or _identity_token(existing.get("domain")) != key_domain
        or _identity_slug(opportunity) != key_slug
        or _identity_slug(existing_opportunity) != key_slug
        or str(existing.get("state") or "").upper() != target
        or _identity_token(existing.get("execution_owner")) != _identity_token(owner)
        or not _identity_token(organization)
        or not _identity_token(existing.get("organization") or existing.get("buyer") or existing.get("company"))
        or (recipient and _identity_token(existing.get("recipient")) != _identity_token(recipient))
        or (thread_id and _identity_token(existing.get("thread_id")) != _identity_token(thread_id))
    ):
        return None

    outbound = [e for e in evidence if str(e.get("kind") or "").upper() == "OUTBOUND_SEND"]
    readbacks = [e for e in evidence if str(e.get("kind") or "").upper() == "OUTLOOK_SENT_ITEM_ID_READBACK"]
    if len(outbound) != 1 or len(readbacks) != 1:
        return None
    sent = outbound[0]
    readback = readbacks[0]
    current_id = str(sent.get("source_id") or "").strip()
    verified_id = str(readback.get("source_id") or "").strip()
    subject = str(sent.get("subject") or "").strip()
    recipient_token = _identity_token(recipient)
    commit = str(readback.get("verification_receipt_commit") or "").strip()
    if (
        not current_id or verified_id != current_id or not subject
        or str(sent.get("source") or "").upper() != "OUTLOOK"
        or str(readback.get("source") or "") != "OUTLOOK_SENT_ITEMS_READBACK"
        or str(readback.get("folder") or "") != "Sent Items"
        or str(readback.get("subject") or "").strip() != subject
        or _identity_token(readback.get("recipient")) != recipient_token
        or recipient_token != _identity_token(existing.get("recipient"))
        or str(readback.get("query_filter") or "") != "sentDateTime ge 2026-10-20T00:00:00Z"
        or str(readback.get("receipt_path") or "") != "AMX/ROOT/INTAKE/DRAIN_Q_EXECUTION_RECEIPT_20261020_FOLLOW_ON.md"
        or not sent.get("observed_at")
    ):
        return None

    prior_evidence = existing.get("evidence", [])
    candidates = [
        row for row in prior_evidence
        if str(row.get("kind") or "").upper() == "OUTBOUND_SEND"
        and str(row.get("source") or "").upper() == "OUTLOOK"
        and str(row.get("observed_at") or "") == str(sent.get("observed_at") or "")
        and str(row.get("subject") or "").strip() == subject
        and str(row.get("source_id") or "").strip()
        and str(row.get("source_id") or "").strip() != current_id
    ]
    if len(candidates) != 1:
        return None
    target_row = candidates[0]
    previous_id = str(target_row["source_id"]).strip()
    if not _linked_sent_items_receipt_is_verified(
        commit=commit,
        receipt_path=readback.get("receipt_path"),
        current_source_id=current_id,
        previous_source_id=previous_id,
        subject=subject,
        recipient=recipient,
        query_filter=readback.get("query_filter"),
    ):
        return None
    matching_rows = [
        row for row in prior_evidence
        if str(row.get("source_id") or "").strip() == previous_id
        and str(row.get("subject") or "").strip() == subject
        and str(row.get("kind") or "").upper() in {"OUTBOUND_SEND", "POST_SEND_OFFER_CONTROL_REVIEW"}
    ]
    if target_row not in matching_rows:
        return None

    correction = {
        "kind": "SOURCE_ID_CORRECTION",
        "field": "evidence.source_id",
        "evidence_kind": "OUTBOUND_SEND",
        "previous_source_id": previous_id,
        "corrected_source_id": current_id,
        "subject": subject,
        "recipient": recipient,
        "source": "OUTLOOK",
        "verification_method": "OUTLOOK_SENT_ITEMS_LIST_READBACK",
        "verification_folder": "Sent Items",
        "verification_source_id": verified_id,
        "verification_receipt_path": readback["receipt_path"],
        "verification_receipt_commit": commit,
        "query_filter": readback["query_filter"],
        "affected_evidence_rows": [
            {
                "kind": str(row.get("kind") or ""),
                "source": str(row.get("source") or ""),
                "observed_at": str(row.get("observed_at") or ""),
                "previous_source_id": previous_id,
                "corrected_source_id": current_id,
            }
            for row in matching_rows
        ],
    }
    for row in matching_rows:
        row["source_id"] = current_id
        row["source_id_correction"] = {
            "previous_source_id": previous_id,
            "corrected_source_id": current_id,
            "verification_receipt_commit": commit,
        }
    existing.setdefault("source_id_corrections", []).append(correction)
    if not any(
        str(row.get("kind") or "").upper() == "OUTLOOK_SENT_ITEM_ID_READBACK"
        and str(row.get("source_id") or "").strip() == verified_id
        and str(row.get("verification_receipt_commit") or "").strip() == commit
        for row in prior_evidence
    ):
        existing.setdefault("evidence", []).append(dict(readback))
    return {
        "adapter": "MISSING_RECORD_UPSERT",
        "opportunity_key": key,
        "to": target,
        "created": False,
        "idempotent": False,
        "source_id_corrected": True,
        "lifecycle_changed": False,
        "source_id_correction": correction,
        "evidence": [sent, readback],
        "critic": {
            "factual_claims": "PASS_LINKED_SENT_ITEMS_READBACK",
            "duplicate_identity": "PASS_CANONICAL_KEY_DOMAIN_AND_SLUG",
            "commercial_state": "PASS_NO_LIFECYCLE_CHANGE",
            "external_action": "NOT_PERFORMED_BY_ADAPTER",
        },
    }


def missing_record_upsert(task, opportunities):
    """Create one missing canonical commercial record from attributable external evidence.

    This is deliberately narrower than generic CRM creation. It only repairs an
    external-execution-without-record gap under existing iSCOPE/PRI identity rules.
    Existing records are left unchanged on exact evidence replay. A conflicting source ID
    can be corrected only when the queue carries a linked independent Sent Items readback
    matching the canonical key, provider item ID, subject and recipient; the old value is
    preserved in correction history. Every other mismatch fails closed.
    """
    payload = task["payload"]
    records = opportunities.setdefault("records", {})
    key = str(payload.get("opportunity_key") or "").strip()
    if not key:
        raise ValueError("opportunity_key is required")

    identity = payload.get("identity") or {}
    organization = str(identity.get("organization") or "").strip()
    opportunity = str(identity.get("opportunity") or "").strip()
    domain = str(identity.get("domain") or "").strip().lower()
    if not organization or not opportunity:
        raise ValueError("identity.organization and identity.opportunity are required")

    target = str(payload.get("to") or "").upper()
    if target not in UPSERT_INITIAL_STATES:
        raise ValueError(f"missing-record upsert cannot initialize state {target}")

    owner = str(payload.get("execution_owner") or "PRI")
    if owner not in {"PRI", "iSCOPE"}:
        raise ValueError("execution_owner must be PRI or iSCOPE")

    evidence = payload.get("evidence", [])
    if not evidence or any(not e.get("source_id") or not e.get("kind") for e in evidence):
        raise ValueError("durable evidence is required")
    required = UPSERT_EVIDENCE_GATES[target]
    if not any(str(e.get("kind", "")).upper() in required for e in evidence):
        raise ValueError(f"{target} requires attributable evidence for missing-record ingestion")

    observed_at = payload.get("observed_at")
    next_action = str(payload.get("next_action") or "").strip()
    if not observed_at or not next_action:
        raise ValueError("observed_at and next_action are required")

    if key in records:
        existing = records[key]
        if _same_upsert_evidence_replay(
            existing,
            key=key,
            organization=organization,
            opportunity=opportunity,
            domain=domain,
            owner=owner,
            target=target,
            recipient=payload.get("recipient"),
            thread_id=payload.get("thread_id"),
            evidence=evidence,
        ):
            return {
                "adapter": "MISSING_RECORD_UPSERT",
                "opportunity_key": key,
                "to": target,
                "created": False,
                "idempotent": True,
                "disposition": "ALREADY_RECORDED_EXACT_EVIDENCE_REPLAY",
                "evidence": evidence,
                "critic": {
                    "factual_claims": "PASS_EXISTING_SOURCE_EVIDENCE_READBACK",
                    "duplicate_identity": "PASS_IDEMPOTENT_EXACT_SOURCE_REPLAY",
                    "commercial_state": "PASS_NO_LIFECYCLE_CHANGE",
                    "external_action": "NOT_PERFORMED_BY_ADAPTER",
                },
            }
        correction = _reconcile_verified_source_id(
            existing,
            key=key,
            organization=organization,
            opportunity=opportunity,
            domain=domain,
            owner=owner,
            target=target,
            recipient=payload.get("recipient"),
            thread_id=payload.get("thread_id"),
            evidence=evidence,
        )
        if correction is not None:
            return correction
        raise ValueError("opportunity already exists; exact evidence replay not proven; use EVIDENCE_TRANSITION")

    org_token = _identity_token(organization)
    opp_token = _identity_token(opportunity)
    domain_token = _identity_token(domain)
    for existing_key, existing in records.items():
        existing_org = _identity_token(existing.get("organization") or existing.get("buyer") or existing.get("company"))
        existing_opp = _identity_token(existing.get("opportunity") or existing.get("title") or existing.get("name"))
        existing_domain = _identity_token(existing.get("domain"))
        same_named_identity = existing_org and existing_opp and existing_org == org_token and existing_opp == opp_token
        same_domain_identity = domain_token and existing_domain == domain_token and existing_opp and existing_opp == opp_token
        if same_named_identity or same_domain_identity:
            raise ValueError(f"possible duplicate canonical identity: {existing_key}")

    observed_at = payload.get("observed_at")
    next_action = str(payload.get("next_action") or "").strip()
    if not observed_at or not next_action:
        raise ValueError("observed_at and next_action are required")

    record = {
        "state": target,
        "execution_owner": owner,
        "organization": organization,
        "opportunity": opportunity,
        "domain": domain or None,
        "recipient": payload.get("recipient"),
        "thread_id": payload.get("thread_id"),
        "last_action_at": observed_at,
        "next_action": next_action,
        "due_at": payload.get("due_at"),
        "evidence": list(evidence),
        "canonical_ingest": {
            "kind": "MISSING_RECORD_RECOVERY",
            "observed_at": observed_at,
            "identity": {
                "organization": organization,
                "opportunity": opportunity,
                "domain": domain or None,
            },
            "evidence_source_ids": [e["source_id"] for e in evidence],
        },
    }
    records[key] = record
    return {
        "adapter": "MISSING_RECORD_UPSERT",
        "opportunity_key": key,
        "to": target,
        "created": True,
        "evidence": evidence,
        "critic": {
            "factual_claims": "PASS_EVIDENCE_GATED",
            "duplicate_identity": "PASS_NO_MATCH_FOUND",
            "commercial_state": "PASS",
            "external_action": "NOT_PERFORMED_BY_ADAPTER",
        },
    }

def access_verification(task, opportunities):
    payload = task["payload"]
    key = payload["opportunity_key"]
    record = opportunities["records"][key]
    evidence = payload.get("evidence", [])
    if not evidence or any(
        e.get("kind") != "VIDEO_ACCESS_PERMISSION" or
        not e.get("source_id") or e.get("role") != "reader"
        for e in evidence
    ):
        raise ValueError("reader permission evidence is required")
    recipient = payload["recipient"].lower()
    valid = {record.get("recipient", "").lower()}
    valid.update(x.lower() for x in record.get("recipients", []))
    if recipient not in valid:
        raise ValueError("permission recipient does not match commercial record")
    record["video_access_verified"] = True
    record["video_access_verified_at"] = payload["observed_at"]
    record["proof_access"] = {
        "file_id": payload["file_id"],
        "visibility": "CONTROLLED_READER",
        "public": False,
        "recipient": payload["recipient"],
    }
    record["evidence"].extend(evidence)
    return {
        "adapter": "ACCESS_VERIFICATION",
        "opportunity_key": key,
        "commercial_state": record["state"],
        "state_changed": False,
        "video_access_verified": True,
        "recipient": payload["recipient"],
        "file_id": payload["file_id"],
        "critic": {
            "rights": "PASS_CONTROLLED_READER",
            "privacy": "PASS_NOT_PUBLIC",
            "recipient_match": "PASS",
            "external_acceptance": "NOT_INFERRED",
        },
    }

def stripe_payment_settlement(task, opportunities):
    """Independently read Stripe settlement, attest it, then use the existing PAID gate."""
    payload = task["payload"]
    key = payload["opportunity_key"]
    record = opportunities["records"][key]
    expected = payload.get("expected_from") or record.get("state")
    if expected not in {"INVOICED", "RECEIVABLE"}:
        raise ValueError("Stripe settlement verification requires INVOICED or RECEIVABLE state")
    if record.get("state") != expected:
        raise ValueError(f"state mismatch: {record.get('state')} != {expected}")
    payment_intent_id = payload.get("payment_intent_id") or record.get("stripe_payment_intent_id")
    if not payment_intent_id:
        raise ValueError("Stripe payment_intent_id is required")
    attestation = attest_stripe_settlement(record, key, payment_intent_id)
    result = evidence_transition(
        {"payload": {
            "opportunity_key": key,
            "expected_from": expected,
            "to": "PAID",
            "evidence": [attestation],
            "observed_at": attestation["settled_at"],
            "next_action": payload.get("next_action") or "Reconcile verified Stripe settlement and issue receipt/closeout.",
        }},
        opportunities,
    )
    result["adapter"] = "STRIPE_PAYMENT_SETTLEMENT"
    result["payment_intent_id"] = payment_intent_id
    return result


ADAPTERS = {
    "EVIDENCE_TRANSITION": evidence_transition,
    "MISSING_RECORD_UPSERT": missing_record_upsert,
    "ACCESS_VERIFICATION": access_verification,
    "STRIPE_PAYMENT_SETTLEMENT": stripe_payment_settlement,
}

def claim_work(signals, opportunities):
    """Durably claim every actionable signal. Claims cannot silently disappear:
    COMPLETED still requires a receipt. Off-route claims remain durable but cannot
    remain READY merely because they were actionable in an earlier ledger snapshot.
    """
    now = datetime.now(timezone.utc)
    try:
        claims = read(CLAIMS)
    except (FileNotFoundError, json.JSONDecodeError):
        claims = {"version": 1, "claims": {}}
    active = claims.setdefault("claims", {})
    seen = set()
    records = opportunities.get("records", {})
    for office in ("iSCOPE", "PRI"):
        for item in signals.get(office, []):
            key = office + "|" + item["opportunity_key"]
            seen.add(key)
            prior = active.get(key, {})
            if prior.get("status") == "COMPLETED" and prior.get("receipt"):
                continue
            active[key] = {
                **prior,
                "office": office,
                "opportunity_key": item["opportunity_key"],
                "state": item.get("state"),
                "next_action": item.get("next_action"),
                "status": item.get("status", "WAITING"),
                "priority": item.get("priority", 99),
                "smallest_next_action": item.get("smallest_next_action"),
                "thread_id": item.get("thread_id"),
                "required_executor": "iSCOPE PRI Field Force",
                "routing_reason": item.get("routing_reason"),
                "last_seen_at": now.isoformat(),
                "attempts": int(prior.get("attempts", 0)),
                "receipt_required": True,
            }
    for key, claim in active.items():
        record = records.get(claim.get("opportunity_key"))
        if record is not None:
            claim.update({
                "state": payment_state(record, claim.get("opportunity_key")),
                "next_action": record.get("next_action"),
                "due_at": record.get("due_at"),
            })
        # Execution authorization is a current-state projection, not durable history.
        # Never let an old READY flag survive a current WAITING/CLOSED/COMPLETED state.
        if claim.get("status") != "READY":
            claim["external_action_ready"] = False
        if claim.get("status") == "COMPLETED" and claim.get("receipt"):
            continue
        if key not in seen and not claim.get("customer_request_id"):
            # Preserve work and receipts. A missing signal is not task completion.
            claim["status"] = "WAITING"
            claim["routing_reason"] = "NOT_CURRENTLY_ROUTED" if record else "LEDGER_RECORD_MISSING"
            if record and str(record.get("state", "")).startswith("CLOSED") and record.get("evidence"):
                claim["status"] = "CLOSED"
                claim["closure_source"] = "opportunities.json"
                claim["closure_evidence"] = record["evidence"]
        elif claim.get("status") == "READY":
            claim.pop("routing_reason", None)
    reconcile_customer_requests(active, records)
    claims["generated_at"] = now.isoformat()
    claims["ready_count"] = sum(v.get("status") == "READY" for v in active.values())
    claims["external_ready_count"] = sum(
        v.get("status") == "READY" and v.get("external_action_ready") is True
        for v in active.values()
    )
    claims["executable_order"] = sorted((k for k,v in active.items() if v.get("status")=="READY"), key=lambda k:(active[k].get("priority",99), active[k].get("due_at") or "9999",k))
    write(CLAIMS, claims)
    return claims

def commercial_action(key, record, now):
    state = payment_state(record, key)
    action = str(record.get("next_action") or "").strip()
    if state == "PAYMENT_UNVERIFIED":
        action = "Independently verify the attributed bank/provider settlement before any PAID claim."
    due_now = False
    if record.get("due_at"):
        try:
            due_now = datetime.fromisoformat(record["due_at"].replace("Z", "+00:00")) <= now
        except (ValueError, TypeError):
            pass
    priority = 8
    if state in {"INVOICED", "RECEIVABLE"} and due_now: priority = 1
    elif state == "ACCEPTED" and action: priority = 1
    elif state in {"RESPONDED", "NEGOTIATING"} and action: priority = 2
    elif state in {"CONTRACTED", "ORDERED"}: priority = 3
    elif state in {"INVOICED", "RECEIVABLE", "PAYMENT_UNVERIFIED"}: priority = 4
    elif record.get("submission_ready") is True and record.get("route_verified_live") is True and record.get("payment"): priority = 5
    elif record.get("bounded_paid_deliverable") and record.get("acceptance_criteria") and record.get("payment"): priority = 6
    elif record.get("credible_buyer") and record.get("bounded_paid_deliverable"): priority = 7
    if due_now and priority == 8: priority = 2
    reason = None
    readiness = str(record.get("execution_readiness") or record.get("readiness") or "").upper()
    active_deps = [v for v in (record.get("active_dependencies") or {}).values() if v.get("state") == "ACTIVE"]
    unavailable_route = any(phrase in str(constraint).lower() for constraint in record.get("constraints", [])
                            for phrase in ("no authenticated", "is presently unavailable", "registration/authentication is still required"))
    suppressed_state = state in {"NO_CONTACT", "REJECTED", "WRONG_ROUTE", "DELAYED"}
    readiness_gate = (
        readiness.startswith(("HOLD", "SUPPRESSED"))
        or readiness in {
            "WAITING",
            "BLOCKED",
            "HUMAN_PROVIDER_GATE",
            "HUMAN_ONLY_GATE",
            "OWNER_GATE",
            "PROVIDER_GATE",
        }
    )
    if state.startswith("CLOSED") or state == "PAID": status = "CLOSED"
    elif suppressed_state:
        status, reason = "WAITING", state
    elif state.startswith("HOLD") or state == "DEPRIORITIZED" or readiness_gate:
        status, reason = "WAITING", state if state.startswith("HOLD") else (readiness or state)
    elif active_deps:
        status, reason = "WAITING", "ACTIVE_DEPENDENCY"
    elif unavailable_route or (record.get("submission_ready") is True and record.get("route_verified_live") is not True):
        status, reason = "WAITING", "EXECUTION_ROUTE_UNAVAILABLE_OR_UNVERIFIED"
    elif not action:
        status, reason = "WAITING", "NEXT_ACTION_MISSING"
    elif action.lower().startswith(("monitor", "wait", "no action")) and not due_now:
        status, reason = "WAITING", "AWAITING_REPLY_OR_DUE_INTERVAL"
    elif state in {"SUBMITTED", "OFFERED"} and not due_now:
        status, reason = "WAITING", "FOLLOWUP_NOT_DUE"
    else: status = "READY"
    smallest = active_deps[0].get("next") if active_deps else action
    if status == "READY" and record.get("thread_id") and (due_now or action.lower().startswith(("monitor", "wait"))):
        smallest = f"Read existing thread {record['thread_id']} for a material reply; continue in-thread only if due or requested; never repeat initial outreach."
    if state == "PAYMENT_UNVERIFIED":
        smallest = "Independently verify the attributed bank/provider settlement before any PAID claim."
    return {"opportunity_key": key, "state": state, "next_action": action,
            "smallest_next_action": smallest, "thread_id": record.get("thread_id"),
            "due_at": record.get("due_at"), "due_now": due_now, "status": status,
            "priority": priority, "routing_reason": reason}


def reconcile_customer_requests(active, records):
    if not REQUESTS.exists(): return
    with REQUESTS.open() as handle:
        fcntl.flock(handle, fcntl.LOCK_SH)
        lines = handle.read().splitlines()
    for line in lines:
        if not line.strip(): continue
        request = json.loads(line)
        rid, opportunity = request["request_id"], request.get("opportunity_key")
        key = f"PRI|{opportunity}|request|{rid}"
        prior = active.get(key, {})
        record = records.get(opportunity, {})
        thread = request.get("thread_id")
        evidence = prior.get("action_evidence", {})
        if (prior.get("status") in {"COMPLETED", "CLOSED"} and evidence.get("source_id")
                and evidence.get("thread_id") == thread
                and evidence.get("kind") in {"CUSTOMER_REQUEST_ACTIONED", "CUSTOMER_REQUEST_CLOSED"}):
            continue
        actionable = record.get("execution_owner") == "PRI" and thread and thread == record.get("thread_id")
        active[key] = {**prior, "office": "PRI", "opportunity_key": opportunity,
            "customer_request_id": rid, "customer_id": request.get("customer_id"),
            "proposal_ref": request.get("proposal_ref"), "thread_id": thread,
            "customer_request_source": f"/api/customer-requests/{rid}", "state": payment_state(record, opportunity),
            "status": "READY" if actionable else "WAITING", "priority": 2,
            "next_action": f"Review {request['action']} {rid} and respond in existing thread {thread}; do not contact a new address or repeat outreach.",
            "smallest_next_action": f"Read private customer request {rid} through the authorized request endpoint, then continue in thread {thread}.",
            "required_executor": "iSCOPE PRI Field Force", "receipt_required": True,
            "routing_reason": None if actionable else "CUSTOMER_THREAD_ASSOCIATION_UNVERIFIED"}


def detect_work(opportunities):
    """Classify the full ledger; route actionable and waiting obligations without sending."""
    now = datetime.now(timezone.utc)
    signals = {"generated_at": now.isoformat(), "iSCOPE": [], "PRI": [], "ledger": {}}
    for key, record in opportunities.get("records", {}).items():
        item = commercial_action(key, record, now)
        signals["ledger"][key] = item
        if item["status"] == "CLOSED": continue
        owner = record.get("execution_owner")
        if owner == "iSCOPE" or (not owner and record.get("state") == "DISCOVERED"):
            signals["iSCOPE"].append(item)
        elif owner == "PRI":
            signals["PRI"].append(item)
    for office in ("iSCOPE", "PRI"):
        signals[office].sort(key=lambda x:(x["status"] != "READY", x["priority"], x.get("due_at") or "9999", x["opportunity_key"]))
    write(SIGNALS, signals)
    return signals

def tick():
    if not claim_lock():
        print(json.dumps({"status": "HOLD", "reason": "active_tick"}))
        return 0
    try:
        raw_signals = SIGNALS.read_text() if SIGNALS.exists() else None
        raw_claims = CLAIMS.read_text() if CLAIMS.exists() else None
        state = read(STATE)
        opportunities = read(OPPORTUNITIES)
        signals = detect_work(opportunities)
        claims = claim_work(signals, opportunities)
        routing_changed = (
            not semantically_equal_raw(raw_signals, signals)
            or not semantically_equal_raw(raw_claims, claims)
        )
        pending = [task for task in state.get("queue", []) if task["status"] == "PENDING"]
        if not pending and not routing_changed:
            # A wake is not a commercial transition. Keep tracked state byte-identical
            # when only scan timestamps moved; workflow logs remain the heartbeat.
            restore_raw(SIGNALS, raw_signals)
            restore_raw(CLAIMS, raw_claims)
            counts = {"iSCOPE": len(signals["iSCOPE"]), "PRI": len(signals["PRI"])}
            print(json.dumps({
                "status": "WATCHING",
                "pending": 0,
                "signals": counts,
                "ready_claims": claims["ready_count"],
                "state_changed": False,
            }, sort_keys=True))
            return 0

        state["last_tick"] = utcnow()
        state["last_signal_count"] = {"iSCOPE": len(signals["iSCOPE"]), "PRI": len(signals["PRI"])}
        state["ready_claims"] = claims["ready_count"]
        if not pending:
            state["adapter_status"] = "OPERATIONAL"
            state["last_tick_result"] = {
                "processed": [],
                "pending": 0,
                "signals": state["last_signal_count"],
                "state_changed": True,
            }
            write(STATE, state)
            print(json.dumps({
                "status": "WATCHING",
                "pending": 0,
                "signals": state["last_signal_count"],
                "ready_claims": state["ready_claims"],
                "state_changed": True,
            }, sort_keys=True))
            return 0
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
