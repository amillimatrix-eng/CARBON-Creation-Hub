# FORX-VFY-20261006-002 — real-work acceptance receipt

**Observed:** 2026-10-20 09:37:17 SAST / 07:37:17Z  
**Existing flight:** `AMX-FLT-20261012-DSYNC-145440-9fb44f0c`  
**Authorization:** `AMX-AUTH-20261012-145440-9fb44f0c`  
**Segment:** 12 — existing flight only  
**Stable interrogation ID:** `AMX-FORX-VFY-20261020-LZ-VARIATIONAL-REENTRY-01`  
**Runner:** current AMX runtime, operating the FORX-VFY acceptance protocol on real bounty-research work  
**Current pre-flight:** Registry v1.3 root SHA-256 `96c0beb3328ebefc16286d93a7baadc0ff4be0a17c1e6a8718b89de94f58df1a`; FORX mandate registered CURRENT at `a9570686dae130bd36d0995d9f58dbd0f7cde1597968dc16245c94a65f0f3109`; Reaper mandate registered CURRENT at `754d8fb9b6816da1bf0013940883106e0d3928b1637526ee82b38e1792c1dcd3`. No mandate payload was changed.

## Objective and test

**Objective:** Demonstrate that the 13-head, re-entrant Instigator protocol improves contradiction/eligibility detection, pivots on material evidence, preserves prior dispositions, and resumes from the right bounty-work continuation point.

**Why:** The previous Reaper receipt had useful source-level dispositions but lacked an explicit, stable re-entry identity and a recorded pivot-to-continuation chain. FORX-VFY-20261006-002 requires observable real-work benefit; having a specification or a prior 13-item list is not enough.

**Pass test:** One bounded interrogation on the existing LayerZero and Variational parcels; a material scope/access-control pivot triggers the Instigator re-entry under the same stable interrogation ID; all thirteen heads adjudicate the hypotheses; previous evidence and distinctions survive; the chain resumes at the next distinct source-backed candidate; no unsupported hypothesis becomes submission truth. Persist and independently fetch this receipt before claiming handoff continuity.

## Initial adversarial frame — LayerZero parcel `BR-20261003-024`

Could a failed native-drop receiver call still have its nominal amount counted as spent, while endpoint receive continues, producing a meaningful loss/lock or denial condition that an attacker can trigger and that fits the bounty program?

Historical continuity anchor: execution receipt `BOUNTY_REAPER_EXECUTION_RECEIPT_20261019_2159_SAST.md`, run `BR-20261019-2159-SAST-02`. That receipt preserved the pinned-source subclaims as killed and the parent only as C/Q3/PARKED because exact implementation/scope/attacker-trigger/impact proof were not established.

## 13-head interrogation — pass 1

1. **INSTIGATOR — OPEN A TESTABLE FRAME.** The call-failure/accounting behavior is worth checking only if an attacker-controlled route and an in-scope impact can be evidenced. The allegation is a hypothesis, not truth.
2. **SPECIFICATION — NARROW.** The pinned LayerZero Executor source identifies `nativeDrop`, `nativeDropAndExecute301`, and `nativeDropAndExecute302` as `onlyRole(ADMIN_ROLE)`. A failed receiver call is recorded in `NativeDropApplied`; nominal `param.amount` is included in `spent`; the 302 route still attempts `lzReceive` and catches its revert. These semantics alone do not prove attacker reachability or eligible loss.
3. **PROVENANCE / AUTHORITY — PRESERVE.** The prior receipt pins the source revision to `LayerZero-Labs/LayerZero-v2@9c741e7f9790639537b1710a203bcdfd73b0b9ac`. Current official program scope page says last updated 02-Oct-2026 and requires a PoC/KYC.
4. **EFFICIENCY — REJECT UNSUPPORTED REACHABILITY.** No source evidence in this parcel establishes an unprivileged trigger, a privilege modification, qualifying attacker-controlled impact, or a runnable compliant PoC. Do not expand the allegation from a code-path observation.
5. **CONTINUITY CHALLENGER A — MATERIAL PIVOT.** The live official LayerZero scope explicitly excludes impacts requiring privileged-address access without additional modifications to the privileges attributed. This changes the bounty-eligibility disposition of the privileged-only theory; it is a scope/eligibility pivot, not proof of deception or a contradiction of the pinned source.
6. **ROI / VALUE — BOUNTY CANDIDATE KILLED.** Re-entry is required because the official scope rule is material to the submission decision. Do not submit or reword this same privileged-only path to evade the rule.
7. **FAILURE NODE / DEPENDENCY GRAPH — RE-ENTRY TRIGGERED.** The stable interrogation ID remains `AMX-FORX-VFY-20261020-LZ-VARIATIONAL-REENTRY-01`; the re-entry uses new eligibility evidence, stays bounded, and carries forward the LayerZero source revision, already-killed subclaims, and the parent's Q3/PARKED status.
8. **ROUTING / EXECUTION OWNERSHIP — RE-ENTRY FRAME.** Return to existing Reaper-owned research, not a new lane. The next independent candidate is the existing Variational cross-path UUID hypothesis; it is not a promoted report.
9. **CONTINUITY CHALLENGER B — ACCESS-CONTROL CHECK.** Current Blockscout source readback for Arbitrum One confirms `Oracle.atomicDeposit` and `Oracle.batchAtomicDeposit` are gated by `onlyRole(PROVIDER_ROLE)`. The pool's `batchDepositUSDCAtomic` is `onlyOracle`. Different UUID marker mappings do not establish a public/unprivileged exploit route.
10. **VERIFICATION — PRESERVE SOURCE LIMITS.** Blockscout currently reports the SettlementPoolFactory as fully verified; the Oracle as fully verified; and the linked SettlementPool implementation as verified but **not fully verified** (`is_partially_verified=true`, `is_changed_bytecode=true`). Do not flatten those verification states. Official Variational scope is live, last updated 15-Oct-2026, states max bounty USD 100,000 and requires a PoC/KYC; its listed assets include the Settlement Pool Factory Contract.
11. **OPTIMIZATION — STOP THE SAME-QUESTION LOOP.** No nonprivileged trigger, violated intended invariant, eligible impact, or runnable local PoC was established. The Variational hypothesis remains **B / NOT PROMOTED**; no submission is justified by the marker distinction alone. More repetition of the same source question without new evidence is not progress.
12. **WEIGHTED CONTINUATION — RETURN TO THE RIGHT POINT.** Continue from the remaining independent Reaper research parcel, while separately retaining the canonical Tracker/write-readback dependency. Existing tracker remains unavailable; Queue Q1 is **UNKNOWN, NOT ZERO**. The inability to read the tracker is not evidence of an empty queue and does not justify idling other lawful source work.
13. **CONTINUITY CHALLENGER C — FINAL INVARIANT.** No external submission/report ID, award, or verified payment is claimed. LayerZero's privileged-only theory remains killed; its distinct parent remains Q3/PARKED; Variational remains B / NOT PROMOTED pending a qualifying unprivileged route, intended-invariant evidence, eligible impact and a compliant PoC. Prior truth is preserved; no candidate has been silently promoted.

