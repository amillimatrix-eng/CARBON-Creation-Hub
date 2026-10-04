# AMX GOVERNANCE INTAKE CANDIDATE
## RUN OUTCOME RECONCILIATION + TRANSCRIPT BRIDGE PROTOCOL

Status: CANDIDATE — GOVERNANCE INTAKE
Requested disposition: REVIEW FOR MERGE + BLUE STATE
Date: 2026-10-04
Origin: Owner directive
Authority note: This file submits the proposal for governance disposition. It does not self-promote to Canon or merged Blue State.

## 1. Problem

AMX can execute code runs, repair runs, pre-runs, post-runs, commissioning runs, recovery runs, tests, migrations, bootstrap work and other consequential technical work while the resulting truth remains trapped in one transcript, one model session, one terminal, or one worker receipt.

That creates a desynchronization hazard:
- one instance sees the failure;
- another sees only the repair;
- another sees only a status summary;
- governance sees neither the exact pre-state nor the exact outcome;
- later models rediscover the same fault and “repair” already-repaired systems;
- failed approaches and useful evidence are lost;
- prompt/config state can diverge from actual runtime state.

The correction is mandatory outcome reconciliation, not more status reporting.

## 2. Proposed Blue-State invariant

For every consequential coded run, repair run, pre-run, post-run, commissioning run, migration, recovery, bootstrap, test, or comparable technical execution:

RUN ATTEMPT -> OUTCOME RECEIPT -> INTAKE DELIVERY/BRIDGE -> GOVERNANCE VISIBILITY -> RECONCILIATION

A run is not fully CLOSED merely because the command completed or a worker reported success.

A consequential run is synchronized only when governance can recover:
1. what was intended;
2. what state existed before execution;
3. what actually ran;
4. what actually happened;
5. what evidence proves it;
6. what worked;
7. what failed;
8. what changed;
9. what remains unresolved;
10. what must be amended, preserved, reverted, retried, or superseded;
11. who/what owns the next action;
12. whether the run is terminal or still nonterminal.

Missing outcome transport = DESYNC_RISK / NOT CLOSED.

## 3. Required run outcome envelope

Every qualifying run should produce one durable outcome envelope with at least:
- RUN_ID
- timestamp / time window
- originating office / worker / model / execution surface
- objective
- authority / scope
- pre-run state
- inputs / dependencies
- commands / actions actually executed
- actual outcome
- evidence / receipt / commit / hash / log / external response references
- what worked
- what did not work
- faults / blockers / side effects
- state delta
- claims explicitly NOT proven
- amendments / corrections required
- unresolved dependencies
- next owner
- next action
- terminal state
- T10 outcome truth:
  - supposed outcome
  - actual outcome
  - proof
  - changed
  - still unproven

No invented evidence. UNKNOWN/HOLD over inference.

## 4. Delivery rule

### 4.1 Normal path
If the executor/model has an authorized durable intake-write route, it MUST send the outcome envelope to the AMX intake/control estate in the same execution window where practical.

### 4.2 No intake-write capability
If the executor/model cannot write directly to intake, that inability MUST NOT silently strand the outcome in the transcript.

It must emit a structured handoff marked:

AMX_INTAKE_BRIDGE_REQUIRED

The structured handoff must contain the full run outcome envelope, or an exact durable pointer to it.

Any Librarian / Root / Master / authorized reconciliation surface that subsequently gains access to that transcript or output and also has intake-write capability MUST ingest that handoff into intake before treating the relevant system state as synchronized.

### 4.3 Transcript-only fail-safe
Where the transcript is the only available output surface:
- the model must expose the structured outcome envelope in the transcript;
- it must label it as pending intake reconciliation;
- the state remains DESYNC_RISK / NOT CLOSED until a durable intake receipt exists;
- the next authorized Librarian with access must perform the bridge write and read back the resulting intake record.

