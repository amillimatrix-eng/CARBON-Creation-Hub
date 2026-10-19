# AMX Commercial Routing Control v1

Status: ACTIVE
Effective: 2026-09-30
Owner disposition: ACCEPTED

## Canonical routing

NEW INCOMING COMMERCIAL OPPORTUNITY → iSCOPE
QUALIFIED HANDOFF → PRI
ALL OUTGOING COMMERCIAL PROPOSITIONS → PRI
EXISTING PRI-OWNED SALES THREAD, INCLUDING INBOUND REPLY → PRI UNTIL TERMINAL

## Single-writer authority

iSCOPE is the sole execution owner for commercial discovery and pre-handoff qualification.
PRI is the sole execution owner for post-handoff commercial progression and outbound propositions.

All other runtimes, chats, automations, OVERDRIVE lanes, production workers, scanners and managers are support/transport/evidence surfaces only for these mandates. They must route evidence/work to iSCOPE or PRI rather than create parallel commercial ownership.

## Boundary

iSCOPE: discover → verify → dedupe → qualify → durable OPP-ID/evidence → handoff.
PRI: intake → prioritize → prepare → approach → follow up → qualify further → objection handling → package/offer → negotiate → close → expand/reactivate → record → next.

A new inbound lead/opportunity routes to iSCOPE.
A response in an existing PRI-owned thread routes to PRI.

## Automation reconciliation effected 2026-09-30

- AMX Revenue Execution was replaced in-place by the active iSCOPE → PRI Commercial Loop.
- AMX Overdrive Conversion was disabled/superseded as an independent commercial executor.
- CARBON° Production Studio was restricted to production; new commercial evidence routes to iSCOPE and commercial-ready assets route to PRI.
- Master Control Check was updated to enforce this routing, detect/stop duplicate commercial execution, and preserve Root Continuity Watch without another slot.
- HASH Calibration remains a separate bounded non-commercial mandate.

No separate iSCOPE or PRI automation slot is required: the consolidated commercial loop invokes the two governed offices while preserving exclusive ownership boundaries.

## Commercial states

DISCOVERED → QUALIFIED → OFFERED/SUBMITTED → RESPONDED → NEGOTIATING → CONTRACTED → INVOICED/RECEIVABLE → PAID

Do not merge AVAILABLE / SUBMITTED / ACCEPTED / INVOICED / PAID.
Realized revenue is zero until payment evidence exists.

## Collision/failover

A waking runtime must recover current control before commercial action. If the action belongs to iSCOPE or PRI, it routes/supports rather than executes independently.
Loss/degradation of an owner does not reactivate all workers. One evidenced successor receives the mandate.

## Continuity

Current durable evidence supersedes automation prompt snapshots.
No opportunity may be discarded during handoff/reconciliation.
NO RECEIPT → NO CLOSURE.


## Owner-directed addendum — immutable offer/pro-forma identity, South African price supersession, and market selection (2026-10-19)

**Authority:** Additive implementation of the Owner-directed Blue State section `OWNER-DIRECTED COMMERCIAL INTENT / OFFER IDENTITY / MARKET SUCCESS LAW — 2026-10-19`. Keep this control, the existing proposal registry, and the existing opportunity ledger as one commercial path. Do not create another writer or ledger.

### Single-writer requirements

- iSCOPE remains sole owner for discovery, current buyer/authority/fit qualification, deduplication, and evidence-backed handoff.
- PRI remains sole owner for all outgoing propositions, quote issuance, offer negotiation and customer-response progression.
- Existing delivery owner confirms feasibility and accepts the bounded delivery handoff; Banker validates cost/margin, invoice/tax logic, actual payment and settlement.
- Other runtimes may supply sourced evidence only. They do not independently issue offers, resend or change accepted terms.

### Required offer object

