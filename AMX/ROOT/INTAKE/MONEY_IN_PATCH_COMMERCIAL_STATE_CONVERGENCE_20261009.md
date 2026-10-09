# ECOSYSTEM / INTEGRATION UPGRADE PROPOSAL — COMMERCIAL STATE CONVERGENCE

**Intake ID:** ROOT-20261009-MONEY-IN-COMMERCIAL-STATE-CONVERGENCE  
**Recommended classification:** ECOSYSTEM / INTEGRATION UPGRADE  
**Secondary scope:** governance/evidence acceptance  
**Authority effect:** PROPOSAL ONLY — Governance decides promotion.

## Anomaly

Current live readback shows:
- Gmail contains broad outbound activity and high-information buyer threads;
- Close contains 3 leads, 3 overdue tasks and **0 active opportunities**;
- Face Production and Ecognix are absent from Close search;
- Stripe has 0 PaymentIntents, 0 invoices and 0 balance transactions;
- Banker correctly remains at USD 0 verified settlement.

This is not a Close defect or Stripe defect. It is a commercial-state convergence defect.

## Existing authority

Category-B Revenue Inflow Mechanics already recommends:
- revenue-truth reconciliation;
- CRM projection, not replacement;
- accepted-scope → existing-rail bridge.

The condition persists, so this artifact asks Governance whether to promote that recommendation into an explicit integration requirement.

## Proposed integration contract

Do not create a second CRM or commercial ledger.

Preserve the existing authoritative AMX commercial ledger / continuity as source of commercial lifecycle state.

Provider roles:
- Gmail/provider send receipts = external communication evidence;
- Close = operational projection for qualified/warm managed opportunities;
- Stripe/other rails = payment/receivable/settlement evidence where applicable;
- Banker = terminal financial truth;
- FORX raw candidates remain outside CRM until qualified;
- iSCOPE qualifies;
- PRI owns external progression.

For every qualified or warmer opportunity worth active management, the projection must expose:
- canonical opportunity ID;
- organization + current buyer/contact;
- exact lifecycle state;
- warm/cold source class;
- latest external thread/receipt;
- exact offer/version/value;
- NEXT_ACTION;
- DUE / waiting condition;
- owner;
- suppression / bounce / wrong-person state;
- accepted scope/price evidence where present;
- payment-step state;
- latest settlement truth pointer.

## Commercial consequence

Without convergence:
- warm opportunities can disappear from the operational view;
- overdue work can survive without a live opportunity;
- strategy can be changed from incomplete funnel data;
- response, rejection and bounce learning cannot reliably flow back to source weighting;
- payment activation cannot be attributed cleanly.

## Acceptance test

A bounded cohort of qualified/warm opportunities must be reconstructable without material mismatch across:

**AMX canonical state ↔ Gmail/provider evidence ↔ Close projection ↔ Banker ↔ payment rail where applicable.**

For the cohort:
- no duplicate external send caused by projection lag;
- no warm buyer absent from the active operational view without an explicit reason;
- latest NEXT_ACTION/DUE matches canonical state;
- bounces/rejections/acceptances propagate;
- PAID remains Banker/payment-evidence controlled.

## Falsifier / optionality

If Close introduces more maintenance latency than decision value, Governance may choose another operational projection or keep Close optional. The invariant is state convergence, not loyalty to Close.
