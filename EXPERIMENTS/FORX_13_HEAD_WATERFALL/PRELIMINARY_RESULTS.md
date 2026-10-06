# FORX 13-HEAD A/B — PRELIMINARY SHADOW RESULTS

**Branch:** `forx-waterfall-13head-experiment-20261006`  
**Production effect:** NONE  
**Live protocol on main:** 13-head re-entrant Instigator remains current.  
**Experimental protocol:** strict Head 1 → Head 13 waterfall, no mid-pass rewind.

## Evidence limit

This is a first shadow comparison, not a production disposition. Four cases are reconstructed from already-resolved work. Case 5 is a live interruption observed during this experiment.

Scores are 0–5. Execution drag is inverse-scored: 5 = least unnecessary reasoning/work.

---

## CASE 1 — DOM8N / FORX security collision

### Re-entrant result
Resolved quickly at authority/ownership without forcing all heads. Preserved:
- DOM8N / GOLD = canonical / constitutional security authority;
- FORX / WHITE = operational forensic security assurance;
- no rename;
- no reporting-line transfer.

### Strict-waterfall shadow
Would preserve the same conclusion, but Heads 4–13 add little once authority and ownership are settled.

| Metric | Re-entrant | Waterfall |
|---|---:|---:|
| Correctness | 5 | 5 |
| Contradiction detection | 5 | 5 |
| Continuity | 5 | 5 |
| Actionability | 5 | 5 |
| Execution drag | 5 | 2 |
| Pivot responsiveness | 5 | 3 |
| False-conflict resistance | 5 | 5 |
| Handoff clarity | 4 | 5 |
| Outcome consequence orientation | 5 | 4 |

**Case lead:** RE-ENTRANT.

---

## CASE 2 — Attio / Lusha / ZoomInfo identity gates

### Re-entrant result
Dependency/routing analysis found:
- Attio company-email gate;
- Lusha work-email gate;
- ZoomInfo Workspace gate;
- Clay + Tavily + Close provide current outcome-equivalent route-around.

Commercial recovery was correctly classified as **not globally blocked**.

### Strict-waterfall shadow
Likely same result with stronger explicit handoff record but materially more head activations.

| Metric | Re-entrant | Waterfall |
|---|---:|---:|
| Correctness | 5 | 5 |
| Contradiction detection | 4 | 4 |
| Continuity | 5 | 5 |
| Actionability | 5 | 5 |
| Execution drag | 5 | 2 |
| Pivot responsiveness | 5 | 3 |
| False-conflict resistance | 5 | 5 |
| Handoff clarity | 4 | 5 |
| Outcome consequence orientation | 5 | 4 |

**Case lead:** RE-ENTRANT.

---

## CASE 3 — side-task interruption / P0 retention

### Re-entrant result
P0 remained intact, but FORX allowed useful side tasks to consume too much immediate execution bandwidth before returning to the money-producing objective.

### Strict-waterfall shadow
Would improve explicit priority pinning if Head 12 weighted continuation and Head 13 literal check must always be reached before a side task can displace active work. Cost: unnecessary full-pass overhead for trivial interruptions.

| Metric | Re-entrant | Waterfall |
|---|---:|---:|
| Correctness | 4 | 5 |
| Contradiction detection | 4 | 5 |
| Continuity | 5 | 5 |
| Actionability | 4 | 4 |
| Execution drag | 4 | 2 |
| Pivot responsiveness | 5 | 3 |
| False-conflict resistance | 5 | 5 |
| Handoff clarity | 4 | 5 |
| Outcome consequence orientation | 3 | 4 |

**Case lead:** MIXED. Waterfall improves priority discipline; re-entrant is much cheaper.

---

## CASE 4 — Reaper capability expansion without bounty consequence

### Re-entrant result
The protocol correctly retained:
- independent Reaper role;
- expanded capability;
- provenance/supersession;
- no false payout/completion claim.

Head-13/continuation pressure exposed the key contradiction:
**better reasoning estate, unchanged bounty consequence.**

### Strict-waterfall shadow
Would make the full causal chain easier to audit, but could delay direct action when an early failure node is already clear.

