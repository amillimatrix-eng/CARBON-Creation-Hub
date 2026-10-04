# AMX OVERDRIVE

Commercial execution control scaffold for AMilliMATRiX.

## Verified implementation — current readback 4 October 2026

The Python runner consumes evidence-transition/access-verification queue items, persists receipts, and derives office signals and durable work claims from the opportunity ledger. It does **not** execute external commercial actions; a transport tick or READY claim is not a buyer submission, acceptance or payment.

Repository readback records an OPERATIONAL transport tick at 2026-10-04T00:44:51Z: 18 iSCOPE and 17 PRI signals, no pending adapter queue items. After the retained-claim repair, 54 claims reconcile with 66 opportunity records: 35 READY, 13 WAITING and 6 CLOSED; zero state/next-action mismatches. Closed claims retain their existing ledger evidence; waiting claims are preserved rather than marked completed.

The sole scheduled reasoning writer is the existing Field Force automation, with separate iSCOPE and PRI mandates. The legacy execution engine is disabled. Post-merge attributable reasoning-worker execution proof remains a separate acceptance condition; transport health does not satisfy it.

Jojo proposal PUBLIC v2 has a Gmail SENT receipt with its PDF attachment, persisted in the ledger and Notion handoff. This interactive authorized substitute receipt does not prove scheduled-worker execution, recipient receipt, acceptance or revenue. The September 30 zero-run/sequence-zero observations are historical.

## Operating contract

Resume each opportunity from its furthest evidenced state:

DISCOVERED → QUALIFIED → OFFERED/SUBMITTED → RESPONDED → NEGOTIATING → CONTRACTED → INVOICED/RECEIVABLE → PAID

Use one organization/opportunity record and one action owner. Check prior contact and provider receipts before external actions. Count failed delivery separately from sent mail. Keep internal production identifiers out of buyer-facing packaging.

## Commissioning acceptance

An operational worker must demonstrably claim a real task, invoke an authorized adapter, persist its artifact and return an attributable receipt visible in the existing CARBON° operating dashboard. Verify retry/recovery and prevent duplicate actions. Connect the actual production assets to the Living Exhibition Gallery and a controlled buyer viewing route.

The existing House deployment is the consolidation target; recovering its capabilities does not authorize a replacement system. A scaffold, static label, receipt hash or validation run does not satisfy commissioning.

## Safety

No credentials, private contact ledgers or confidential commercial terms in this public repository. Preserve provider controls, rights and existing audience restrictions. Commercial terminal state remains PAID; do not fabricate execution or revenue.
