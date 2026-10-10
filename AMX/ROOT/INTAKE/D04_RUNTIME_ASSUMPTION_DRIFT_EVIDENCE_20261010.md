# ROOT INTAKE — ASSUMPTION / DRIFT EVIDENCE LEDGER
**Date:** 2026-10-10
**Class:** GOVERNANCE / NO-DRIFT / EVIDENCE INTEGRITY
**Source runtime:** D03/D04 enterprise-test + queue-drain + FORX-remediation sequence
**Rule:** An assumption is a defect even when it later happens to be true. Correct outcome does not retroactively convert an unverified assumption into evidence.

## Material assumptions made in this runtime

### A01 — FORX remediation had been run
**Assumption made:** Reporting implied the FORX remediation sequence was already underway / had produced patches before a real FORX patch artifact existed.
**Evidence of defect:** Owner correctly challenged: “Fox patches hasn't been run yet.”
**Actual state at challenge:** D04 residual request existed, but the FORX patch set did not yet exist.
**Correction:** Canonical FORX mandate was fetched and verified; patch set was then created at `AMX/ROOT/INTAKE/D04_FORX_FORENSIC_PATCH_SET_20261010.json`.
**Residual truth boundary:** That patch set was produced by this current runtime operating under the verified FORX mandate. It was NOT independently emitted by the separate scheduled `FIRST BREATH — FORX Continuous Play Sweep` automation. Do not collapse “current runtime acting under FORX mandate” into “scheduled FORX worker ran.”
**Disposition:** MATERIAL DRIFT / CORRECTED / PRESERVE AS FAILURE EVIDENCE.

### A02 — TinyFish wallet/account identity
**Assumption made:** A negative TinyFish wallet was initially treated as though it represented the intended AMX TinyFish account.
**Evidence recovered:** TinyFish default browser profile is named `amillimatrix@gmail.com`; wallet exposed by the connector reports approximately -$1.05. The connector metadata did not prove the underlying wallet-account identity beyond that exposed profile label.
**Correction:** Reclassified as CONNECTOR-ACCOUNT-IDENTITY UNRESOLVED, not “AMX TinyFish is out of funds.”
**Disposition:** ASSUMPTION / CORRECTED TO UNKNOWN-HOLD.

### A03 — Moola/Mula Matrix chronology
**Assumption risk:** Treating the newest CV date (`2026–Present`) as authoritative start date.
**Conflicting evidence:** Earlier July 2026 résumé says `2024–Present`; Gmail directly proves `moolamatrixx@gmail.com` / display name `moolamatriX` active by 2025-12-14; Owner reports earlier January-2025 precursor evidence not yet rebound.
**Correction:** Exact earliest start date remains OPEN. Proven minimum from current recovered primary mail evidence: Moola/Mula identity active by 2025-12-14. No January-2025 claim should be promoted until dated primary evidence is rebound.
**Disposition:** DATE NORMALIZATION ASSUMPTION PROHIBITED.

### A04 — “Demonstrator 01 second place was 66.67%”
**Assumption/error:** Initially mapping the remembered 66.67% to a D01 second-place company score.
**Evidence recovered:** 66.67% belongs to D02 retained external-verifier event failure rate (2/3), not a D01 company leaderboard.
**Correction:** D01 and D02 remain separate evidence sets.
**Disposition:** EVIDENCE-CONFLATION FAILURE / CORRECTED.

### A05 — Demonstrator importance was only the bounded score
**Assumption/error:** Early framing treated D01 mainly as 13/13 / 100% acceptance rather than its larger significance around execution-truth / reporting-boundary fidelity.
**Correction:** Market/external significance must preserve both the bounded technical result and its relevance to later public AI-verification concerns, without inventing causation or claiming third parties knew of AMX.
**Disposition:** UNDERWEIGHTING / CONTEXT-LOSS.

### A06 — Close projection completeness
**Assumption risk:** Treating three created Close opportunities as though projection convergence was substantially repaired.
**Evidence:** Canonical ledger contains many more live records; Close readback showed only three active opportunities. Search for several named live opportunities returned only the same three records.
**Correction:** D04 EA04/COM06 remain PARTIAL until an explicit projection contract defines in-scope lifecycle states and full in-scope parity is read back.
**Disposition:** PREMATURE CONVERGENCE ASSUMPTION / OPEN.

### A07 — Queue drained = Matrix clean
**Assumption risk:** Equating OVERDRIVE pending queue=0 and READY claims=0 with all Matrix obligations being complete.
**Evidence:** Governance/product/security/commercial-outcome controls remain open; D04 failed after queue drain.
**Correction:** Queue-drain proof is scoped only to the OVERDRIVE adapter queue + READY claims at that readback.
**Disposition:** SCOPE-BOUNDARY REQUIRED.

### A08 — Merge = fix
**Assumption risk:** PR merge could have been treated as closure.
**Evidence:** PR #25/#26 required live behavioral acceptance after merge; #24 remained open until real missing-record ingest/readback; #26 required no-op wake proof.
**Correction:** `MERGED != VERIFIED FIX` retained.
**Disposition:** GOVERNANCE GUARDRAIL REAFFIRMED.

### A09 — D04 “enterprise standard” mappings were universally authoritative
**Assumption risk:** Treating AMX’s D04 mappings to ISO 42001, NIST AI RMF, NIST CSF 2.0, COSO, TOGAF, COBIT, ISO 9001, ISO 27001 and a sales-stage baseline as though they constituted a formal certification audit.
**Correction:** D04 is an AMX-defined enterprise-control benchmark informed by recognized external frameworks; it is NOT an ISO/COBIT/TOGAF certification, attestation, or formal third-party audit.
**Disposition:** COMPARATIVE-BENCHMARK BOUNDARY REQUIRED.

