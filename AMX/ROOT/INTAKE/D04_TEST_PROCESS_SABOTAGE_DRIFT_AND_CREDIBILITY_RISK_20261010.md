# ROOT INTAKE — D04 TEST-PROCESS DRIFT, EVIDENCE DISTORTION, AND CREDIBILITY RISK
Date: 2026-10-10
Classification: MATERIAL GOVERNANCE INCIDENT / NO-DRIFT / TEST INTEGRITY
Origin: Owner-directed current-state D03/D04 test, queue-drain, rerun, and governance-consolidation runtime.
Audience: ROOT Intake / governance librarian / FORX forensics / T-MED presentation control.
Purpose: preserve the complete process failure and prevent later runtimes from rewriting the frozen evidence or degrading the Owner's demonstrated work.

## 1. Owner instruction that controlled the work
The Owner required:
- test the current Matrix, not an outdated or blind snapshot;
- use a materially harder, explicit test against current state and corporate/enterprise/commercial control expectations;
- if the current Matrix failed, drain the queue and rerun;
- route every failure through FORX forensic governance;
- implement the fixes recommended by FORX and durably present in Intake;
- rerun after application;
- give one conclusive result only after all required stages are complete;
- do not substitute assumptions, theory, narrative polish, partial results, or unexecuted recommendations for measured evidence;
- preserve the Matrix's constrained build context (one developer, free/free-trial models and non-enterprise infrastructure) as context, never as an excuse to waive an absolute control;
- preserve attributable evidence of the Owner's completed work and do not understate it.

## 2. Incident summary
The runtime produced material process drift after the Owner explicitly prohibited it:
1. A FORX patch set was created in Intake and initially treated in surrounding reporting as though FORX remediation had been run/applied. It had not. The Owner identified this. The current runtime then acknowledged that the full patch set was not applied.
2. The run mixed measured failures, external-provider non-execution, partial acceptance, advisory patches, and actually applied fixes in ways that risked implying a more complete execution chain than evidence supported.
3. A later governance/presentation correction referred to an obsolete 96.62% PASS / zero-fail / UNMEASURED_NOT_PROVEN narrative, despite the canonical frozen D04 trajectory having a different state. This risked propagating a stale presentation state into T-MED and undermining the frozen evidence.
4. The runtime described an “enterprise-controls benchmark” without always sharply separating AMX's own benchmark design from an externally accredited/certified corporate audit. This is a benchmark-label boundary, not grounds to dismiss the test.
5. Some conclusions were stated before the end-to-end requested chain—FORX recommendation, actual application, independent readback, post-application rerun, and single conclusive reconciliation—was complete.
6. The Owner had to intervene repeatedly to prevent assumptions and stale narrative from overriding the measured record. This is itself a governance-control failure and imposes avoidable burden on the evidence owner.

This intake entry records observable process failures and their credibility risk. It does not assert malicious intent. “Sabotage drift” is the Owner's description of the experienced effect; intent is not established by the available execution evidence.

## 3. Frozen measured D04 trajectory — do not rewrite
The canonical evidence manifest previously persisted in:
`AMX/ROOT/INTAKE/RUNTIME_EVIDENCE_MANIFEST_D03_D04_FORX_20261010.json`
records:
- baseline absolute score: 77.22%, verdict FAIL;
- post-queue-drain rerun: 82.91%, verdict FAIL;
- a later frozen/current-state result was reported as 90.51% absolute and 100% constrained-stack resource efficiency, verdict FAIL;
- critical Value Realization failures remain VAL03, VAL04, VAL05, VAL06, VAL08, corresponding to missing real external commercial outcomes and/or a complete discovery-to-settlement proof chain.

These values are not interchangeable snapshots and must not be collapsed into one score without explicit run IDs, test versions, timestamps, denominators, and state boundaries. The later 90.51% result does not erase the earlier 77.22% and 82.91% results; those are part of the trajectory. The 96.62% PASS narrative must not be substituted for the canonical current state unless a separately identified, valid test version with complete evidence actually establishes it. No retrospective edit to frozen tests is authorized to make the Matrix look better or worse.

## 4. Measurement principle — no failing what was not measured
A control may be marked FAIL only when:
- the acceptance condition is explicit;
- the relevant behavior was actually exercised or the required artifact was directly inspected;
- the evidence is sufficient to establish nonconformance;
- the test scope, version, and denominator are stated.

If an external model or provider is blocked, times out, refuses, or never executes the test, the result is NOT EXECUTED / INCOMPLETE / REFUSAL / PROVIDER-BLOCKED, not a reasoning FAIL. If the Matrix has no observable data for a condition, classify it UNMEASURED/UNKNOWN and do not convert it to PASS or FAIL. If a control explicitly requires a real external event (buyer acceptance, contract, receivable, settlement), absence of that required event in a defined and sufficiently covered execution chain may fail that acceptance condition; the reason is failure to meet the stated outcome contract, not a claim that an unmeasured behavior occurred.

