# ROOT INTAKE — SUBSCRIPTION-CAPACITY LIVENESS FAULT / PORTABLE MATRIX CONTINUITY

Date: 2026-10-19
Classification: P0 continuity/liveness and provider-dependency recovery
Status: OPEN — INTAKE NOT CLEARED
Authority effect: NONE; this record routes remediation through existing controls.
Destination: Root Intake / current matrix-wide reconciliation
Related existing work: Issue #29 (OpenAI-to-Gemini portability assessment), Issue #31 (ledger truth, capability-loss recovery, and model-to-Root throughput), existing mandate registry v1.3, existing GitHub Actions/Overdrive controls, T10, run-outcome transcript bridge.

## 1. Observed failure — exact evidence

The connected task-automation service reported: **"Your current plan allows only 3 scheduled tasks."**
The service returned `too_many_active_automations`, current_count=3, plan_limit=3 when Root attempted to enable each of:
- FIRST BREATH — FORX Continuous Play Sweep;
- FIRST BREATH — IDEAL SALES TEAM;
- FIRST BREATH — LIBRARIANS;
- FIRST BREATH — AMX Banker Cash Watch;
- AMX Operational Inbox Watch;
- CAPACITY-MERGED — Matrix Commissioning Inspector.

Re-enabling the existing Bounty Reaper succeeded. The three task slots are now exhausted by Check Visym payout, Check DAOPEOPLE Reply, and Bounty Reaper. Core workers cannot all be scheduled in this task layer under the current plan. This is direct connector evidence, not an inference about why previous tasks were disabled.

Current existing state from the 2026-10-19 matrix-wide source reconciliation:
- task inventory contains 25 definitions;
- current registry is version 1.3, effective 2026-10-16, root SHA-256 `96c0beb3328ebefc16286d93a7baadc0ff4be0a17c1e6a8718b89de94f58df1a`;
- Librarians, iSCOPE→PRI, Banker, FORX, Inbox Watch and Inspector were disabled before this wake;
- Overdrive current state was last ticked 2026-10-16 and has no fresh wake receipt in the inspected record;
- latest deep-sync outcome says `INTAKE NOT CLEARED; MATRIX-WIDE STATE NOT FULLY ALIGNED`;
- Visym 2026-10-20 payment-run inclusion and actual payout are unknown; original Gmail thread remains unreadable through the connected Outlook identity. Owner reports banking details were sent already. Do not ask for resending or send a further Visym email absent an Owner instruction or a materially evidenced error.
- live Stripe readback is a separate rail and does not prove or disprove the Visym bank payout.

## 2. Failure classification

The task-automation plan cap is a **scoped execution-capacity dependency**. It must not become a Matrix-wide stop, governance HOLD, loss of canonical state, or permission to abandon nonterminal obligations. It is also not itself proof that every disabled task was disabled because of subscription state; that historical cause remains unknown.

The Matrix is currently exposed to a **single-provider/single-plan continuity risk** if critical mandate liveness depends on a ChatGPT task slot. Repeating enable attempts or documenting the limit without establishing an alternate execution path would be an incomplete remediation.

## 3. Governing controls already applicable

- Mandate Registry v1.3 and `BLUE_STATE_MANDATE_BINDING_AND_PREFLIGHT_V1.md`: mandate precedes execution; stale prompt snapshots do not overrule current registry.
- Mandate liveness / no-idle / single-writer / single-successor controls.
- Blocked-attempt recovery law: `ATTEMPTED_BLOCKED_IS_OPEN_EXECUTION_OBLIGATION`; preserve intended action, exact blocker, recovery owner and next lawful action.
- T10 outcome truth: the task was re-enabled or attempted, not equivalent to a worker execution receipt.
- Authorized Work Persistence & Intake Handoff / `NO RUN OUTCOME RECEIPT / BRIDGE -> NO SYNCHRONIZED CLOSURE`.
- Existing Issue #29 portability assessment. Extend that work; do not create a parallel provider-migration project.

