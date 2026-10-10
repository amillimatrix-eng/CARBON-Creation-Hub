# D04 TEST-INTEGRITY CONTROL RECONCILIATION — 2026-10-10
Supersedes no frozen test. Companion to `D04_TEST_INTEGRITY_AND_EVIDENCE_PRESERVATION_CORRECTION_20261010.md`.

## Frozen source readback
- Baseline: `AMX/ROOT/DEMONSTRATORS/D04/D04_ENTERPRISE_CORPORATE_CONTROLS_V1.json`
- Baseline blob SHA: `b392cb16ba15bef38d3f281c5144852a355b59b0`
- Post-queue-drain rerun: `AMX/ROOT/DEMONSTRATORS/D04/D04_RERUN_01_POST_QUEUE_DRAIN_20261010.json`
- Rerun blob SHA: `916516c4a7336d6d1117eeb3a278a7279ed87835`
- Rerun states `criteria_unchanged=true`, `pass_rule_unchanged=true`, queue pending=0 and READY claims=0, 82.91 absolute, 5 critical failures, overall FAIL.
- Frozen aggregation: critical controls weight 2; normal weight 1; PASS=1, PARTIAL=0.5, FAIL/NOT_EVIDENCED=0. PASS rule requires absolute >=90, zero critical FAIL, and no unresolved executable queue affecting a critical control.

## Control-by-control reconciliation

| Control | Frozen measured condition | Evidence/status in frozen baseline and rerun | Correct interpretation |
|---|---|---|---|
| VAL02 | Qualified opportunities produce substantive buyer responses | PARTIAL; RemotePuzzle response exists but many sends remain waiting/no-response | PARTIAL is supported by mixed observed responses and missing conversion reliability. Do not say no response at all. |
| VAL03 | Responses convert to accepted scope/price | Critical FAIL; no current accepted scope/price evidenced | The control explicitly measures accepted-scope conversion. FAIL is supported only within the current canonical commercial/provider evidence scope; it does not prove the Owner cannot do the work or that no unobserved external evidence exists. |
| VAL04 | Accepted scope converts to contract/commitment | Critical FAIL; no current contracted work evidenced | Same boundary: observed commercial record has no current contract. This is a current system outcome gap, not a technical capability verdict. |
| VAL05 | Contracted work converts to invoice/receivable | Critical FAIL; no current invoice/receivable evidenced | No receivable evidenced in the examined canonical scope. Do not infer a global all-account/all-rail negative without complete authoritative coverage. |
| VAL06 | Receivable converts to verified paid/settled money | Critical FAIL; no current paid/settled commercial outcome evidenced | No settlement evidenced in examined scope. Banker coverage law applies: rail-unobserved is UNKNOWN, not global zero. The control remains a failed current revenue-path acceptance only to the extent the required current settlement case is directly evaluated. |
| VAL08 | At least one closed-loop discovery→settlement case is proven | Critical FAIL; no complete current end-to-end revenue case exists | This is an explicit end-to-end acceptance condition. No complete case is in the reviewed canonical record. It does not invalidate unrelated successful build/demonstrator tests. |

## Critical distinction
The five current critical failures are not all claims that “the Matrix is incapable.” They concern the current commercial realization path. For VAL03/04, the current canonical evidence supports no accepted scope/contract. For VAL05/06, the statement is strictly bounded to the reviewed receivable/settlement evidence and must not be restated as an all-rail global zero unless authoritative coverage is complete. VAL08 is an explicit “at least one closed loop” requirement; no qualifying case is currently evidenced in the frozen record.

The frozen test uses `FAIL/NOT_EVIDENCED=0` for scoring, but these statuses remain semantically distinct. Do not relabel a missing observation as measured FAIL merely because both score zero. The current artifact specifically records VAL03/04/05/06/08 as FAIL, not NOT_EVIDENCED; a correction to that classification requires evidence that the original test did not measure the stated condition, and must be versioned separately rather than silently mutating the frozen baseline.

## Independent positive evidence remains intact
- D01/D02 results remain separate and bounded to their respective test contracts.
- Marketplace 50/50 first-run result and Search 36/36 plus 81/81 CI / recorded timing remain independent evidence.
- D04’s constrained-stack resource-efficiency score is 92.31% in the frozen baseline; it is not a substitute for the absolute score or critical-control gate.
- A commercial-outcome failure does not erase successful engineering/build evidence; successful engineering evidence does not satisfy missing commercial acceptance/settlement evidence.

## No-retrofit rule
The frozen baseline and rerun are preserved. If a test-design defect is discovered, issue a new version with an explicit changed contract and rerun it. Do not rewrite scores, thresholds, control meanings, or evidence pointers after seeing results.

## Status
This is an evidence-bound reconciliation of the six Value Realization controls read from the frozen source and the post-drain rerun. It narrows the claims to their actual evidence scope. It does not claim an all-rail settlement audit, a full external financial audit, or an external certification.
