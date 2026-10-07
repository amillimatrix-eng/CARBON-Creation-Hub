# FORX 13-HEAD A/B — OWNER-ACCEPTED DISPOSITION

**Date:** 2026-10-07  
**Experiment branch:** `forx-waterfall-13head-experiment-20261006`  
**Lifecycle:** OWNER ACCEPTED EXPERIMENT DISPOSITION — NOT MERGED / NOT CANON / NOT BUILD AUTHORITY

## Accepted disposition

**HYBRIDIZE**

### Live production method
Use the **re-entrant 13-head FORX method** for live operations.

Reason:
- responds to material pivots immediately;
- can re-enter relevant heads without forcing a full restart;
- reduces execution drag;
- better suited to active repair, routing and continuity work.

### Shadow/reference method
Use the **strict 13-head waterfall** as a bounded:
- benchmark;
- calibration reference;
- forensic audit path;
- reconstruction/training aid;
- difficult-case comparison method.

Reason:
- preserves clean causal sequencing;
- makes every head's contribution explicit;
- improves handoff/reconstruction clarity;
- can expose omissions in the live method.

## Current evidence basis

The strongest live example is the Reaper/BLACK XOXNO incident.

The live re-entrant method detected a material pivot:
- the missing receipt was initially treated as an execution/transport blocker;
- direct inspection showed the original job did not satisfy the live BLACK worker contract because it lacked the required `command` array;
- FORX immediately reopened the relevant dependency/routing questions and created a corrected executable parcel plus liveness canary;
- the live run then continued through an outcome-equivalent GitHub/static-review route rather than waiting.

Under the strict waterfall design, that same mid-chain pivot would be recorded as `PIVOT_PENDING`, the current pass would continue through Head 13, and a full second pass could be required.

This is evidence that re-entry has lower live execution drag for material pivots.

## Important limitation

The fixed-case benchmark in `BENCHMARK.md` has **not been exhaustively scored case-by-case**.

Therefore this record does **not** claim:
- the waterfall experiment is fully completed;
- re-entrant FORX dominates every case;
- waterfall has no production value;
- the benchmark should be retired.

The Owner has accepted the **hybrid operating disposition** from the evidence already available.

## Standing comparison rule

Where useful, closed material cases may be replayed through both methods.

If waterfall identifies a material issue missed by live FORX:
- preserve the delta;
- treat it as learning input;
- improve the live method through existing governance;
- do not silently change production behavior.

If waterfall repeatedly adds no material finding while materially increasing reasoning cost:
- narrow its use further to high-risk/audit/calibration cases.

## Current state

**LIVE FORX:** RE-ENTRANT 13-HEAD METHOD  
**SHADOW / BENCHMARK:** STRICT WATERFALL 13-HEAD METHOD  
**DISPOSITION:** HYBRIDIZE — OWNER ACCEPTED  
