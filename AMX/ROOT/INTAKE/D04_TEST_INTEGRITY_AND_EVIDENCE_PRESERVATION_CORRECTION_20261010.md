# D04 TEST-INTEGRITY AND EVIDENCE-PRESERVATION CORRECTION
Date: 2026-10-10
Class: MATERIAL GOVERNANCE CORRECTION / ROOT INTAKE
Scope: How D03/D04 results are interpreted and presented. This correction does not rewrite frozen tests or fabricate new results.

## Owner's controlling objection
A system cannot fail a condition that the test did not measure. A vote analogy makes the same point: one cannot classify a person as a voter/supporter based solely on an unobserved vote. Missing measurement is NOT MEASURED / UNKNOWN, not FAIL and not PASS.

## Mandatory result semantics
- PASS: the named acceptance condition was measured and satisfied.
- FAIL: the named acceptance condition was measured and not satisfied.
- NOT MEASURED: the test had no observation capable of determining the condition.
- NOT EXECUTED / BLOCKED / TIMEOUT / REFUSAL: no complete scored execution occurred.
- PARTIAL / INCOMPLETE: some required conditions were observed, but the acceptance contract was not fully evaluated.
- UNKNOWN: available evidence cannot settle the claim.
These categories must not be collapsed.

## Preserve distinct evidence dimensions
1. Frozen D03/D04 test contract and version.
2. Each individual control result and its exact measurement/evidence.
3. Whole-suite verdict, computed only by the frozen aggregation rule.
4. Resource-constrained execution context (free/free-trial models, one developer, non-enterprise infrastructure), reported as context, not as a waiver or penalty.
5. Demonstrated capability/build evidence (including previously accepted 50/50 and 36/36 first-run results and their timing evidence) preserved as independent positive evidence. A separate commercial-outcome control cannot invalidate these results.
6. Commercial outcomes (buyer acceptance, contract, invoice/receivable, settlement) are separate external outcomes. Their absence can fail a control only where that exact outcome is explicitly part of the measured acceptance contract. It does not prove technical incapability.
7. Comparative rank, public significance, chronology and causal attribution require their own sourced measurements; do not infer them from an unrelated score.

## Frozen-score protection
Do not silently change a frozen score, test threshold, control scope, aggregation rule, or milestone after seeing results. If a defect in the test design is discovered, preserve the original result and create a separately versioned corrected test. Do not retrofit the corrected interpretation into the old run.

The trajectory values previously recorded (77.22%, 82.91%, 90.51% absolute; 100% constrained-stack resource efficiency) must each remain bound to their specific test artifact, version, denominator and aggregation rule. They must not be combined into one narrative without that binding. The whole-suite verdict remains whatever the controlling frozen acceptance rule computes; do not turn it into PASS based on resource efficiency, and do not use the whole-suite FAIL to erase individual PASS evidence.

## Current evidence boundary
The canonical D04 rerun record currently describes five critical Value Realization controls as FAIL because real buyer acceptance, contract, receivable, settlement, and a complete discovery-to-settlement case were not evidenced. Intake must verify, per control, that each was actually part of the frozen measured acceptance condition. Where it was not measured, reclassify that control to NOT MEASURED/UNKNOWN in a new correction record, without rewriting the original frozen run. Where it was explicitly required and the test measured its absence, retain FAIL and state the precise evidence boundary.

## Anti-drift / assumptions
- No inferred failure from a missing data source.
- No inferred success from a narrative, merge, scheduler-enabled state, or patch recommendation.
- No inferred technical failure from absent buyer/payment outcomes.
- No inferred external-market superiority without a defined comparison population.
- No chronology promotion without attributable dated primary evidence.
- No resource constraint may be used to discount proven capability or waive a failed control.
- A later correct conclusion does not erase the earlier assumption that produced it.
- Preserve contradictory records, supersessions, and executor attribution; never silently rewrite history.

## Required governance action
ROOT/T-GOV and the relevant test owner must reconcile each of the five critical controls against the frozen D04 contract and record, for each: control ID, exact requirement, exact observation, whether measured, denominator/evidence pointer, result class, and aggregation effect. FORX may recommend corrections but may not unilaterally alter the frozen acceptance contract. T-MED must publish only the reconciled, artifact-bound trajectory and may not collapse NOT MEASURED into FAIL or PASS.

## Status
This file records the Owner's material objection and mandatory correction path. It does not claim the per-control reconciliation is already complete. Acceptance requires durable readback of the reconciled table and verification that downstream T-MED presentation references it.
