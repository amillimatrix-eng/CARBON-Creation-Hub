"""Fail-closed payment attestation shared by transport and read projections.

The authorized verifier must independently read the bank/processor/chain settlement
and sign these facts with its runtime-only AMX_PAYMENT_VERIFICATION_KEY. Emails,
invoices, queue receipts and commercial status labels are never attestations.
"""
import hashlib
import hmac
import json
import os
import re
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation


def verified_payment(record, opportunity_key, evidence=None):
    secret = os.getenv("AMX_PAYMENT_VERIFICATION_KEY", "")
    if len(secret) < 32 or not opportunity_key:
        return False
    try:
        due = Decimal(str(record["amount_due"]))
        if not due.is_finite() or due <= 0:
            return False
        currency = record["currency"]
        payer, payee = record["payer_id"], record["payee_account"]
        if not payer or not payee or not re.fullmatch(r"[A-Z]{3}", currency):
            return False
    except (KeyError, TypeError, ValueError, InvalidOperation):
        return False
    items = record.get("evidence", []) if evidence is None else evidence
    if not isinstance(items, list):
        return False
    for item in items:
        if not isinstance(item, dict):
            continue
        facts = {k: v for k, v in item.items() if k != "verification_hmac"}
        signature = item.get("verification_hmac")
        if not isinstance(signature, str):
            continue
        digest = hmac.new(secret.encode(), json.dumps(facts, sort_keys=True, separators=(",", ":")).encode(), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(signature, digest):
            continue
        if (facts.get("kind") != "PAYMENT_SETTLED" or facts.get("source") not in {"BANK", "PAYMENT_PROCESSOR", "BLOCKCHAIN"}
                or facts.get("status") != "SETTLED" or facts.get("direction") != "INBOUND"
                or facts.get("independently_verified") is not True
                or facts.get("opportunity_key") != opportunity_key
                or facts.get("currency") != currency or facts.get("payer_id") != payer
                or facts.get("payee_account") != payee or not facts.get("source_id")
                or not str(facts.get("source_reference", "")).startswith(("https://", "bank://", "chain://"))):
            continue
        try:
            amount = Decimal(str(facts["amount"]))
            settled = datetime.fromisoformat(facts["settled_at"].replace("Z", "+00:00"))
            if amount.is_finite() and amount >= due and settled.tzinfo and settled <= datetime.now(timezone.utc):
                return True
        except (KeyError, TypeError, ValueError, InvalidOperation):
            continue
    return False


def payment_state(record, key):
    state = str(record.get("state", "UNKNOWN")).upper()
    return "PAYMENT_UNVERIFIED" if state == "PAID" and not verified_payment(record, key) else state
