# AMX OVERDRIVE

Commercial execution control scaffold for AMilliMATRiX.

## Verified implementation

The current Python runner writes local readiness receipts. It does **not** invoke discovery, production, distribution, conversion or other external adapters. `READY_FOR_ADAPTER` means an adapter is still required; it is not evidence of completed work.

The GitHub workflow compiles the runner and parses its JSON configuration/state. It is a validation workflow, not a commercial execution heartbeat. The Actions API returned zero workflow runs during inspection on 30 September 2026. This does not establish the state of a separately deployed worker.

The repository state has an empty queue, sequence 0 and no last tick. Lane labels alone do not prove operational workers.

## Operating contract

Resume each opportunity from its furthest evidenced state:

DISCOVERED → QUALIFIED → OFFERED/SUBMITTED → RESPONDED → NEGOTIATING → CONTRACTED → INVOICED/RECEIVABLE → PAID

Use one organization/opportunity record and one action owner. Check prior contact and provider receipts before external actions. Count failed delivery separately from sent mail. Keep internal production identifiers out of buyer-facing packaging.

## Commissioning acceptance

An operational worker must demonstrably claim a real task, invoke an authorized adapter, persist its artifact and return an attributable receipt visible in the existing CARBON° operating dashboard. Verify retry/recovery and prevent duplicate actions. Connect the actual production assets to the Living Exhibition Gallery and a controlled buyer viewing route.

The existing House deployment is the consolidation target; recovering its capabilities does not authorize a replacement system. A scaffold, static label, receipt hash or validation run does not satisfy commissioning.

## Safety

No credentials, private contact ledgers or confidential commercial terms in this public repository. Preserve provider controls, rights and existing audience restrictions. Commercial terminal state remains PAID; do not fabricate execution or revenue.