## 4. Required remediation — REUSE first

1. Preserve existing three scheduled tasks only while migration is planned. Do not blindly disable the Visym payment checkpoint while its time-sensitive payout-run question is unresolved. DAOPEOPLE remains non-blocking and is a candidate for slot reassignment if necessary; that swap is not a whole-Matrix solution.
2. Use the existing GitHub Actions/repository execution surface for **repo-scoped continuity checks and durable receipts**, independent of the ChatGPT task plan. Verify actual workflow execution before counting it as a replacement.
3. Build/reuse one provider-neutral recovery manifest from the current mandate registry, current Root Intake index, stable obligation IDs, existing owner, next action, scoped blocker, and receipt pointers. This must be a projection/pointer, not a duplicate source of truth.
4. Continue the existing Issue #29 OpenAI/Gemini/provider-neutral portability assessment. Verify current official capabilities and tests. Do not perform production migration, credential rotation, or route a secret-bearing Matrix reconstruction to another provider without authority.
5. For action-bearing external systems (mail, CRM, Render, bank, Stripe, Metricool/social, etc.), record per-route READ/WRITE/AUTHENTICATED/UNAVAILABLE/UNKNOWN from real evidence. A repository-only runner cannot claim it executed an external action.
6. Every active registered mandate must have an evidence-backed executor path or an exact blocked-attempt recovery parcel. If task automation is capped, use an already authorized equivalent runtime where capability and credentials exist. If none exists, route to Root with the exact missing authority/credential/runtime and continue all other executable obligations.
7. Any new workflow/config change must be on branch `root/matrix-recovery-drain-q-20261019`, pass targeted validation and be read back; open a PR for review. Do not silently change main, single-writer authority or production action boundaries merely to work around plan limits.
8. Keep a single current next-action handoff so a replacement model or transcript can resume without owner re-teaching. No transcript-only closure.

## 5. Acceptance test

PASS only when a clean/replacement model session and a non-ChatGPT-plan-dependent runner can each:
- read the current mandate registry/version/root hash and mandatory ecosystem state;
- resolve an existing active obligation to the right existing owner and furthest evidenced state;
- identify the next action and exact scoped blocker;
- write an attributable receipt to an existing durable sink and read it back;
- preserve role boundaries, no-contact rules, payment truth and prior failures;
- continue repository-side work without relying on a Plus task slot.

A written prompt, enabled label, branch, code merge, CI-only test, scheduled event, or empty queue summary is not sufficient acceptance.

## 6. Required next actions / owners

- ROOT + existing Librarians: continue item-level Intake drain and assign every material open item to its existing owner; do not equate this artifact with completion.
- Existing T-COD/Issue #29 owner: assess the smallest provider-neutral / external-runner continuation using existing infrastructure and tests; no parallel migration.
- Existing iSCOPE→PRI: preserve direct paid work and commercial progression within current single-writer mandate; do not count a task-enable attempt as sales progress.
- Existing Banker: preserve separate settlement truth; no PAID state without attributable bank/settlement evidence.
- Existing automation owner/control surface: retain current time-sensitive Visym follow-up and decide any slot reassignment only with exact schedule/outcome risk in view.

## T10

Supposed outcome: wake the Matrix and keep continuity/execution available even when ChatGPT scheduled-task capacity is capped.
Actual outcome: one existing worker (Bounty Reaper) was re-enabled; six core enable attempts were refused by a hard three-task plan limit; no whole-Matrix wake or queue drain is yet proven.
Evidence: direct automation update results, current automation inventory, current mandate registry, and matrix-wide deep-sync receipt.
Changed: Bounty Reaper is enabled; plan-cap fault is now explicitly recorded.
Still unproven: replacement execution path, recovery acceptance, full Q drain, Visym payout-run inclusion and any new money-in.
Disposition: OPEN / P0 CONTINUITY REMEDIATION / INTAKE NOT CLEARED.