A transcript statement such as “fixed”, “working”, “done”, or “passed” without the envelope and evidence is not a substitute.

## 5. Bridge / reconciliation behavior

The bridge must be deterministic and deduplicating.

Recommended identity:
RUN_ID + origin + target + execution time window.

On ingest:
- preserve the original outcome;
- do not rewrite failure into success;
- do not collapse ATTEMPTED, EXECUTED, VERIFIED, CLOSED, DEPLOYED, SUBMITTED, ACCEPTED or PAID;
- link follow-on repair outcomes to the earlier failed run rather than overwriting history;
- preserve superseded evidence as provenance;
- merge duplicate envelopes by identity/evidence, not by wording similarity;
- surface contradictions to governance instead of silently choosing one.

## 6. Governance use

The intake record is not merely archival. Governance/Librarians use accumulated run outcomes to identify:
- recurring repair loops;
- bad commands / brittle runbooks;
- repeated false assumptions;
- unnecessary human intervention;
- stale dependencies;
- runtime/configuration divergence;
- worker regression;
- missing observability;
- weak pre-run checks;
- failed post-run verification;
- candidate Blue State improvements;
- candidate merge amendments;
- reusable successful recovery patterns.

The point is selection pressure: successful execution patterns become easier to reuse; failed patterns become harder to repeat.

## 7. Relation to existing AMX rules

This candidate is intended to MERGE cleanly with, not replace:
- T10 Outcome Truth;
- BLUE STATE execution fidelity / partial progress != DONE;
- mandate liveness / work persistence;
- rolling consensus;
- recovery vs supersession;
- UNKNOWN/HOLD preference;
- evidence-first operation;
- NO RECEIPT -> NO CLOSURE.

Proposed additional invariant:
NO RUN OUTCOME RECEIPT / BRIDGE -> NO SYNCHRONIZED CLOSURE.

## 8. Minimum implementation if accepted

Governance should select the smallest existing machinery rather than create duplicate architecture.

Preferred implementation order:
REUSE -> CONFIGURE -> EXTEND -> BUILD NEW.

Minimum required capability:
1. canonical run-outcome envelope schema;
2. one durable intake destination;
3. one transcript/output bridge rule for models lacking direct intake-write capability;
4. dedupe/linking by RUN_ID/evidence;
5. readback proving intake persistence;
6. downstream governance disposition: ACCEPT / MERGE / AMEND / REJECT / HOLD;
7. resurfacing of unresolved amendments when materially relevant.

Do not create a separate dashboard merely for this protocol unless existing operating surfaces cannot expose the records.

## 9. Current evidence / motivating case

BLACK/Codex recovery on 2026-10-04 demonstrated the need:
- historical Git control sync failed due a stale .git/index.lock;
- BLACK service was stopped, stale lock removed, and service restarted;
- subsequent BLACK jobs produced and pushed fresh receipts;
- Codex was then launched from the BLACK repository;
- the user-facing Codex session remained visibly busy/hanging while ChatGPT showed “Codex is working”;
- this sequence contains valuable truth about the fault, recovery, successful post-repair worker execution and still-unproven Codex terminal outcome.

Without a mandatory run-outcome bridge, later models can easily see only part of that sequence and restart the same repair loop.

Current terminal claim for this motivating case:
BLACK worker recovery = evidenced operational recovery after stale-lock repair.
Codex commissioned terminal outcome = NOT YET PROVEN at time of this intake submission.

## 10. Governance question

Should AMX adopt this as a merged Blue State protocol requiring every consequential technical run to produce a durable, governance-visible outcome envelope, with a mandatory transcript bridge whenever the originating model cannot write directly to intake?

Requested governance actions:
- review;
- reconcile overlap with existing Blue State/T10/rolling-consensus controls;
- amend where required;
- MERGE if accepted;
- define exact authoritative intake destination/schema;
- define bridge owner/trigger;
- preserve this candidate as provenance regardless of disposition.