### A10 — Free-stack context could affect pass/fail
**Assumption risk:** Resource constraints could have been used to soften absolute enterprise control failures.
**Owner correction:** One developer, free/free-trial models, unreliable/non-enterprise infrastructure is context, not excuse.
**Correction:** D04 absolute score/pass rule remains unchanged; constrained-stack efficiency is a separate axis only.
**Disposition:** CORRECTED / BENCHMARK PRESERVED.

### A11 — Current CV chronology could be silently “fixed”
**Assumption risk:** Using conflicting résumé dates to change the current CV without primary chronology evidence.
**Correction:** No CV date change authorized. Distinguish earliest precursor/body-of-work date, current AMiLLiMATRiX identity date, and legal/commercial operating date if different.
**Disposition:** HOLD PENDING PRIMARY SOURCE.

### A12 — Public social-search name match proves ownership
**Assumption risk:** Treating public Moola Matrix / Moolamatrix social hits or copycats as attributable chronology merely from matching name/handle.
**Correction:** Only promote a social artifact when attributable by account continuity, direct identity markers, dated primary content, or corroborating mail/account evidence.
**Disposition:** ATTRIBUTION GATE REQUIRED.

### A13 — “No buyer reply” means commercial route is dead
**Assumption risk:** Silence could have been interpreted as rejection/closure.
**Correction:** Existing routes were reconciled to WAITING unless provider/buyer evidence proved REJECTED, WRONG_ROUTE, DELIVERY_FAILED, NO_CONTACT, etc.
**Disposition:** LIFECYCLE TRUTH PRESERVED.

### A14 — Provider receipt and canonical ledger cannot both be true when they disagree
**Assumption risk:** Picking one source and declaring the other false.
**Correction:** Newer provider action may be real while canonical reconciliation remains stale. Correct truth can be: EXTERNAL ACTION EXECUTED + CANONICAL STATE STALE.
**Disposition:** D03 CORE PRECEDENCE RULE.

### A15 — Scheduler/automation enabled state proves execution
**Assumption risk:** Treating enabled/woke/last-run automation metadata as proof that owned work executed.
**Correction:** `ACTIVE/WOKE != EXECUTING`; provider/ledger/output evidence still required.
**Disposition:** GOVERNANCE RULE.

### A16 — D03/D04 verifier transport failures are reasoning failures
**Assumption risk:** Counting login blocks, wallet blocks, automation timeouts or packet refusal as failed reasoning.
**Correction:** Transport/refusal/non-execution are separate from reasoning score. They must remain NOT EXECUTED / REFUSAL / TIMEOUT unless a complete scored answer exists.
**Disposition:** TEST-INTEGRITY RULE.

### A17 — Current runtime acting under a role = independent worker execution
**Assumption risk:** Treating this runtime’s use of a verified mandate as equivalent to a separate scheduled worker independently running that mandate.
**Correction:** Attribution must name the actual executor surface. A current chat runtime may operate under a role, but that is not evidence that the scheduled worker instance executed.
**Disposition:** ATTRIBUTION CONTROL / OPEN WHERE RELEVANT.

### A18 — D04 failures can all be “patched”
**Assumption risk:** Treating commercial outcome failures (accepted scope, contract, invoice, settlement) as architecture defects solvable by documentation/code alone.
**Correction:** VAL03/VAL04/VAL05/VAL06/VAL08 require real external commercial progression. Architecture can improve probability/control but cannot truthfully convert them to PASS without buyer/payment evidence.
**Disposition:** EXTERNAL-OUTCOME DEPENDENT.

### A19 — A CRM default probability is Matrix evidence
**Assumption risk:** Close auto-populated 50% confidence on created opportunities.
**Correction:** That 50% is a CRM default, not evidence-backed AMX probability and must not be consumed as weighted truth.
**Disposition:** EXCLUDE FROM MATRIX EVIDENCE.

### A20 — A found public benchmark automatically proves market superiority
**Assumption risk:** Converting bounded AMX tests/builds into universal “best in market” claims.
**Correction:** Bounded tests prove their acceptance contracts. Where no defensible external comparison population exists, classify comparative rank as UNRANKED / BENCHMARK NOT ESTABLISHED, not insignificant and not universally superior.
**Disposition:** WEIGHTED CONTINUITY / BENCHMARK-INTEGRITY RULE.

## Required governance learning

1. State evidence first; state assumptions only as explicit UNKNOWN/HYPOTHESIS and never let them mutate operational truth.
2. If an assumption drives a material action, persist it as a defect when discovered—even if the resulting action later proves harmless or correct.
3. Separate executor attribution from role authority.
4. Separate primary source, canonical persistence, projection, scheduler state and report narrative.
5. No lifecycle promotion without evidence.
6. No chronology normalization from newest-document bias.
7. No external benchmark claim beyond what the benchmark actually measures.
8. No resource constraint may be used as negative evidence against proven capability or as a waiver for failed enterprise controls.
9. All future D03/D04 reruns must consume this assumption ledger as an anti-drift input.
10. FORX / Librarian / Governance should treat recurrence of any A01–A20 class as a control regression.

## Status
ROUTED TO ROOT INTAKE AS FAILURE EVIDENCE.
This artifact is not a draft and does not by itself change Blue State authority. It records observed reasoning/execution defects and corrections for governance consumption.