| Metric | Re-entrant | Waterfall |
|---|---:|---:|
| Correctness | 5 | 5 |
| Contradiction detection | 5 | 5 |
| Continuity | 5 | 5 |
| Actionability | 4 | 4 |
| Execution drag | 4 | 2 |
| Pivot responsiveness | 5 | 3 |
| False-conflict resistance | 5 | 5 |
| Handoff clarity | 4 | 5 |
| Outcome consequence orientation | 4 | 4 |

**Case lead:** RE-ENTRANT, but waterfall has auditability advantage.

---

## CASE 5 — LIVE XOXNO BLACK handoff failure

### Initial observed state
Reaper reported:
- job A exists;
- expected receipt absent;
- XOXNO remains Q3/HYPOTHESIS;
- blocker described as queued BLACK job with no durable execution receipt;
- owner notification classified as irreducible.

### FORX live re-entrant investigation
FORX inspected the actual live BLACK worker and discovered:

**Job A does not contain a `command` array.**

Current `BLACK/worker.py` rejects any job without a non-empty command list:

`JOB_INVALID <job-id>`

The worker logs that exception but does not create an invalid-job receipt.

Therefore the missing receipt did **not** prove BLACK had executed and failed, nor did it yet prove BLACK was dead. It proved a **Reaper → BLACK contract/schema mismatch**.

FORX preserved A and queued executable job B under the current worker schema:

`BLACK/jobs/REAPER-XOXNO-20261006-2057-B.json`

Main commit:

`4250edd485fa87ed82772cccd200bf481c0f4ea1`

At the first immediate readback after queueing B, no B receipt was yet present. Because BLACK polls asynchronously, that immediate absence is not sufficient by itself to classify liveness failure.

### Strict-waterfall shadow

A strict waterfall has a real advantage in this case.

- Head 1: challenge "queued means executable."
- Head 2: compare job specification to worker contract.
- Head 3: confirm current worker code is authoritative for executable schema.
- Head 4: reject owner escalation before cheap schema validation.
- Head 5: restate exact accepted facts.
- Head 6: identify zero-value owner interruption if local repair exists.
- Head 7: locate failure at handoff schema.
- Head 8: assign repair to existing Reaper/BLACK route.
- Heads 9–13: verify the conclusion and preserve continuity before escalation.

This would likely have prevented the premature **irreducible blocker** classification before Owner notification.

The re-entrant protocol did recover quickly once the blocker was challenged, but only after the watcher had surfaced the wrong blocker class.

| Metric | Re-entrant | Waterfall |
|---|---:|---:|
| Correctness | 4 | 5 |
| Contradiction detection | 5 | 5 |
| Continuity | 5 | 5 |
| Actionability | 5 | 5 |
| Execution drag | 5 | 3 |
| Pivot responsiveness | 5 | 3 |
| False-conflict resistance | 4 | 5 |
| Handoff clarity | 4 | 5 |
| Outcome consequence orientation | 5 | 5 |

**Case lead:** WATERFALL for false-blocker prevention; RE-ENTRANT for repair speed after discovery.

---

# PRELIMINARY RESULT

Neither mechanism dominates.

Current evidence suggests:

## Re-entrant is stronger when:
- the failure is localized early;
- a material pivot appears mid-chain;
- speed / execution density matter;
- upstream assumptions remain valid.

## Strict waterfall is stronger when:
- a blocker is about to be escalated;
- the system is about to call something irreducible;
- lifecycle/authority/ownership truth is contested;
- a false blocker would interrupt the Owner;
- a terminal PASS/FAIL/HOLD claim is about to be made.

## Leading candidate

**HYBRIDIZE, subject to more evidence:**

Normal work:
**re-entrant FORX**

Before any of these high-consequence outputs:
- OWNER GATE / IRREDUCIBLE BLOCKER;
- FAIL;
- terminal PASS;
- governance/authority conflict;
- role transfer;
- worker retirement;
- money/closure classification;

run a **mandatory strict 13-head waterfall closeout pass**.

This preserves the current protocol's speed while using the Owner's original waterfall design as a high-consequence falsification gate.

No production change is authorized by this shadow result.
