# AMX INTAKE EVIDENCE — BLACK RECEIPT OBSERVABILITY CORRECTION

EVIDENCE_ID: BLACK-RECEIPT-OBSERVABILITY-CORRECTION-20261006-001
DATE: 2026-10-06
TARGET: DR-0021 / BLACK autonomous receipt-path evidence
STATE: EVIDENCE CORRECTION
LIFECYCLE: PRESENT → INDEXED CANDIDATE
AUTHORITY: Evidence only. Not Canon. Not closure. Does not itself promote, merge or supersede governance.

## Correction

The earlier interpretation:

missing BLACK receipt = no work performed

is invalid for the defective historical period.

During the known BLACK receipt/observability defect, absence of a BLACK receipt proves only that the receipt path did not provide evidence of execution.

Therefore:

- PRE-FIX missing BLACK receipt = historical observability/receipt defect.
- Where no independent corroborating evidence exists, execution state is UNKNOWN.
- Historical missing receipt must not be relabelled FAILED merely because the receipt is absent.
- Independent evidence may still establish that a job executed, partially executed, completed, failed or produced downstream effects during that period.
- PRI and Reaper must not be penalized for historical BLACK receipt absence unless separate evidence establishes failure in their own execution paths.

## Post-fix rule

From the correction/fix point forward, an expected fresh BLACK receipt is part of the acceptance path.

Accordingly:

- POST-FIX missing expected receipt = evidence of a new BLACK receipt/transport regression or activation failure.
- It does not establish that the underlying job itself failed unless separately evidenced.
- The current verification canary is:
  BLACK-RECEIPT-VERIFY-20261006-1140-001

At the latest readback available to Root, its receipt had not appeared.

Therefore the repaired receipt path is not independently verified.

## Active cause hypotheses — DO NOT PREMATURELY EXCLUDE

The following remain active suspects until direct evidence excludes them:

1. BLACK worker-side Git transport / credential / local repository state.
2. Windows host behavior affecting WSL availability, Startup execution, process continuity, service wake or interop.
3. WSL/systemd/service activation state, including failure to start or restart the expected BLACK worker after Windows/WSL transitions.
4. Local Git lock, dirty worktree, divergence or stale process state preventing BLACK from updating to the merged repair.
5. Copilot or another locally active coding/agent surface modifying, locking, rebasing, checking out, running, restarting or otherwise interfering with the same BLACK clone/process state.
6. Interaction between Windows, WSL, Copilot/local agents and Git that produces an observability failure without proving underlying task failure.

None of these hypotheses is currently established as the cause solely by missing receipt evidence.

Do not narrow DR-0021 to Git transport alone until Windows/WSL and Copilot/local-agent interaction have been tested or otherwise excluded.

## Current disposition

Historical defective period:
EXECUTION = UNKNOWN where unsupported by other evidence.
RECEIPT PATH = DEFECTIVE / OBSERVABILITY DEGRADED.

Current repaired period:
SOURCE REPAIR = MERGED.
PHYSICAL/RECEIPT ACTIVATION = NOT YET INDEPENDENTLY VERIFIED.
CANARY RECEIPT = NOT YET OBSERVED AT LAST CHECK.

## Provenance

Related Root run outcome:
AMX/ROOT/INTAKE/RUN_OUTCOMES/BLACK-AUTONOMOUS-CONTROL-REGRESSION-20261006-001.md

Related source-repair merge:
57fd11cded791a23cfa06ed0fd61229e9235e24c

Related Root evidence commit:
9aba060e5c1ccf71c740b0a06c52aa0c1866691c

Evidence correction intake commit:
d8edbd857db3e5dd551f68c640835a78d5ed388c

## Standing evidence rule

NO RECEIPT -> NO CLOSURE remains valid.

But during a proven historical observability defect:

NO RECEIPT != NO EXECUTION
NO RECEIPT != FAILED

UNKNOWN must be preserved unless other evidence resolves the execution state.
