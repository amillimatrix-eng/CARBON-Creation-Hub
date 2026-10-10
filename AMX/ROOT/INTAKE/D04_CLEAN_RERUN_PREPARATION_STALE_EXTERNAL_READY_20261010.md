# D04 CLEAN-RUN PREPARATION — STALE EXTERNAL-READY PROJECTION DEFECT

Date: 2026-10-10  
Class: EXECUTION-STATE CONTAMINATION / INTAKE HYGIENE  
Status: PATCHED ON ISOLATED BRANCH; CI READBACK REQUIRED  
Scope: Current OVERDRIVE claim projection only. Historical evidence is preserved.

## Directly observed defect

Read current `overdrive/claims.json` (blob `92a05a72db676a11626220f6f76cf640de12aa93`) and `overdrive/opportunities.json` (blob `b04be618dccf1fed8405ccd7ff5c4be34d18004d`).

The CrowdGen claim `PRI|crowdgen.com|project-coffee-data-labeling-specialist|south-africa` was recorded as:
- `status=WAITING`;
- `routing_reason=HOLD_AUTHENTICATED_ROUTE`;
- `ready_count=0` globally;
- `executable_order=[]`;
- but stale `external_action_ready=true` and `external_ready_count=1`.

The canonical opportunity independently records `execution_readiness=HOLD_AUTHENTICATED_ROUTE` and an Opera `BROWSER_NOT_CONNECTED` evidence item. The next action itself says to hold automated execution until the authenticated route is restored. No send, submission, or new application was performed.

## Root cause in the runner

In `overdrive/runner.py` (blob `e72a6d47b6ced25e69665b44cbc53df66e470972`), `claim_work()` merged the prior claim before refreshing its status. It recomputed `ready_count` and `executable_order`, but did not clear a stale external action flag when the current status became WAITING and did not recompute `external_ready_count`.

That allowed downstream consumers to read contradictory execution state. This is a concrete contamination defect, not evidence that a test control failed.

## Bounded correction

On branch `d04-clean-state-guards-20261010`:
1. Any claim whose current status is not READY now has `external_action_ready=false`.
2. `external_ready_count` is recomputed from claims for which both `status=READY` and `external_action_ready=true`.
3. A regression test seeds an old READY/external-ready claim, then proves a current route HOLD forces WAITING, clears the flag, zeroes both counters and empties the executable order.

The authentic CrowdGen work item remains durably WAITING with its evidence and route hold. It is not deleted or falsely closed. A verified new route would need to be observed before fresh execution authorization.

## Clean D04 isolation boundary

- Frozen benchmark definitions, weights, and pass rule are read only.
- Historical D04 result vectors, prior scores, prose-only corrections, model summaries and old queue snapshots are provenance only. They are not scoring inputs to a clean run.
- Fresh status for every control must be established against current evidence; unavailable service/tool surfaces are logged as execution-availability limitations, not silently scored as failures.
- Original artifacts are immutable history. Active projections and handoff pointers must identify only the latest verified state.

## Current disposition

The prior 96.62% figure is reproducible arithmetic over the earlier vector after excluding five controls as UNMEASURED_NOT_PROVEN; it is not a fresh rerun. The separate fresh D04 rerun must occur only after the stale projection fix is accepted and current runtime evidence can be read back. No claim of full clean-run completion is made by this preparation record.
