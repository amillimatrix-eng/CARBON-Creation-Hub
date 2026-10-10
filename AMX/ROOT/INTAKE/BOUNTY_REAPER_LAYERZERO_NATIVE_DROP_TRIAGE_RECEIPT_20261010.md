# BOUNTY REAPER — LAYERZERO NATIVE-DROP STATIC TRIAGE RECEIPT

**Receipt ID:** BR-20261010-STATIC-001  
**Date:** 2026-10-10 (SAST)  
**Existing Reaper parcel:** BR-20261003-024  
**Receipt type:** Productive static/source-history narrowing  
**Current classification:** **Q3 NARROWED — NOT READY FOR SUBMISSION**  
**Tracker marker:** `TRACKER_WRITE_BLOCKED`

## 1. Work performed

Recovered the existing BLACK job `BLACK/jobs/REAPER-RECOVERY-20261006-0934-001.json`, the LayerZero source pin it specifies, and existing Reaper execution-stagnation disposition. Used available GitHub source/history routes because BLACK is an accelerator rather than a mandatory dependency. Fetched and inspected the pinned source and current `main` source for the relevant Solidity control flow, plus the corresponding public commit history. No live targets, transactions, credentials, exploit execution, or fund movement were used.

- Existing recovery job SHA: `bbb0334a702eecc74c318555b7fe1ea9f6bf90ea`.
- Immutable source requested by that job: `LayerZero-Labs/LayerZero-v2@9c741e7f9790639537b1710a203bcdfd73b0b9ac`.
- Source file: [Executor.sol at the pinned commit](https://github.com/LayerZero-Labs/LayerZero-v2/blob/9c741e7f9790639537b1710a203bcdfd73b0b9ac/packages/layerzero-v2/evm/messagelib/contracts/Executor.sol).
- Current source independently inspected: [Executor.sol at main](https://github.com/LayerZero-Labs/LayerZero-v2/blob/main/packages/layerzero-v2/evm/messagelib/contracts/Executor.sol).
- Test path inspected for contextual behavior: [OmniCounter.t.sol](https://github.com/LayerZero-Labs/LayerZero-v2/blob/9c741e7f9790639537b1710a203bcdfd73b0b9ac/packages/layerzero-v2/evm/oapp/test/OmniCounter.t.sol). The accessible example test covers successful native-drop delivery; it does not establish the failed-recipient case.
- Relevant source-history entries identified include `67582d09449a8dabef123dd84c7159f029b98829` (2024-10-10, “update EVM Executor reference implementation”) and `943ce4a2bbac070f838e12c7fd034bca6a281ccf` (2024-11-11, “Sync ReadLib”). The function's observed semantics are present in current `main` too; source age is not evidence of a valid/known disclosure by itself.

## 2. Static result — precise code semantics

In `Executor._nativeDrop` the contract:
1. Calls each `param.receiver` with `param.amount` and the supplied gas limit using a low-level call.
2. Stores the returned success flag in `success[i]`.
3. Increments `spent` by `param.amount` unconditionally, regardless of the call result.
4. Emits `NativeDropApplied(..., success)`, so failed transfers are represented in the event.

In `nativeDropAndExecute302`, `value = msg.value - spent` is calculated from the nominal total, then `endpoint.lzReceive` is still attempted with that `value`. A receive failure is caught and sent to `lzReceiveAlert`. Thus a false native-drop result alone does **not** mechanically stop the message receive attempt. The failed transfer amount remains at the Executor contract unless another authorized path accounts for it; no retry/refund flow was found in this contract's relevant functions.

The call path is privileged with `onlyRole(ADMIN_ROLE)`; the receiver appears in the native-drop parameters derived from message options. Current static evidence does not demonstrate an unprivileged caller forcing an unrelated victim to lose funds. If the message sender selected a recipient contract that rejects native currency, that fact alone is not proof of adversarial victim impact. The event also exposes the failure, so the behavior is not silent.

## 3. Hypothesis disposition

**Killed/narrowed sub-claim:** “A failed native drop by itself prevents `lzReceive` from being attempted.” The code continues to `lzReceive` with the remaining value and catches execution failure separately.

**Unresolved Q3 concern:** A failed native transfer is still counted as spent, while the transfer itself has failed. The requested amount may remain on the Executor with no retry/refund path in this contract. The accessible evidence does not yet establish that this creates eligible loss to a non-self-selected victim, or that such a loss can affect an eligible in-scope asset. This is a narrowed hypothesis, not a vulnerability finding.

The parcel remains Q3 rather than Q1 or Q2 because the following gates are open:
- exact deployed Executor address / chain / proxy implementation binding;
- verified eligibility under the current program scope or a concrete primacy-of-impact path to an in-scope asset;
- attacker/victim impact and amount-at-risk proof from an authorized local/fork fixture;
- confirmation whether an off-chain Executor workflow provides retry or recovery;
- prior-disclosure/audit dedupe.

## 4. Current program and dedupe gate

Official LayerZero Immunefi pages were reviewed:
- [Current scope](https://immunefi.com/bug-bounty/layerzero/scope/) — last updated 2026-10-02; lists PoC and KYC requirements, impact categories and scope/out-of-scope boundaries.
- [Program information](https://immunefi.com/bug-bounty/layerzero/information/) — requires a runnable PoC with an end-effect for an in-scope asset and states vulnerabilities identified in LayerZero's audit repository are not eligible for a reward.
- [Program resources](https://immunefi.com/bug-bounty/layerzero/resources/) — says only assets in the Assets in Scope table are considered in-scope, while other LayerZero assets may be submitted for consideration if they produce an eligible impact.

The source file alone does not bind an on-chain deployment or establish that this Executor is a named in-scope target. No qualifying high/critical effect on an in-scope asset is presently proven. The LayerZero audit repository tree contains EVM MessageLib audits including the 2023 initial review and 2026 diff review. This runtime's GitHub text-search route returned no matching `nativeDrop` / `NativeDropApplied` terms in indexed audit material, but the PDFs themselves could not be read through the current available connectors. **Audit dedupe is therefore NOT PASSED**; absence of indexed search hits is not evidence the issue is absent from an audit.

## 5. Tracker write fallback — exact blocker

Canonical sink: `AMX Bounty Reaper — Live Tracker`, spreadsheet ID `1ETiK6b2YOz499OXBA5wuvgyWMjnDZoEdJIwCt2xGeCk`.

- Attempted action: discover an authorized Google Sheets/Drive route, read current Runs/Queue/Payouts, write a productive Runs receipt, and independently read that row back.
- Exact blocker: no Google Sheets/Drive read-write connector is exposed to this runtime. Therefore no authorized operation was available to read or mutate the sheet or verify a row. This does not establish that the sheet or its data are absent.
- Fallback: this receipt is written to existing Root Intake and linked from the existing Intake index, with the literal marker `TRACKER_WRITE_BLOCKED`.
- Runs row: **not written**. Current Q1: **UNKNOWN**, not zero. Queue/Payouts were not changed.

## 6. Next lawful execution step

Recover the exact Executor deployment and implementation mapping from existing LayerZero deployment registries and the program's current assets; inspect the relevant audit PDFs or obtain an authorized searchable copy; then construct a local-only test with a receiver that rejects native currency to document retained balance, `NativeDropApplied.success=false`, subsequent `lzReceive` arguments, and any real retry/recovery path. No public/mainnet/testnet target execution is authorized by this receipt.

Until exact scope, prior-art and attacker/victim impact are proved, do not build a submission packet or submit to Immunefi. Continue other independent executable Reaper parcels instead of idling on this Q3 gate.

## 7. Truth boundary

- Material parcel movement: **YES** — failed-drop / receive semantics narrowed from untested signal to code-grounded behavior; one sub-claim killed.
- Validated bounty finding: **NO**.
- Submission package ready: **NO**.
- Immunefi report submitted: **NO**.
- Acceptance / award: **NONE evidenced**.
- Payment: **NONE verified**.
- Live Tracker row: **NOT WRITTEN**; Root Intake fallback receipt only.
