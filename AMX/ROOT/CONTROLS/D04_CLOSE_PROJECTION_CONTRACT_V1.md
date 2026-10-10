# D04 CLOSE PROJECTION CONTRACT V1
Date: 2026-10-10
Controls: EA04 / COM06 / QMS07

## Authority and purpose
Close is an operational projection, not the canonical commercial ledger and not a second CRM truth plane. Canonical commercial truth remains `overdrive/opportunities.json` plus attributable provider evidence.

## Projection scope
Close projects only the current fixed-price AMX outbound pilot offers that satisfy all of:
1. externally sent through an attributable provider route;
2. exact one-time USD amount is evidenced in the canonical record/provider receipt;
3. canonical state is still commercially open;
4. PRI remains the commercial owner.

At this acceptance point the complete in-scope set is:
- Kingston Stanley — USD 99 — canonical state SUBMITTED / WAITING;
- Xubio — USD 49 — canonical state SUBMITTED / WAITING;
- Synergy Interactive — USD 99 — canonical state SUBMITTED / WAITING.

Employment applications, content submissions, discovery-only records, unpriced collaborations, platform tasks, HOLD/NO_CONTACT/REJECTED/WRONG_ROUTE items and buyer routes without an AMX fixed-price outbound offer are intentionally out of this Close projection. They remain canonical in OVERDRIVE.

## Truth rules
- Close status labels are coarse UI projection only; the exact canonical state must be carried in the opportunity note.
- Close confidence/probability is NOT Matrix evidence. Projected opportunities use confidence=0 unless an evidence-governed probability model is separately authorized.
- Close value may mirror only an evidenced offer amount. It is not a receivable.
- A Close opportunity may not promote SUBMITTED/SENT to RESPONDED/ACCEPTED/CONTRACTED/INVOICED/PAID without canonical/provider evidence.
- Any projection mismatch is a reconciliation defect, not authority to rewrite canonical truth.

## Acceptance readback — 2026-10-10
Close contains exactly three active opportunities in this bounded scope:
- Kingston Stanley: 9900 cents, Proposal Sent UI label, confidence 0, note states canonical SUBMITTED / WAITING and no response/acceptance/payment.
- Xubio: 4900 cents, Proposal Sent UI label, confidence 0, same truth boundary.
- Synergy Interactive: 9900 cents, Proposal Sent UI label, confidence 0, same truth boundary.

Result: scoped projection parity PASS. This does not claim that Close mirrors every AMX opportunity.