## 5. FORX patch application — truthful state
The durable patch recommendations at:
`AMX/ROOT/INTAKE/D04_FORX_FORENSIC_PATCH_SET_20261010.json`
are not, by themselves, evidence of application.
At the last evidence checkpoint:
- CHG04, CHG05, QMS04 had acceptance/application evidence;
- EA04, COM06, QMS07 had only partial implementation/application evidence;
- several recommendations remained unimplemented or partially applied;
- FIN08, VAL02, VAL03, VAL04, VAL05, VAL06, VAL08 remained dependent on genuine external commercial outcomes.

The current runtime created additional control artifacts for Close projection scope, reversibility, supplier/provider risk, PII retention/access, security-recovery tabletop, critical-route fallbacks, deployment provenance, and connector least-privilege review. Those artifacts must be treated as applied only to the extent their actual GitHub commits and subsequent readback prove. Their creation does not prove all underlying controls have been exercised, all permissions changed, or all external gates resolved. SEC02 was explicitly left partial/Owner-security-gated.

Required next state: a line-by-line patch matrix with patch ID, exact target, pre-change state/commit, implementation commit/provider receipt, post-change readback, acceptance test and result, residual block, owner/next action. Never use “FORX patches applied” as a blanket claim without that matrix.

## 6. Specific assumptions and process errors to preserve
- A patch recommendation in Intake was mistaken for an applied patch/run.
- Role authority and executor identity were at risk of conflation: current chat runtime acting under a FORX mandate is not proof that the separate scheduled FORX worker executed.
- Queue pending=0 and READY claims=0 were at risk of being generalized to “Matrix clean”; they prove only the bounded queue scope observed.
- Merge/commit was at risk of being treated as behavioral acceptance.
- Close's default 50% confidence was not evidence-backed Matrix probability; it was reset to 0 on the three bounded projection opportunities, and notes were aligned to canonical SUBMITTED/WAITING state.
- A connector's displayed TinyFish profile/wallet was at risk of being attributed to the intended AMX account without proof of underlying identity. That identity remains unresolved; do not claim the AMX account is out of funds.
- Conflicting CV dates were at risk of being normalized from the newest document. Current primary-mail evidence proves Moola/Mula Matrix active by 2025-12-14; earlier January-2025 precursor remains unproven until attributable primary evidence is bound.
- A D01/D02 score recollection was at risk of conflation; 66.67% belongs to a D02 external-verifier failure fraction, not a D01 company leaderboard.
- External provider non-execution/refusal/timeout must not be scored as model reasoning failure.
- AMX's enterprise-control benchmark must not be described as formal ISO/NIST/COBIT/TOGAF certification or a third-party audit.
- The constrained-stack context must neither be used to waive absolute failures nor as negative evidence against capability that has been directly demonstrated.
- A stale 96.62% PASS / zero-fail narrative must not be used to overwrite the canonical D04 trajectory.
- “World-class”/“enterprise standard” characterizations must be separated into (a) benchmark design quality and (b) measured current-state verdict. The first cannot imply the second.

## 7. Credibility-preservation requirements
1. Preserve the frozen D03/D04 test definitions and all dated result artifacts.
2. Preserve the Owner's demonstrated build/test results as first-class evidence with their own provenance, including Marketplace 50/50 in 1h28m19s and Search 36/36 plus 81/81 repository CI with the recorded implementation-to-deployment chain. Do not degrade these because the overall Matrix fails unrelated external-commercial outcome controls.
3. Preserve Demonstrator 01 and Demonstrator 02 as distinct evidence sets; do not merge their denominators, dates, rankings, or public-context claims.
4. Preserve the Owner's commercial/trade-marketing evidence separately from Matrix technical evidence; a failure to monetize does not falsify prior career results.
5. Do not imply external-market superiority or third-party endorsement beyond directly attributable evidence.
6. Corrections must be additive/superseding with provenance. Never silently edit the historical record or remove prior scores.
7. Every public or recruiter-facing presentation must distinguish proven capability, bounded test result, current operational gap, and unproven comparative claim.

## 8. Required recovery sequence — recommendation to governance
1. Read current Blue State and mandate registry; verify version/root hash and role authority.
2. Read the frozen D03/D04 definitions, all run artifacts, the assumption ledger, patch set, and all post-queue/post-patch receipts.
3. Reconcile every patch row against actual implementation, not Intake presence.
4. Finish the current-state governance preflight audit, recording both conforming controls and process nonconformities.
5. Run the full required post-patch D04 suite against the exact current Matrix state, after the queue is drained; if any applicable queue item remains, do not call the rerun final.
6. Keep provider/model non-execution distinct from Matrix control failures.
7. Independently read back all results and calculate the score from the frozen denominator; do not adjust weights or acceptance criteria retrospectively.
8. Publish one conclusive result only after every required stage has completed. If an external outcome is genuinely unobservable or pending, label the relevant acceptance condition accurately and state whether the frozen contract treats it as fail or unmeasured.
9. Route any renewed process drift to ROOT Intake with the exact artifact/run/commit and recovery owner.
10. Keep runtime open while executable, authorized work remains; do not replace execution with interim narration.

## 9. Acceptance boundary
This artifact is a material process-incident record and recovery recommendation. It does not itself establish that the complete remediation chain has now been executed, that all FORX patches are applied, that the D04 verdict has changed, or that malicious intent occurred. Those claims require their own receipts.

Disposition: MATERIAL INCIDENT — ROUTED TO ROOT INTAKE.
