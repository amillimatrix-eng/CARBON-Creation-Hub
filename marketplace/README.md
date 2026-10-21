# CARBON° Intent Marketplace

Status: implementation branch evidence. Not a claim of production payment readiness.

## What this slice proves

The first executable CARBON° marketplace loop extends the existing FastAPI/SQLite backend rather than creating a second stack.

It implements:

- browsing without obligation;
- seller intent and seller-defined bond bounds;
- buyer bonded interest;
- capped monetary signal so overbonding cannot automatically buy priority;
- seller selection without activating buyer consequence;
- bilateral commitment activation only after buyer confirmation;
- explicit time windows and expiry/review states;
- valid exit versus breach-review separation;
- bilateral performance evidence;
- inspection and dual deal acceptance;
- immutable marketplace event history;
- pseudonymous marketplace actor references;
- a provider-neutral money boundary.

## Money boundary

The current adapter is deliberately named `SANDBOX_NO_MONEY_MOVED`.

It does not custody, transfer, forfeit, release, or settle real funds.

Production writes remain fail-closed unless a runtime explicitly enables demo mode. A regulated payment/escrow provider, production identity/KYC, legal rules, and approved money-resolution instructions remain external gates.

## Runtime

The container entrypoint uses:

```
uvicorn backend.carbon_app:app
```

The existing Evidence House remains mounted. CARBON° adds:

- `/market`
- `/api/carbon/bootstrap`
- marketplace listing/interest/commitment/deal routes

## Development demo

Set:

```
CARBON_MARKETPLACE_DEMO_MODE=1
```

Demo identities are represented to the marketplace only through deterministic `C°...` references. Demo mode still moves no money.

## Product boundary preserved

CARBON° is not defined by escrow.

The executable spine is:

Intent → Commitment → Bond → Time → Behaviour → History → Market Intelligence.

Freedom until commitment. Accountability after commitment.
