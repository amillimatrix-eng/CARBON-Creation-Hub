# DRAIN-Q Source Receipt — Forest Energy O&M Alert-to-Closeout Outreach — 2026-10-21

## Source records

1. **Outbound message**
   - Provider: Outlook / Sent Items
   - Message ID: `AQMkADAwATM0MDAAMS03NTM2LTYyNzgtMDACLTAwCgBGAAADR02W6I7woU2AiDvBGiB_dgcACcuKl8g3RkyfBaEy7toItQAAAgEJAAAACcuKl8g3RkyfBaEy7toItQACLz9RygAAAA==`
   - Exact subject: `A bounded paid pilot for O&M alert-to-closeout handoff`
   - Sender: `usduplessis@outlook.com`
   - Recipient: `sales@forestenergy.co.za`
   - Timestamp read from the existing sent item: `2026-10-21T04:49:22Z`
   - Action: initial scoped introduction / request for a workflow-owner scope check; no price or checkout route promised as ready, no production access assumed, no further contact authorized by this receipt.
2. **Automatic reply**
   - Provider: Outlook / Inbox
   - Message ID: `AQMkADAwATM0MDAAMS03NTM2LTYyNzgtMDACLTAwCgBGAAADR02W6I7woU2AiDvBGiB_dgcACcuKl8g3RkyfBaEy7toItQAAAgEMAAAACcuKl8g3RkyfBaEy7toItQACLz9hTgAAAA==`
   - Exact subject: `Automatic reply: A bounded paid pilot for O&M alert-to-closeout handoff`
   - Sender: `ruan@forestenergy.co.za`
   - Recipient: `usduplessis@outlook.com`
   - Timestamp read from the inbox item: `2026-10-21T04:49:36Z`
   - Observed text: sender is out of office with limited access and will respond when available.

## Commercial interpretation

- The outbound item and automatic response are both verified in the connected Outlook mailbox.
- The automatic response is **not** substantive buyer interest, scope/price acceptance, contract, receivable, or payment. Do not transition to `RESPONDED` or `ACCEPTED` based on this auto-reply.
- A current-main scan of `overdrive/opportunities.json` blob `6fc0ca68ada4b07a3263618f2a23a1d64db9f3f9` contained 124 canonical records and no Forest Energy/domain match. This is a missing-record evidence reconciliation for the already-sent outbound; it is not a new outreach action.
- Proposed canonical key: `forestenergy.co.za|o-m-alert-to-closeout-handoff-pilot|2026-10-21`.
- Correct initial lifecycle state: `SUBMITTED` (initial outreach; no fixed-scope/price offer accepted). Execution owner: `PRI`. Thread ID deliberately left null because the native readback returned no independently confirmed conversation ID.
- Current next action: WAIT for a material, non-automated buyer reply in the existing Outlook thread; no duplicate outreach. If the buyer identifies the owner or expresses interest, confirm exact scope, acceptance criteria, supported collection route, and access boundaries before any work. Do not begin work before paid receipt and authorized access are verified.

## Writer boundary / disposition

- Existing evidence-gated `MISSING_RECORD_UPSERT` adapter is the only approved mutation route. No direct edit to the opportunity ledger or claim projection was made here.
- The task may be appended to the existing Overdrive queue only with the outbound Sent Items ID, this durable receipt, and the auto-reply evidence; the writer must record state `SUBMITTED` and preserve the auto-reply without promoting it to a substantive buyer response.
- No email was sent by this receipt. No payment, invoice, acceptance, or revenue is inferred.

## Directive 23

- **Expected outcome:** the confirmed outbound is represented once in the canonical ledger, with source evidence and a truthful wait state.
- **Owner:** existing PRI / revenue pipeline owner; T-COD owns the writer and receipt.
- **Action:** run the existing evidence-gated upsert for the canonical key; verify the durable writer receipt, ledger row, and claim projection; keep the item waiting.
- **Dependencies:** exact outbound source ID, canonical source receipt, and current-main duplicate check.
- **Evidence/readback:** native Outlook message IDs above; current-main opportunity blob above; the post-write runner receipt and a fresh 124+/claim projection readback must be captured after processing.
- **Safety:** no duplicate message, no false buyer-response or money-in state, no new worker, no direct ledger mutation.
- **Disposition:** external outreach verified; canonical ledger ingestion awaits evidence-gated writer execution.
- **Remaining work:** independently read back the new writer receipt, ledger key, and claim projection after the existing writer processes the task.
