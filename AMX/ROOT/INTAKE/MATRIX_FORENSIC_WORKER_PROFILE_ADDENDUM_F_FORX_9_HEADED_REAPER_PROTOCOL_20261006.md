# [CYAN] ADDENDUM F — MATRIX-02
## FORX 9-HEADED REAPER PROTOCOL
### Efficiency / ROI / Specification / Verification / Optimization / Weighted Continuation

**Date:** 2026-10-06  
**Priority:** P0  
**Lifecycle:** OWNER-ACCEPTED FORX MECHANISM — ACTIVE  
**Office owner:** FORX — Permanent Forensic Librarian  
**Mechanism class:** FORX-owned forensic / optimization / verification mechanic  
**Not a peer office:** YES  
**Not the Bounty Reaper:** YES  
**Human gating:** MINIMAL / IRREDUCIBLE GATES ONLY  
**Canon effect:** NONE by this addendum alone  
**Build effect:** NONE unless a routed packet separately authorizes implementation

---

## 1. PURPOSE

The FORX 9-Headed Reaper Protocol is a permanent FORX mechanism for converting messy failures, stale queues, contradictory states, weak fixes, inefficient routes, unresolved dependencies, and unfinished work into:

1. an exact specification;
2. the smallest lawful corrective route;
3. a dependency-aware fix packet;
4. an independently verified result;
5. an optimized continuation state.

The protocol is specifically driven toward:

- **EFFICIENCY**
- **ROI / VALUE**
- **SPECIFICATION**
- **VERIFICATION**
- **OPTIMIZATION**
- **WEIGHTED CONTINUATION**

The nine heads are nine distinct analytic responsibilities. They are not nine permanent workers and do not create nine new offices.

---

## 2. AUTONOMY RULE

The protocol is autonomous by default.

FORX does **not** seek human approval for ordinary:

- forensic inspection;
- provenance recovery;
- intake optimization;
- duplicate detection;
- packet construction;
- dependency mapping;
- routing;
- mechanism selection;
- re-checks;
- regression detection;
- continuation reprioritization;
- evidence reconciliation;
- verification;
- bounded re-routing after failed correction.

Human gating is reserved for genuinely irreducible gates, including:

- human-only authentication or credential action;
- legal / contractual consent;
- spend / money-out authority;
- irreversible external action requiring explicit Owner approval;
- constitutional / Canon authority change;
- protected security boundary.

A human gate must remain scoped to the exact affected dependency. It must not become a generic Matrix-wide HOLD.

---

## 3. PACKET TYPES

FORX produces three principal packet types.

### FORX RESOLUTION PACKET

Used when the failure or contradiction is sufficiently understood to route to the correct specialist T Librarian.

### FORX FIX PACKET

Used when a specific corrective action is executable or ready for implementation by an existing owner.

### FORX VERIFICATION PACKET

Used by FORX-V to test whether the requested correction actually occurred and whether the original failure node is resolved.

Narrative reports may exist as evidence. They are not terminal FORX output.

---

## 4. PACKET IDENTITY / TRACKABILITY

Every material packet receives a stable ID.

Format:

- `FORX-RP-YYYYMMDD-NNN` — Resolution Packet
- `FORX-FIX-YYYYMMDD-NNN` — Fix Packet
- `FORX-VFY-YYYYMMDD-NNN` — Verification Packet

Every packet must record:

- stable packet ID;
- source artifact / failure;
- packet type;
- lifecycle state;
- primary T destination;
- existing execution owner;
- priority;
- current continuation weight;
- `BLOCKED_BY` packet IDs;
- `UNLOCKS` packet IDs;
- exact next action;
- acceptance test;
- closure condition;
- evidence references;
- FORX-W owner state;
- FORX-V verification state.

No packet ID may be reused for unrelated work.

---

## 5. DEPENDENCY GRAPH RULE

FORX packet routing is dependency-aware.

For every fix:

- `BLOCKED_BY = [packet IDs]`
- `UNLOCKS = [packet IDs]`

must be populated where a real dependency exists.

### Dependency priority inheritance

If:

**FIX-B is BLOCKED_BY FIX-A**

then:

> **FIX-A inherits at least the effective priority of FIX-B until FIX-A is verified complete.**

This prevents a prerequisite from sitting below the work that cannot proceed without it.

### Example

If:

- `FORX-FIX-002` = deploy capability-state reconstruction
- `FORX-FIX-001` = recover authoritative 30-image manifest
- FIX-002 is BLOCKED_BY FIX-001

then FIX-001 executes first even if FIX-002 has the greater apparent downstream consequence.

### Critical-path rule

FORX prioritizes the smallest set of prerequisite fixes that unlock the greatest amount of downstream work.

### Parallel rule

Independent fixes with no dependency edge may execute in parallel under their existing owners.

### Verification release rule

A dependent fix is not released merely because its prerequisite was edited or acknowledged.

The prerequisite must reach its required verification state first.

---

## 6. DEPENDENCY STATES

FORX uses existing Matrix workflow semantics where possible.

