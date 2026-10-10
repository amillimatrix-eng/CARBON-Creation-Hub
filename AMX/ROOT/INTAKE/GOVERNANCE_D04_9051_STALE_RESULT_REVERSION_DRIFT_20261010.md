# GOVERNANCE — D04 90.51 STALE RESULT REVERSION DRIFT — SEPARATE INCIDENT

**Date:** 2026-10-10  
**Status:** **OWNER IDENTIFIED / ACCEPTED DRIFT INCIDENT / BLUE STATE PREVENTION RULE REQUIRED**  
**Class:** Supersession / evidence chronology / stale projection drift  
**Incident:** Later T-MED projection resurrected the superseded D04 `90.51% / FAIL` interpretation.

## Incident

A later Notion/T-MED block labelled:

**MATERIAL SUPERSESSION — D04 CURRENT SELF-REPAIR STATE**

asserted:
- `90.51% absolute`;
- D04 verdict `FAIL`;
- VAL03 / VAL04 / VAL05 / VAL06 / VAL08 as genuine critical failures;
- the earlier 96.62% PASS wording as superseded.

The block was later in page chronology, but its evidence source was the **older** final-internal rerun artifact:
- commit `cb5713fc0d1adb5c1b1f326b3aa54437752a30bf`;
- persisted at 2026-10-10T07:17:18Z.

That rerun's result interpretation had already been superseded by later durable corrections:
- `ecafad6b5acd9eb4ea65c74417d057163ae1bc5e` — corrected `UNMEASURED / NOT EVIDENCED / UNKNOWN != FAIL`;
- `78d0473dbea7dcb9bb66fa1239843f1564853118` — Critic correction;
- `99adcea49f172136637a71c86b8f5960e95c3ced` — Owner clarification: **D04 PASS under the unchanged frozen rule**;
- `5aa034c35a23483ebae27d1c79ba9f8161bb5a23` — canonical weighted-continuity ledger aligned to **D04 BENCHMARK PASS — 96.62%**.

Therefore the later 90.51 block was not newer evidence. It was a **newer projection of older superseded evidence**.

## Drift finding

**LATER TIMESTAMP != LATER AUTHORITY.**

**NEWER PROJECTION OF OLDER EVIDENCE != NEWER EVIDENCE.**

A downstream surface may not supersede a current corrected result merely because the downstream text was written later.

Before declaring supersession, the writer must resolve:
1. source artifact chronology;
2. current controlling interpretation;
3. explicit supersession records;
4. current evidence ledger/authority state;
5. whether the alleged newer state contains genuinely newer contrary evidence.

The 90.51 block failed this test.

## Correct current state

The controlling result remains:

**D04 ENTERPRISE-CONTROLS BENCHMARK — PASS — 96.62% — ZERO MEASURED FAIL.**

The five value-realization controls remain `UNMEASURED_NOT_PROVEN` because the run did not validly measure them. They are not participant failures.

This correction does not delete the 90.51 artifact. The original rerun and stale projection remain provenance of the examiner/projection drift.

## Required prevention rule

A current surface must never supersede a durable corrected state using an older source without new contrary evidence.

Required pre-supersession sequence:

**RECOVER SOURCE CHAIN → ORDER EVIDENCE BY AUTHORITY/SUPERSESSION, NOT PAGE TIMESTAMP → READ CURRENT LEDGER → VERIFY CONTRARY EVIDENCE → ONLY THEN SUPERSEDE.**

If a later-written page cites an earlier source and conflicts with a later controlling correction, classify the page as **STALE PROJECTION / DRIFT** until reconciled.

## Relationship to CDD

This incident is separate from Capability Downselling Drift.

- CDD concerns representation below what current evidence supports.
- This incident concerns **supersession failure**: stale evidence was resurrected as current truth.

The stale reversion also caused downselling downstream, but the causal defect is distinct and must remain independently visible.

## Evidence references

- `AMX/ROOT/DEMONSTRATORS/D04/D04_RERUN_02_FINAL_INTERNAL_SELF_REPAIR_20261010.json`
- `AMX/ROOT/INTAKE/D04_RESULT_INTERPRETATION_OWNER_CLARIFICATION_20261010.md`
- `AMX/ROOT/INTAKE/EVIDENCE_WEIGHTED_CONTINUITY_LEDGER_20261010.json`
- T-MED Notion preflight page `3f58f8b5-6cd7-8134-b03e-ef503e113ccf`
- correction commits listed above.

**OWNER DISPOSITION: RECORD THIS AS A SEPARATE D04 DRIFT INCIDENT AND MERGE THE PRE-SUPERSESSION PREVENTION RULE INTO BLUE STATE.**