## Acceptance-criteria readout

| FORX-VFY-002 criterion | Result | Observable evidence |
|---|---|---|
| Useful adversarial frame from known state | PASS | LayerZero call-failure/accounting premise isolated from exploitability and eligibility |
| Heads 2–13 prove/narrow/reject | PASS | Thirteen ordered adjudications above |
| Later material pivot triggers Instigator re-entry | PASS | Current official scope rule made privileged-only LayerZero theory ineligible; re-entry to Variational followed |
| Bounded re-entry with stable ID | PASS | `AMX-FORX-VFY-20261020-LZ-VARIATIONAL-REENTRY-01` |
| Prior continuity anchors preserved | PASS | Prior Reaper receipt/run ID, LayerZero pinned revision, killed subclaims, parent Q3/PARKED and Variational B disposition carried forward |
| Supersession distinguished from contradiction/deception | PASS | Scope eligibility pivot is recorded as a legitimate new decision constraint, not alleged misconduct |
| Unsupported allegation never becomes packet truth | PASS | No submission, no promotion, no invented attacker path or impact |
| Same-question loop terminates accurately | PASS | Variational B / NOT PROMOTED; tracker WAITING; Q1 UNKNOWN, NOT ZERO |
| Efficient enough to support action | PASS | One bounded re-entry; no duplicate worker/queue/tracker and no repeated claim submission |
| State survives restart/handoff | PASS on handoff readback | This receipt will be independently fetched and used to reconstruct the next action; no literal process restart is claimed |

## Verdicts and gates

- **FORX-VFY real-work protocol test: PASS.** The protocol produced an evidence-backed eligibility pivot, kept uncertainty explicit, prevented a false-positive bounty submission, and returned to an independent continuation point.
- **Bounty conversion / money-in: FAIL for this segment.** No submission-ready package, external report ID, accepted finding, award, or payment has been established.
- **Reaper's effective live 13-head adoption: NOT YET PROVEN.** This is a FORX-V verification receipt, not a Reaper runtime acceptance receipt.
- **Canonical tracker: TRACKER_WRITE_BLOCKED; Q1 UNKNOWN, NOT ZERO.**
- **Existing Bounty Reaper automation:** remains disabled; stored prompt still references registry v1.2 / root `6f46db56ce4b54bd4655f9e0f5e919dcdb004520d6a0acd455281841a1d7912f` and does not prove runtime adoption. No schedule or automation setting was changed in this receipt.
- **Authority effect:** this PASS releases `FORX-RP-20261006-002` for its specified bounded transfer review by existing destination T-COD. It does not itself accept the transfer, change the automation prompt, enable the automation, write to the Tracker, or authorize submission of a bounty report.

## Directive 23 — outcomes and remaining work

- **Expected outcome:** more accurate eligibility decisions, fewer repeated dead-end investigations, preserved continuity, and a clean release decision for the existing conditional Reaper transfer.
- **Owner:** FORX-V for this acceptance packet; T-COD for bounded transfer review and the existing Reaper prompt reconciliation after this gate; Reaper/authorized Tracker owner for queue reconciliation and subsequent bounty work.
- **Action:** complete the real-work 13-head challenge and trigger bounded re-entry from fresh program-eligibility evidence.
- **Dependencies:** T-COD transfer review; source/deployment-specific eligibility and PoC for any Variational candidate; authorized Tracker read/write/readback.
- **Persistence/readback:** create this receipt, independently fetch it, then update/read back the existing FORX-VFY packet and post the result to existing Root Intake issue #31.
- **Safety/preservation:** no live exploit, testnet/mainnet transaction, funds movement, spend, KYC attestation, public disclosure, external submission, duplicate queue, tracker, worker or scheduler.
- **Disposition:** protocol test PASS; overall Segment 12 remains IN_FLIGHT.
- **Remaining work:** existing T-COD to accept/reject the conditional transfer and reconcile the single existing Reaper prompt; Reaper then continues from the durable candidate/tracker state. Keep unsupported Variational hypotheses unsubmitted until their required gates are evidenced.

**TERMINAL:** NO — parent flight is still IN_FLIGHT; this acceptance result is not a flight landing.
