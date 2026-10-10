# BOUNTY REAPER — XOXNO INV-ACCT-10 STATIC TRIAGE RECEIPT

**Receipt ID:** BR-20261010-XOXNO-STATIC-001  
**Date:** 2026-10-10 (SAST)  
**Existing parcel:** REAPER-XOXNO / jobs `REAPER-XOXNO-20261006-2057-A` and superseding attempt `REAPER-XOXNO-20261006-2057-B`  
**Frozen source:** `XOXNO/rs-lending-xlm@a2486b255b974ef8432ce44de014931f51552f4b` (commit dated 2026-09-29)  
**Outcome:** **Q3 NARROWED; SPECIFIC STALE/NON-RETURNED POSITION SUB-CLAIM NOT REPRODUCED BY STATIC REVIEW. NOT SUBMISSION-READY.**  
**Tracker fallback:** `TRACKER_WRITE_BLOCKED`

## 1. Why this work was selected

The existing job A/B asks for bounded static/local review of controller-to-pool account-position synchronization under `INV-ACCT-10`, especially stale or non-returned scaled positions and liquidation/accounting paths. The BLACK jobs have no evidenced durable result receipt. BLACK is an accelerator, not a mandatory dependency, so this wake executed the smallest available GitHub-backed source/history and test-specification review instead of idling or repeatedly dispatching an unreceipted job.