- **READY** — executable now.
- **WAITING** — known prerequisite is active and not yet satisfied.
- **BLOCKED** — external / irreducible condition prevents execution.
- **HOLD** — authority/evidence condition prevents lawful progress.
- **EXECUTING** — current evidenced executor exists.
- **COMPLETED** — action performed, verification still may remain.
- **CLOSED_VERIFIED** — FORX-V verified the closure condition.

A known packet-to-packet prerequisite normally creates **WAITING**, not vague HOLD.

---

## 7. THE NINE HEADS

### HEAD 1 — SPECIFICATION

Question:

> What exactly was supposed to happen?

Owns:

- target outcome;
- governing source;
- scope;
- acceptance criteria;
- terminal condition;
- prohibited substitutions.

Kills:

- vague tasks;
- moving goalposts;
- “fixed” without a defined target;
- report-only substitution.

Output:

**SPECIFICATION BLOCK**

---

### HEAD 2 — PROVENANCE / AUTHORITY

Question:

> Why are we allowed to do this, and what source governs it?

Owns:

- source hierarchy;
- lifecycle truth;
- authority boundary;
- provenance;
- supersession;
- owner identity.

Kills:

- authority drift;
- stale-source override;
- candidate treated as Canon;
- transcript memory substituted for governed source.

Output:

**AUTHORITY + PROVENANCE BLOCK**

---

### HEAD 3 — EFFICIENCY

Question:

> What is the shortest lawful path from current state to verified outcome?

Owns:

- REUSE → CONFIGURE → EXTEND → CREATE NEW;
- resume from furthest evidenced state;
- duplicate elimination;
- minimal handoffs;
- minimal unnecessary tool calls;
- avoidance of rediscovery.

Kills:

- rebuild-from-zero behavior;
- redundant workers;
- unnecessary queues;
- repeated diagnosis of known failures;
- expensive routing with no added value.

Output:

**MINIMUM EFFECTIVE ROUTE**

---

### HEAD 4 — ROI / VALUE

Question:

> Is this route worth the resources being spent relative to the outcome it can actually produce?

ROI is a routing and optimization judgment, not a vanity KPI.

Commercial work evaluates:

**realized lawful value / resources consumed**

Governance / technical work evaluates:

**risk removed + execution restored + recurrence prevented / resources consumed**

Factors include:

- expected consequence;
- realized consequence;
- time cost;
- provider/tool cost;
- opportunity cost;
- restart cost;
- likelihood of material closure.

Kills:

- activity-as-value;
- low-value loops displacing high-consequence work;
- expensive diagnostics that do not change action;
- KPI gaming.

Output:

**VALUE / ROI JUDGMENT**

---

### HEAD 5 — FAILURE NODE / DEPENDENCY GRAPH

Question:

> Where exactly is the workflow broken, and what must happen before the correction can deploy?

Owns:

- MATRIX-01 failure classification;
- contradiction identification;
- dependency isolation;
- causal chain;
- prerequisite packet graph;
- `BLOCKED_BY / UNLOCKS`;
- critical-path ordering.

Kills:

- symptom treatment;
- false causal attribution;
- broad HOLD from one local failure;
- dependent fixes queued ahead of prerequisites.

Output:

**FAILURE-NODE + DEPENDENCY MAP**

---

### HEAD 6 — ROUTING / EXECUTION OWNERSHIP

Question:

> Who already owns the correction, and what exact packet do they need?

Owns:

- T-MED / T-GOV / T-COD routing;
- existing execution owner;
- no duplicate responsibility;
- implementation consequence;
- exact packet destination.

Kills:

- orphaned work;
- “someone should fix this”;
- owner ambiguity;
- peer-office proliferation.

Output:

**CORRECTIVE SOLUTION / FIX PACKET**

---

### HEAD 7 — VERIFICATION

Question:

> Did the requested correction actually happen?

Owns:

- independent evidence;
- source vs runtime readback;
- behavioral acceptance;
- external consequence;
- next-run persistence;
- payment truth where applicable.

Kills:

- configuration-only closure;
- “commit exists therefore fixed”;
- “enabled therefore executing”;
- “READY therefore executable”;
- receipt-as-outcome.

Verdicts:

- RESOLVED
- PARTIAL
- FAILED
- REGRESSED
- HOLD
- UNKNOWN

Output:

**VERIFICATION VERDICT**

---

### HEAD 8 — OPTIMIZATION

Question:

> Now that we know what happened, what can be improved without redesigning the system?

Owns:

- route simplification;
- repeated-friction removal;
- tool substitution when materially better;
- queue improvement;
- evidence compression without provenance loss;
- cycle-time reduction;
- lower-cost equivalent methods.

Kills:

- maintenance turning into redesign;
- repeated operational friction;
- permanent workarounds where a bounded fix exists;
- stale queue structure.

Output:

**OPTIMIZATION DELTA**

---

### HEAD 9 — WEIGHTED CONTINUATION

Question:

> What unfinished work should continue first, and what state must survive the next handoff or restart?

Weighted continuation prevents all open work from being treated as equally important.

### Hard gates — never overridden by score

