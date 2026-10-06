# TEMP EXPERIMENT — FORX 13-HEAD STRICT WATERFALL

**Branch:** `forx-waterfall-13head-experiment-20261006`  
**Purpose:** A/B test the Owner's original strict waterfall interpretation against the current live re-entrant FORX protocol.  
**Authority:** EXPERIMENT ONLY — NO LIVE FORX / CANON / BUILD AUTHORITY.  
**Production protocol remains unchanged on main.**

## Strict sequence

Every case passes through all heads in order:

1. INSTIGATOR
2. SPECIFICATION
3. PROVENANCE / AUTHORITY
4. EFFICIENCY
5. CONTINUITY CHALLENGER A
6. ROI / VALUE
7. FAILURE NODE / DEPENDENCY GRAPH
8. ROUTING / EXECUTION OWNERSHIP
9. CONTINUITY CHALLENGER B — 12-year-old clarity lens
10. VERIFICATION
11. OPTIMIZATION
12. WEIGHTED CONTINUATION
13. CONTINUITY CHALLENGER C — 3-year-old literal-continuity lens

## Waterfall rule

- No head may be skipped.
- No head may re-enter earlier in the same pass.
- Each head receives the cumulative output of Heads 1..N-1.
- A material pivot discovered mid-chain is recorded as `PIVOT_PENDING`; the current pass continues to Head 13.
- Head 13 determines whether:
  - ACTIONABLE — sufficient verified state exists for the next lawful action;
  - SECOND_PASS_REQUIRED — a material pivot invalidated an upstream premise;
  - WAIT / BLOCK / HOLD — exact unresolved state;
  - ESCALATE — only where existing controls require it.
- A second pass, if required, restarts at Head 1 with the newly pinned state. No partial rewind.

## Instigator rule

The Instigator appears only at Head 1 of each full pass.

Its allegations remain probes, never facts.

## Comparison control

The live protocol on `main` remains the current re-entrant design:
- Instigator at entry;
- bounded Instigator re-entry at material pivots;
- return to continuation point rather than restarting the full pass.

This experiment does not alter the live protocol.

## Expected tradeoff hypothesis

The waterfall may:
- preserve clearer causal sequencing;
- reduce recursive interruption;
- make handoff/reconstruction simpler;
- expose whether downstream heads can resolve pivots without rewind.

The waterfall may also:
- waste work after an upstream premise has materially changed;
- delay response to contradictions;
- increase total head activations when a full second pass is required.

No preference is assumed before evidence.