- Job A SHA: `f0426685806b97941bb14b1e86ae2eba63a5979a`.
- Superseding job B SHA: `952d102845023de12e447a46178e4c0d19d391f4`.
- Pinned source: [XOXNO controller source at exact queued commit](https://github.com/XOXNO/rs-lending-xlm/tree/a2486b255b974ef8432ce44de014931f51552f4b).
- Invariant statement: [`INV-ACCT-10`](https://github.com/XOXNO/rs-lending-xlm/blob/a2486b255b974ef8432ce44de014931f51552f4b/docs/reference/invariants.md).
- Pool trust model: [Pool README](https://github.com/XOXNO/rs-lending-xlm/blob/a2486b255b974ef8432ce44de014931f51552f4b/contracts/pool/README.md).

## 2. Static paths inspected and result

The pool has aggregate market totals rather than a per-account ledger; therefore its caller—the controller—must keep each account's scaled position coherent. The queued invariant states that standard mutation paths must carry the current position in and commit the pool's returned position out. Static inspection of the following paths found the expected returned-position flow, not an evidenced stale-position write:

- `contracts/controller/src/positions/supply.rs`: `process_deposit` passes the existing controller position into pool supply; `merge_supply_leg` replaces `scaled_amount` with `LegOutcome::from(PoolPositionMutation).new_scaled`.
- `contracts/controller/src/positions/debt.rs`: borrow/repay paths pass the tracked position and merge the returned mutation through `merge_debt_leg`; that function writes `outcome.new_scaled`.
- `contracts/controller/src/positions/supply.rs`: withdrawal results are merged through `merge_withdraw_leg`, which writes the returned scaled position and applies the precise before/after spoke-usage delta.
- `contracts/controller/src/strategies/legs.rs`: same-market net settlement takes both returned `supply_position` and `debt_position` from the pool result and merges each side.
- `contracts/controller/src/positions/liquidation/apply.rs`: repayment merges returned pool mutations. In share-credit liquidation, the source account is debited by `seized_scaled`, the receiver is credited `liquidator_scaled`, and code asserts `seized_scaled - liquidator_scaled == fee_scaled`; only the fee is sent to the pool for reclassification as revenue. The account-share conservation path is explicit.
- `contracts/controller/src/positions/liquidation/bad_debt.rs`: remaining positions are passed to pool seizure, spoke usage is released, then the account is removed and its NFT burned. This is an explicit account-exit path, not a normal stale-position merge.

### Deliberate zero-position close footprint — checked

`strategies/legs.rs::execute_withdraw_all` can issue a footprint-only withdraw with `scaled_amount: 0` and `WITHDRAW_ALL_SENTINEL` when same-transaction repayment has removed the position in simulation. This initially looks unlike a real position mutation, but the exact pinned source has a paired pool-side rule: `contracts/pool/src/ops/withdraw.rs` recognizes `position.raw() == 0 && amount == i128::MAX` as `empty_close`; it moves no shares or cash and skips the utilization check that could otherwise strand net settlement. The source contains `contracts/pool/tests/withdraw.rs::full_close_keeps_the_utilization_gate_and_an_empty_close_skips_it` and `dust_close_keeps_native_recipient_writable_when_interest_crosses_one_unit`. The September 25, 2026 commit [`9566b23f1d9ccd14a66ff2def51e9acdeb179250`](https://github.com/XOXNO/rs-lending-xlm/commit/9566b23f1d9ccd14a66ff2def51e9acdeb179250) introduced this footprint behavior and its tests; comparison of history confirms that change is an ancestor of the queued immutable commit from September 29. It is not evidence of a stale position by itself.

## 3. Existing validation evidence found (not executed in this runtime)

- `tests/test-harness/tests/fuzz/accounting_conservation.rs::prop_accounting_conservation` checks after each randomized operation that user supply balances reconcile with pool supplied shares less revenue, debt balances reconcile with borrowed shares, reserves remain non-negative, and indexes are monotone within defined tolerances.
- `tests/test-harness/tests/controller/liquidation_seize_modes.rs::credit_mode_leaves_supplied_and_cash_untouched_and_moves_only_revenue` checks that share-credit liquidation preserves supplied totals and cash while moving the protocol fee to revenue.
- The same test module's `credit_mode_moves_spoke_usage_by_exactly_the_protocol_fee` checks spoke usage decreases by the exact fee.
- `certora/controller/spec/spoke_rules.rs` enumerates production position-mutation classes, including cross-account credit liquidation, and includes fail-closed coverage for unwired new mutation verbs.

These are test/specification definitions in the repository, not evidence that tests or Certora jobs passed during this wake. The current connector provides source retrieval, not a local checkout/toolchain. No compilation, property-test execution or formal proof was run.

## 4. Hypothesis disposition

**Sub-claim narrowed/killed:** the inspected supply, borrow, repay, withdraw, net-settlement and liquidation flows do not show a write of a stale/non-returned scaled value. They derive normal mutations from pool return values; the credit-liquidation path applies an explicit debit-credit-fee conservation identity. The conspicuous zero-position close is an intentional simulation/inclusion footprint mechanism and already has paired pool logic and targeted regression tests in the pinned commit.

**What this does not prove:** absence of every possible accounting defect across all code/configurations, deployed Wasm, deployment wiring or adversarial sequence. The property test and formal specification were inspected but not executed. No reproducible exploit or invariant deviation was found by this static pass. Therefore do not promote to Q2, do not prepare a bounty finding, and do not submit. The original broad suspicion is narrowed to any *specific additional path* that can be evidenced with a concrete non-returned position input, actor/precondition, and mismatched post-state; without that, this parcel has no submission-grade vulnerability claim.

## 5. Dedupe and bounty gate

No program-specific bounty submission is justified from this parcel's current evidence. This receipt does not claim that a current XOXNO bounty program/scope was verified, nor that public-audit/prior-art review or deployed contract/WASM mapping is complete. The code's explicit invariant and property tests are prior art for this *generic controller position-conservation hypothesis*, not proof that every imaginable path is safe. A future, narrower claim needs an exact new counterexample and official current program/scope check before any packet or external action.

## 6. Durable tracker fallback — exact attempted action and blocker

Canonical sink: `AMX Bounty Reaper — Live Tracker`, spreadsheet ID `1ETiK6b2YOz499OXBA5wuvgyWMjnDZoEdJIwCt2xGeCk`.

- Attempted action: obtain an authorized Google Sheets/Drive connector, read current `Runs/Queue/Payouts`, write the attributable run row for this Q3 narrowing/kill transition, and independently read the row back.
- Exact blocker: the current runtime exposes no Google Sheets/Drive read-write connector. No authorized call exists here to read the sheet, append a row, or verify a row. This is a tool/access-surface blocker; it is not evidence the tracker or its contents are missing.
- Required fallback: this receipt is being written to the existing Root Intake route with the literal `TRACKER_WRITE_BLOCKED`, attempted action and precise blocker.
- Runs row: **not written**. Queue/Payouts: **not read or updated**. Current Q1 remains **UNKNOWN**, not zero. Do not represent this report as a tracker write.

## 7. Next lawful action

If the same stale-position concern is to be reopened, provide/derive one exact concrete path, caller precondition, non-returned scaled value, and pool/controller post-state discrepancy from the pinned source or a new commit. Otherwise, archive this general sub-claim as not substantiated and advance to another independent Reaper parcel. Any eventual candidate still requires exact deployed source/asset mapping, current official bounty scope, novelty/audit dedupe, impact, and the program-required local/fork PoC before submission.

## 8. Truth boundary

- Material Q3 movement: **YES** — generic stale/non-returned position sub-claim narrowed by source inspection; suspicious empty-close path explained by matching pool logic and targeted test definitions.
- Vulnerability found/validated: **NO**.
- Local tests/Certora executed: **NO**.
- Submission-ready: **NO**.
- External submission/acceptance/award/payment: **NONE claimed**.
- Live Tracker row: **NOT WRITTEN**; `TRACKER_WRITE_BLOCKED` fallback only.