Use the existing `proposal_ref` and current proposal registry as the primary offer reference. On every new outgoing offer, bind:
- immutable `proposal_ref` / Offer ID and `offer_version`;
- existing opportunity key and customer/domain;
- originating signal/source URL/date and the sent-message/thread receipt;
- target country/currency and verified comparable benchmark/source date/tax basis;
- price factor version; exact scope, deliverables, exclusions, inputs/access, acceptance tests, dependencies, turnaround assumptions, IP/usage terms and expiry;
- customer-facing pro-forma/quote location, accepted-version data, any buyer-issued PO reference, payment route, invoice state, delivery state and next action.

The proposed human-readable Offer ID convention is `AMX-OFR-YYYYMMDD-NNNN-V1`; bind it to the existing `proposal_ref`, not a new ID service. A customer PO number is separately captured only if the buyer issues it. The reference convention does not prove a customer-facing offer exists: the pro-forma plus actual send receipt must be independently read back.

**Outbound gate:** do not send a new proposition unless the referenced customer-readable pro-forma/quote has been generated and read back, its version and exact scope/price are fixed, and the country-appropriate payment route is actually supportable. Keep the four contacts messaged in this run under their no-repeat boundary. Their original sent messages must not be reissued just to add an identifier.

### Commercial transitions and truth

Keep the states distinct: `DISCOVERED → QUALIFIED → PRO-FORMA/QUOTE ISSUED → RESPONDED → ACCEPTED (exact version locked) → PAYMENT DUE → PAID VERIFIED → FINAL INVOICE/TAX INVOICE WHEN LAWFULLY REQUIRED → DELIVERY → CUSTOMER DELIVERY ACCEPTANCE`. A contract or legally necessary invoice may be a separate state when the jurisdiction/transaction requires it. Never infer acceptance from a page view, click, demo request or generic customer question; never infer payment from an invoice, checkout session, transfer promise or email. The current customer-portal route explicitly says its request does not accept or pay a quote; a request alone remains a request.

The Owner's normal commercial policy is pro-forma before payment and final invoice/tax-invoice on independently verified payment. Apply any earlier issue requirement imposed by applicable tax/time-of-supply law. SARS guidance generally gives 21 days from time of supply for a tax invoice; tax status, correct value/VAT treatment and lawful issue timing must be verified by the authorized accounting owner. A pro-forma is not mislabeled a final/tax invoice. Do not fabricate VAT status or invoice evidence.

### Price supersession / no mass reissue

- New South African offers: **50% of the current evidenced comparable low-end benchmark for the same scope**, effective 2026-10-19; this supersedes 67% for South Africa only.
- All non-South-African markets keep the existing applicable 67% rule unless separately superseded by the Owner. Recalibrate each market in local currency/scope; do not just FX-convert South African figures.
- Do not mass-edit/retract/resend an existing offer. Preserve its issued price, validity, scope, original version and receipt.
- If the customer returns to accept a still-valid prior South African offer issued at 67%, link the acceptance to the original version. Calculate the same-scope difference at the current 50% rule. Give the customer a clear choice of a lower amount due, equivalent approved account credit, or a defined upgrade. After prior payment, keep the original invoice unchanged and use a legally correct credit note/account credit or upgrade; a cash reimbursement is not automatic. Do not create a credit before the buyer accepts/selects the benefit or book it as cash.
- Expired quotes follow existing quote-expiry recovery; never silently revive or change one.

### Target selection / intention

Global discovery remains active. Use existing FORX → iSCOPE → PRI selection to prioritize markets and buyer cohorts with evidence of online/cross-border digital buying, current business signal, actual decision authority, AMX service fit, an authorized reachable route, supportable payment method, delivery capacity and short time-to-cash. Initial UK focus is a testable market hypothesis, not a guarantee; continue international diversity and update country/cohort weights only from attributable outcome evidence. The Owner's South African skepticism observation is cohort-level owner-reported evidence, not a universal claim about every South African buyer.

### Acceptance / open gap

Acceptance for the control update is exact file readback. Runtime acceptance remains open until a source-backed test proves pro-forma issuance, customer-request vs acceptance separation, immutable accepted-version locking, legacy SA benefit calculation, invoice/tax gating, no-duplicate behavior and payment/settlement truth in the actual proposal/runner path. Do not report these code/runtime behaviors as implemented merely because this rule exists.