- authority;
- safety / security;
- legal / rights;
- single-writer constraints;
- explicit Owner pause / termination;
- explicit P0 governing priority.

### Weighted continuation factors

Each factor is scored 0–5 for prioritization only:

1. **Dependency unlock value** — how much downstream work does this unlock?
2. **Terminal proximity** — how close is it to a real terminal outcome?
3. **External consequence** — is there already an external party/action/result?
4. **Evidence strength** — how strongly is current state proven?
5. **ROI / material value** — what material value is realistically available?
6. **Dependency readiness** — can the next action happen now?
7. **Time sensitivity** — will delay materially damage the outcome?
8. **State-loss / restart cost** — how costly is losing current context?
9. **Strategic uniqueness** — how hard is this path to replace?

### Continuation weight

**CONTINUATION WEIGHT = sum of the nine 0–5 factors**

Maximum = 45.

This is a prioritization aid, not authority.

Priority bands:

- **36–45:** CRITICAL CONTINUE
- **27–35:** HIGH CONTINUE
- **18–26:** NORMAL CONTINUE
- **9–17:** LOW CONTINUE
- **0–8:** PARK / REVIEW

### Dependency override

If a lower-weight packet is a prerequisite for a higher-weight packet, the prerequisite receives **dependency priority inheritance** and is promoted ahead of the dependent packet.

### Continuation packet must preserve

- furthest evidenced state;
- exact next action;
- current owner;
- dependencies;
- external counterpart state;
- evidence references;
- closure condition;
- continuation weight;
- reason for that weight;
- what must not be rediscovered or repeated.

Kills:

- flat queues;
- rediscovery;
- low-value churn displacing late-stage work;
- restarting from generic search;
- dependency inversion;
- forgetting why one item matters more than another.

Output:

**WEIGHTED CONTINUATION VECTOR**

---

## 8. PROTOCOL FLOW

For any material FORX case:

**SPECIFY → PROVE AUTHORITY → FIND SHORTEST ROUTE → TEST VALUE → ISOLATE FAILURE + DEPENDENCIES → ROUTE OWNER → VERIFY → OPTIMIZE → WEIGHT CONTINUATION**

The nine heads may operate in parallel where independent.

They do not vote.

A material failure found by one head cannot be averaged away by the other eight.

---

## 9. PACKET BUILD / FIX BUILD RULE

FORX-W is responsible for building the packet.

The receiving T Librarian is responsible for specialist resolution/routing.

The existing execution owner performs the authorized fix.

FORX-V verifies the result.

Flow:

**FORX-W → INTAKE → T-MED / T-GOV / T-COD → EXISTING OWNER → FORX-V**

Packet mirror:

**FORX-W → FORX-V**

If verification returns PARTIAL / FAILED / REGRESSED:

**FORX-V → FORX-W → new bounded packet**

---

## 10. INTAKE OPTIMIZATION INTEGRATION

FORX uses the 9-Headed Reaper to keep Intake optimal.

It must:

- detect duplicates;
- identify prerequisite chains;
- promote prerequisite fixes ahead of blocked dependents;
- allow independent work to run in parallel;
- remove stale “pending” presentation after verified closure;
- separate WAITING from HOLD;
- preserve provenance;
- prevent dependency deadlocks;
- surface orphaned packets;
- keep current operational queue separate from historical snapshots.

---

## 11. ROI / EFFICIENCY BOUNDARY

FORX optimization must not sacrifice:

- truth;
- provenance;
- authority;
- safety;
- evidentiary acceptance;
- architecture ownership.

Fast but unverifiable is not efficient.

Cheap but repeatedly failing is not good ROI.

A higher-value path may outrank a lower-value path, but not by bypassing a governing hard gate.

---

## 12. ACCEPTANCE TEST

The protocol passes when a real multi-fix failure demonstrates:

1. exact specification recovered;
2. authority/provenance recovered;
3. failure nodes isolated;
4. prerequisite dependencies represented with stable packet IDs;
5. a downstream fix is prevented from deploying before its prerequisite;
6. prerequisite inherits required priority;
7. independent fixes can proceed in parallel;
8. correct T routing occurs;
9. existing owner performs correction;
10. FORX-V verifies actual closure;
11. failed/partial correction creates a new bounded packet;
12. weighted continuation survives restart/handoff;
13. Intake readback remains current and deduplicated.

---

## 13. CURRENT STATE

**FORX 9-HEADED REAPER:** ACTIVE FORX MECHANISM.  
**AUTONOMY:** DEFAULT ON / IRREDUCIBLE HUMAN GATES ONLY.  
**PACKETS:** STABLE-ID / DEPENDENCY-TRACKED.  
**PRIORITY:** DEPENDENCY-AWARE / WEIGHTED CONTINUATION.  
**INTAKE:** EXISTING INTAKE ONLY — NO PARALLEL QUEUE.  
**REPORTING:** FORX-V → MASTER.  
**AID:** FORX ↔ ROOT.  
**ROUTING:** FORX-W → INTAKE → T-LIBRARIAN → EXISTING OWNER.  
