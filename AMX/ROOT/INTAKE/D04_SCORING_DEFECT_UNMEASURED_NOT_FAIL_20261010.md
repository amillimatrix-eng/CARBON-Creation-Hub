# ROOT INTAKE — D04 SCORING DEFECT: UNMEASURED != FAIL

**Date:** 2026-10-10
**Class:** GOVERNANCE / BENCHMARK INTEGRITY / TEST-CORRECTION
**Source:** D04 enterprise-controls benchmark + post-queue-drain rerun
**Status:** MATERIAL TEST DEFECT — CORRECTION REQUIRED

## Defect

D04 baseline scoring defined:

`PASS=1, PARTIAL=0.5, FAIL/NOT_EVIDENCED=0`.

That is not compatible with the current Weighted Continuity / Benchmark Integrity rule when `NOT_EVIDENCED` means the run did not establish the condition.

A missing measurement cannot be converted into negative evidence.

**UNMEASURED / NOT EVIDENCED / UNKNOWN != FAIL.**

The same error affected five commercial-value controls whose evidence text said only:
- "No current accepted scope/price evidenced";
- "No current contracted work evidenced";
- "No current invoice/receivable evidenced";
- "No current paid/settled commercial outcome evidenced";
- "No complete current end-to-end revenue case exists."

Those statements show that the run did not recover proof of those outcomes. They do not, by themselves, prove the opposite proposition across all relevant external reality.

## Correct classification law

- PASS = defined condition directly evidenced.
- FAIL = defined condition was actually observable/testable in the bounded test and contrary/noncompliant evidence was observed.
- PARTIAL = defined subconditions were measured, some met and some not met.
- UNMEASURED / NOT PROVEN / UNKNOWN-HOLD = evidence cannot establish the condition either way.
- UNRANKED / BENCHMARK NOT ESTABLISHED = comparative population/benchmark does not exist or is not defensibly applicable.

Only measured PASS/PARTIAL/FAIL controls belong in the scored denominator.

## Reclassification of post-drain D04

Excluded from the measured denominator:
- SEC07 — NOT_EVIDENCED -> UNMEASURED_NOT_PROVEN.
- VAL03 — FAIL -> UNMEASURED_NOT_PROVEN.
- VAL04 — FAIL -> UNMEASURED_NOT_PROVEN.
- VAL05 — FAIL -> UNMEASURED_NOT_PROVEN.
- VAL06 — FAIL -> UNMEASURED_NOT_PROVEN.
- VAL08 — FAIL -> UNMEASURED_NOT_PROVEN.

This does NOT convert those controls into PASS.
It preserves the truthful state: **NOT PROVEN BY THIS RUN**.

## Corrected arithmetic for the post-queue-drain run

Using the same frozen control weights and the same observed PASS/PARTIAL/FAIL statuses for all genuinely measured controls:

- measured weighted numerator = 131;
- measured denominator weight = 147;
- corrected measured score = **89.12%**;
- the six controls above are excluded from numerator and denominator;
- no pass/fail threshold or other control status is changed by this correction.

## Governance consequence

The prior 82.91% score and "five critical failures" must remain provenance as the original flawed scoring artifact, but must not be treated as the controlling interpretation.

This correction does NOT yet declare D04 PASS or FAIL overall. The remaining governance audit must establish:
1. whether D04 was correctly classified as an AMX-defined milestone / external-framework-informed benchmark rather than a formal certification;
2. whether the 90% threshold was prospectively defined and valid;
3. whether every remaining PARTIAL/FAIL was genuinely measured;
4. whether mandate-preflight/start-receipt requirements were satisfied;
5. whether the test respected no-retrospective-goalpost and weighted-continuity rules.

## Analogy preserved

Absence of an observed act is not evidence of the opposite identity/state. A person not voting is not evidence that they support a particular party. Likewise, "no accepted scope found in this bounded run" is not equivalent to "accepted scope does not exist."

## Required disposition

ROOT / Governance should mark the original D04 scoring model as defective on this point and consume this corrected measurement law for the final audit/rerun.

No historical evidence is deleted or rewritten.
