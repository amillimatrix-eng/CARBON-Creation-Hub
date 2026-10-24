# FORX flight-register continuity repair — current-base proposal

**Status:** PROPOSED FOR ROOT/T-GOV REVIEW; NOT MERGED  
**Base:** `82436afb57905afeccba8918f74f8b23794ed6ef`; current branch `proposal/forx-flight-register-continuity-20261013-r2`  
**Root route:** [Issue #31](https://github.com/amillimatrix-eng/CARBON-Creation-Hub/issues/31)

## Current-source readback
- Register blob `62db9ad0018a4c1934835c4b419de23c63ee929d`, 73 JSONL events across 2 flight IDs. Latest actual checkpoint: `AMX-FLT-20261012-DSYNC-145440-9fb44f0c:CHECKPOINT:SEGMENT-14:OWNER-CORRECTED-TINYFISH-OUTLOOK-ROUTE-20261021T030606Z`; source bytes unchanged.
- The current Index was stale on both current 200K acceptance and register checkpoint. This proposal now records the accepted 200K receipt: 200,000 nodes, 200/200 exact partition hashes, 200,000 unique source IDs; durable receipt `23c11566645475d8feb329c36ad654b422439625`; restart/resume still OPEN.
- Blue State `73d8131032a36757acfbd2762861b52c73eb6b3f`; Registry v1.3 `bcfd1f422bd25ba852666a538712828d594759e8`, root `96c0beb3328ebefc16286d93a7baadc0ff4be0a17c1e6a8718b89de94f58df1a`; authority unchanged.
- One real chain defect remains: Segment-11 checkpoint `AMX-FLT-20261012-DSYNC-145440-9fb44f0c:CHECKPOINT:SEGMENT-11:CURRENT-PREFLIGHT-OUTPUT-AND-CASH-IN-20261014T182303` references absent resume `AMX-FLT-20261012-DSYNC-145440-9fb44f0c:RESUME:SEGMENT-11:WORKER-OUTPUT-RECOVERY-AND-CASH-IN-20261013`. No historical event is fabricated, and the live validator should fail closed until root disposition.
- Three rows that labelled `FORX-20261013-1646Z-01` an existing registered flight (segments 02–04) are corrected to historical-report/provenance anomalies; no LAUNCH exists.

## Bounded change
Repoint the current Index to the actual latest checkpoint, reconcile the stale 200K statement, reclassify historical flight rows, and retain standard-library validator + path-scoped CI + missing-prior-event regression. The register itself and governing authority files are not changed.

## Acceptance gate
ROOT/T-GOV resolves the exact missing prior event by source evidence or an explicit governed disposition. MASTER/LIBRARIAN verifies full-register blob pointer; T-COD reviews current-head tests/CI. This PR is not self-approved and stays open while current-source integrity flags the absent prior event.

## Directive 23
- **Expected outcome:** current Index truth; stale flight claim corrected; real chain defect remains visible; 200K durable PASS accurately separated from restart/resume.
- **Owner:** ROOT/T-GOV, MASTER/LIBRARIAN, T-COD, FORX.
- **Action:** inspect current-base diff and live-data validator; disposition prior-event gap.
- **Dependencies:** missing Segment-11 RESUME event disposition.
- **Evidence/readback:** register/index/Blue State/Registry hashes and current 200K receipt.
- **Safety/preservation:** no register rewrite, fabricated event, authority/schedule/task changes.
- **Disposition:** OPEN / ROOT REVIEW REQUIRED, not queue closure.
- **Remaining work:** missing prior-event disposition, fresh CI, independent review, post-merge readback.

## 2026-10-21 ROOT source reconciliation — identifier typo, not absent RESUME event

The current-main DYNAMIC_FLIGHT_PATH_REGISTER.jsonl was reread byte-for-byte at blob 62db9ad0018a4c1934835c4b419de23c63ee929d, 73 non-empty JSONL events.

- Line 39 contains the exact source event: AMX-FLT-20261012-DSYNC-145440-9fb44f0c:RESUME:SEGMENT-11:WORKER-OUTPUT-RECOVERY-AND-CASH-IN with event_type=RESUME, recorded_at_utc=2026-10-13T14:29:53.808Z, and a valid link to the Segment-10 landing.
- Line 40's CHECKPOINT points to AMX-FLT-20261012-DSYNC-145440-9fb44f0c:RESUME:SEGMENT-11:WORKER-OUTPUT-RECOVERY-AND-CASH-IN-20261013. The referenced string differs from the existing event ID only by the added -20261013 suffix. The register's event bytes remain unchanged.
- Therefore the evidence establishes an existing RESUME record plus a wrong prior-event pointer string; it does not establish a missing real-world resume or authorize fabricating/backdating one.
- Proposed governed disposition for ROOT/T-GOV: classify this as DFP-PRIOR-REF-ID-MISMATCH, with canonical referenced event ID above and the observed bad string preserved as the original pointer. Choose explicitly between (A) append-only correction event defining the old string → existing event mapping with exact acceptance semantics, or (B) a fail-closed finding that the validator should report until a formal correction is authorized. Do not silently rewrite line 40. After disposition, run the validator and all tests against current main, refresh this PR base, and keep it open until review/readback.

Updated status: source event found; pointer defect precisely isolated; ROOT/T-GOV disposition, current-head CI, independent review and post-merge readback remain OPEN. The proposed code does not self-approve this governance correction.