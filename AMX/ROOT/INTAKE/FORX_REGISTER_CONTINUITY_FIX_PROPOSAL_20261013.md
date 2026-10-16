# FORX continuity repair proposal — current-main reconciliation

**Status:** PROPOSED FOR ROOT REVIEW; NOT MERGED  
**Prepared:** 2026-10-13  
**Review branch:** `proposal/forx-flight-register-continuity-20261013-r2`  
**Existing Root route:** [Issue #31](https://github.com/amillimatrix-eng/CARBON-Creation-Hub/issues/31)  
**Controlling rule:** Blue State Category A — Dynamic Flight Path Continuity. This proposal does not alter mandate authority.

## Current-main finding

The defect remains present on the latest inspected `main`:

- Blue State blob `cda4da372801a91debf3a9c71b8c8ebbf33b4114`.
- Registry blob `d3a749a48d98292a13931fd6ff8518dea03e5b20`, v1.2 root `6f46db56ce4b54bd4655f9e0f5e919dcdb004520d6a0acd455281841a1d7912f`; FORX mandate hash remains `a9570686dae130bd36d0995d9f58dbd0f7cde1597968dc16245c94a65f0f3109`.
- Register blob `2fa89004db22bb50580d899e5d37516178c6d6b3`, 39 JSONL events. The latest real CHECKPOINT is `AMX-FLT-20261012-DSYNC-145440-9fb44f0c:CHECKPOINT:SEGMENT-10:CASH-IN-READBACK-6147833141`; later records are a Segment-10 LANDING and Segment-11 RESUME. The register has no entry for `FORX-20261013-1646Z-01`.
- Current Index blob at inspection `e38256b823041e2e88664cfff83ddb5aa6761d6a` still points to missing Segment-05 checkpoint event/blob `ca100baca17c99b0964e0ad172b0a7f2698822eb`. It also labels FORX report segments 02–04 as an “Existing flight,” despite no registered LAUNCH.
- The Index's latest appended ROOT/Librarian state says the current flight remains at Segment 11 and that ROOT must reconcile older Segment-12 references before any new segment is registered.

## Canonical correction — no fabricated event

**This proposal deliberately does not append or backdate any register event.** The new Segment-12 checkpoint from an earlier draft proposal was withdrawn from this revision because the latest main-branch Index requires ROOT to reconcile pre-existing Segment-12 references first.

Proposed Index correction:
1. Point “Latest continuity checkpoint” at the real last CHECKPOINT event from Segment 10 and the exact current register blob `2fa89004db22bb50580d899e5d37516178c6d6b3`.
2. Distinguish that historical checkpoint from the current register head, which is the real Segment-11 RESUME event; keep any next-segment registration on hold pending ROOT's existing reconciliation.
3. Reclassify the segment 02–04 FORX reports as historical provenance with an unregistered-flight-ID anomaly. Keep the reports, do not fabricate their missing LAUNCH, and ask ROOT/T-GOV to decide the identity/status based on independent authorization evidence.

## Durable guard added in this review branch

- A read-only standard-library validator checks JSONL shape, required IDs/status/type, duplicate event IDs, exactly one registered LAUNCH per flight represented, mismatched authorization where both fields exist, and linked prior-event ordering.
- It requires the Index to point to the most recent actual CHECKPOINT event (not necessarily the last event in the file) and to the exact Git blob hash of the complete current register.
- It rejects an Index line that calls a flight “Existing flight” without a registered LAUNCH.
- Six regression tests include a valid checkpoint followed by landing/resume, stale blob, unregistered flight, duplicate IDs, no launch and an outdated checkpoint pointer.
- A read-only GitHub Actions job runs the tests and current register/Index validation on relevant PRs and pushes to main. It creates no runtime, schedule, worker, queue, scoring or staging plane.

## Root decision requested

Please independently read this current-base diff, inspect the CI log, verify current mandate and registry root remain unchanged, and decide MERGE / MODIFY / REJECT under the existing governance route. The FORX report-series identity remains an unresolved continuity anomaly until supported historical launch/authorization evidence or an explicit governed rejection/disposition is recorded.

## Directive 23 — itemized addendum

- **Expected outcome:** correct stale Index pointer without mutating append-only history; distinguish the real Segment-10 checkpoint from Segment-11 resume; suppress false active-flight label; continuously detect recurrence.
- **Owner:** ROOT/T-GOV for identity/segment disposition; MASTER/LIBRARIAN for continuity validation/readback; T-COD for technical review; FORX for evidence/provenance.
- **Required action:** inspect PR and CI, merge only if aligned with Canon or reject/request changes.
- **Dependency/blocker:** existing Root direction prohibits registering another segment until old Segment-12 references are reconciled; missing launch evidence for `FORX-20261013-1646Z-01` cannot be invented.
- **Acceptance evidence:** CI success; branch readback of exact register blob/current latest checkpoint; main mandate/registry hash readback; Root's independent disposition.
- **Persistence/readback:** not complete until Root decision and any approved merge are independently read back.
- **Safety/preservation:** no main mutation outside PR, no register rewrite or fabricated event, no duplicate runtime/worker/scheduler/store, no weight/manifest changes, no mandate or registry change.
- **Item disposition:** **PROPOSED / ROOT REVIEW REQUIRED**.
- **Remaining work:** Root disposition of stale Segment-12 references and unregistered FORX identity; merge/reject; post-merge readback.
