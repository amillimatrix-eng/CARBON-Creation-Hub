# D04 COUNTING-INTEGRITY RECONCILIATION RECEIPT
Date: 2026-10-10
Class: APPEND-ONLY EVIDENCE RECONCILIATION / NO FROZEN-TEST MUTATION
Authority: ROOT/T-GOV result-interpretation authority + MASTER/LIBRARIAN independent recomputation
Status: VERIFIED RECOMPUTATION OF EXISTING EVIDENCE; NO NEW RERUN; NO CRITERIA CHANGE

## Exact source objects read back
- Frozen criteria: `AMX/ROOT/DEMONSTRATORS/D04/D04_ENTERPRISE_CORPORATE_CONTROLS_V1.json`
  - Git blob SHA: `b392cb16ba15bef38d3f281c5144852a355b59b0`
  - frozen_at: `2026-10-10T06:10:00Z`
  - 88 controls; scoring model: critical weight 2, normal weight 1; PASS=1, PARTIAL=0.5, FAIL/NOT_EVIDENCED=0.
  - frozen pass rule: PASS requires >=90 absolute score, zero critical FAIL, and no unresolved executable queue affecting a critical control.
- Final internal self-repair vector: `AMX/ROOT/DEMONSTRATORS/D04/D04_RERUN_02_FINAL_INTERNAL_SELF_REPAIR_20261010.json`
  - Git blob SHA: `91917922e11baea512782d28efa72f8cac09e7f6`
  - 88 control records; criteria_changed=false; weights_changed=false; pass_rule_changed=false.
  - queue cutoff: pending_adapter_queue=0; ready_claims=0.
- Existing interpretation chain preserved: `ecafad6b5acd9eb4ea65c74417d057163ae1bc5e` → `78d0473dbea7dcb9bb66fa1239843f1564853118` → `99adcea49f172136637a71c86b8f5960e95c3ced` → `5aa034c35a23483ebae27d1c79ba9f8161bb5a23`.
- Current Blue State pre-supersession / evidence-floor law is at commit `7c1da8e87914ebc67956ee0fb58589946bbbefb7`.
- This receipt supplements those records; it does not rewrite or delete them.

## Independent recomputation
Raw final-vector counts from the immutable rerun object:
- PASS: 77
- PARTIAL: 6
- FAIL: 5
- NOT_EVIDENCED: 0
- Original five FAIL IDs: VAL03, VAL04, VAL05, VAL06, VAL08.
- Total frozen weight: 158 (70 critical × 2 + 18 normal × 1).
- Weighted numerator: 143.
- Original all-88 arithmetic: 143 / 158 = 90.506329...% → 90.51%, matching the stored artifact exactly.

## Measurement classification for the five disputed controls
The five stored evidence strings are absence-of-proof statements:
- VAL03: “No current accepted scope/price evidenced.”
- VAL04: “No current contracted work evidenced.”
- VAL05: “No current invoice/receivable evidenced.”
- VAL06: “No current paid/settled commercial outcome evidenced.”
- VAL08: “No complete current end-to-end revenue case exists.”

The run does not establish a bounded exhaustive measurement of the external buyer/contract/invoice/payment population for those controls. Under the existing evidence law, lack of recovered positive evidence is not evidence of the opposite state. They are therefore interpreted as `UNMEASURED_NOT_PROVEN`, not measured FAIL and not PASS. This is an interpretation/classification correction, not a change to the frozen criteria or historical raw vector.

## Corrected measured-scope arithmetic
- Excluded unmeasured weight: 10 (five critical controls × 2).
- Measured numerator remains 143.
- Measured denominator: 158 − 10 = 148.
- Measured-scope score: 143 / 148 = 96.621621...% → 96.62%.
- Measured counts: 77 PASS / 6 PARTIAL / 0 measured FAIL / 5 UNMEASURED_NOT_PROVEN.
- Frozen rule: threshold >=90 met; zero measured critical FAIL; executable queue read back at zero.
- Corrected controlling result under the frozen rule: **D04 PASS — 96.62% measured score; zero measured FAIL; five controls remain UNMEASURED_NOT_PROVEN.**

## Public-claim boundary
D04 is an AMX-defined composite enterprise-controls benchmark informed by recognized frameworks/control disciplines. This result is not ISO/COBIT/TOGAF certification, third-party attestation, or a market percentile. Do not claim accepted scope, contract, invoice, payment or settlement. Those outcomes remain unproven and must remain distinct from technical capability.

## Supersession and preservation
- Preserve the 90.51% / FAIL JSON exactly as the original all-88 raw-vector artifact and historical evidence.
- Preserve the separate RERUN_03 artifact (90.19% raw-vector score) as a distinct intermediate run; do not merge it into the RERUN_02 final trajectory point.
- The 96.62% figure is a recomputation of the existing final artifact with the five unmeasured controls excluded from the measured denominator; it is not a new execution or new test run.
- No frozen artifact, control definition, weight, pass rule, or historical score was edited.
- The current public/profile package may use 96.62% PASS only with the measured-scope label and the five `UNMEASURED_NOT_PROVEN` states visible in the detail layer.
