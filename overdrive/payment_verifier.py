"""Independent settlement acquisition for AMX payment truth.

This module does one job the existing payment_truth validator cannot do:
read settlement facts from a payment processor and turn them into a signed
attestation that existing fail-closed PAID logic can verify.

Secrets remain runtime-only. No email, invoice, internal label, or caller-
supplied "paid" flag can create settlement evidence.
"""
from __future__ import annotations

import hashlib
import hmac
import json
import os
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from decimal import Decimal

try:
    from overdrive.payment_truth import verified_payment
except ImportError:  # Existing direct-script entry point used by OVERDRIVE.
    from payment_truth import verified_payment

STRIPE_API = "https://api.stripe.com/v1"
ZERO_DECIMAL = {
    "BIF", "CLP", "DJF", "GNF", "JPY", "KMF", "KRW", "MGA",
    "PYG", "RWF", "UGX", "VND", "VUV", "XAF", "XOF", "XPF",
}


class SettlementVerificationError(ValueError):
    pass


def _require_secret(name: str, minimum: int = 1) -> str:
    value = os.getenv(name, "")
    if len(value) < minimum:
        raise SettlementVerificationError(f"{name} is not configured")
    return value


def _minor_to_major(amount: int, currency: str) -> Decimal:
    exponent = 0 if currency.upper() in ZERO_DECIMAL else 2
    return Decimal(amount) / (Decimal(10) ** exponent)


def fetch_stripe_payment_intent(payment_intent_id: str) -> dict:
    """Read one live Stripe PaymentIntent directly from Stripe."""
    secret = _require_secret("STRIPE_SECRET_KEY")
    if not payment_intent_id.startswith("pi_"):
        raise SettlementVerificationError("invalid Stripe PaymentIntent id")
    query = urllib.parse.urlencode([("expand[]", "latest_charge")])
    request = urllib.request.Request(
        f"{STRIPE_API}/payment_intents/{urllib.parse.quote(payment_intent_id)}?{query}",
        headers={"Authorization": f"Bearer {secret}", "User-Agent": "AMX-Payment-Verifier/1"},
        method="GET",
    )
    try:
        with urllib.request.urlopen(request, timeout=15) as response:
            return json.loads(response.read().decode("utf-8"))
    except Exception as exc:
        raise SettlementVerificationError(f"Stripe settlement read failed: {type(exc).__name__}") from exc


def _sign_attestation(facts: dict) -> dict:
    secret = _require_secret("AMX_PAYMENT_VERIFICATION_KEY", 32)
    body = dict(facts)
    digest = hmac.new(
        secret.encode(),
        json.dumps(body, sort_keys=True, separators=(",", ":")).encode(),
        hashlib.sha256,
    ).hexdigest()
    return {**body, "verification_hmac": digest}


def attest_stripe_settlement(record: dict, opportunity_key: str, payment_intent_id: str) -> dict:
    """Fetch, validate, and sign an independently read Stripe settlement."""
    try:
        due = Decimal(str(record["amount_due"]))
        currency = str(record["currency"]).upper()
        payer_id = str(record["payer_id"])
        payee_account = str(record["payee_account"])
    except (KeyError, TypeError, ValueError) as exc:
        raise SettlementVerificationError("receivable identity is incomplete") from exc

    if due <= 0 or not payer_id or not payee_account:
        raise SettlementVerificationError("receivable identity is invalid")

    intent = fetch_stripe_payment_intent(payment_intent_id)
    if intent.get("status") != "succeeded":
        raise SettlementVerificationError("Stripe payment is not settled")

    observed_currency = str(intent.get("currency", "")).upper()
    if observed_currency != currency:
        raise SettlementVerificationError("Stripe currency does not match receivable")

    try:
        amount = _minor_to_major(int(intent.get("amount_received", 0)), currency)
    except (TypeError, ValueError):
        raise SettlementVerificationError("Stripe amount_received is invalid")
    if amount < due:
        raise SettlementVerificationError("Stripe settled amount does not cover receivable")

    metadata = intent.get("metadata") or {}
    required_metadata = {
        "opportunity_key": opportunity_key,
        "payer_id": payer_id,
        "payee_account": payee_account,
    }
    for key, expected in required_metadata.items():
        if str(metadata.get(key, "")) != str(expected):
            raise SettlementVerificationError(f"Stripe metadata mismatch: {key}")

    charge = intent.get("latest_charge")
    if not isinstance(charge, dict) or charge.get("paid") is not True:
        raise SettlementVerificationError("Stripe latest charge is not independently confirmed paid")
    try:
        settled_at = datetime.fromtimestamp(int(charge["created"]), tz=timezone.utc).isoformat().replace("+00:00", "Z")
    except (KeyError, TypeError, ValueError, OSError) as exc:
        raise SettlementVerificationError("Stripe settlement timestamp is unavailable") from exc

    facts = {
        "kind": "PAYMENT_SETTLED",
        "source": "PAYMENT_PROCESSOR",
        "source_id": str(intent.get("id") or payment_intent_id),
        "source_reference": f"https://dashboard.stripe.com/payments/{payment_intent_id}",
        "status": "SETTLED",
        "direction": "INBOUND",
        "independently_verified": True,
        "opportunity_key": opportunity_key,
        "amount": format(amount, "f"),
        "currency": currency,
        "payer_id": payer_id,
        "payee_account": payee_account,
        "settled_at": settled_at,
    }
    attestation = _sign_attestation(facts)
    if not verified_payment(record, opportunity_key, [attestation]):
        raise SettlementVerificationError("generated settlement attestation failed AMX payment truth")
    return attestation
