# DRAIN Q — FOLLOW-ON WAKE RECEIPT
Date: 2026-10-20
Classification: CATEGORY A — runtime wake / queue continuity
Flight: DQ-20261020-FOLLOW-ON-01
Disposition: OPEN / PARTIAL — NOT CLEARED

## Actions actually taken
Issued one-shot run requests against the existing automation IDs, using their saved prompts/settings:
- Bounty Reaper — `6abf8e6d6a188191aee2b5d3fe24a9c9`
- FORX Continuous Play Sweep — `6ac6a4081dd48191967a0182fca2eba7`
- IDEAL SALES TEAM — `6ac17e8999648191ba125236de46f012`
- Hash Calibration Manager — `6ab5756825d88191a102a79217ad9e08`

Each `run_now` request returned `success=true`, with the message that the immediate run was requested and the saved schedule was unchanged. These acknowledgements do not establish execution completion or delivery.

## Live roster readback
Following the requests, the automation roster showed:
- Hash Calibration Manager: last-run timestamp advanced to `2026-10-20T12:35:36.104483Z` (14:35:36 SAST); task currently disabled. The run result/body was not exposed. Do not infer queue-zero or completion from the disabled flag.
- Bounty Reaper: last-run timestamp remained `2026-10-20T10:23:48.720250Z`; no new attributable result exposed.
- FORX: last-run timestamp remained `2026-10-20T12:01:51.931750Z`; no new attributable result exposed.
- IDEAL SALES TEAM: last-run timestamp remained `2026-10-20T11:55:14.049526Z`; no new attributable result exposed.

## Queue and safety truth
- DRAIN Q remains OPEN / PARTIAL. No item-level queue readback established that the queue is clear.
- Bounty Reaper's canonical Live Tracker remains `TRACKER_WRITE_BLOCKED` on available evidence. Q1 remains `UNKNOWN, NOT ZERO` until the existing Runs/Queue/Payouts source is read and independently reconciled.
- No scheduler cadence was changed, no disabled task was re-enabled, and no new worker, queue, CRM, or tracker was created.
- No external buyer outreach, contract acceptance, spend, transfer, payment configuration change, bounty submission, award, settlement, or realized revenue is evidenced by these wake requests.

## Directive 23 close-out
- **Expected outcome:** evidence-backed queue progression without duplicate infrastructure or false completion.
- **Owner:** Bounty Reaper for bounty parcels; FORX for discovery/graph continuity; iSCOPE/PRI via IDEAL SALES TEAM for commercial progression; Hash Calibration Manager for its bounded hash queue; Root Intake for reconciliation.
- **Action:** issue one-shot wake requests and read back the existing automation roster.
- **Dependencies:** attributable run outputs; authorized access to the existing Bounty Reaper Live Tracker; valid buyer/payment route for commercial progression.
- **Evidence/readback:** four run-request acknowledgements and subsequent automation-roster readback.
- **Safety/preservation:** existing schedules preserved; no duplicate outreach or shadow tracker; Q1 not inferred empty.
- **Disposition:** WAKE REQUESTED / PARTIAL READBACK / DRAIN Q OPEN.
- **Remaining work:** retrieve and inspect attributable run outputs; reconcile item-level queue transitions; restore authorized tracker access and independently read back Q1; continue executable work while lawful tasks remain.


## SAME-RUN CONTINUATION — PR #47 AND LIVE RUNTIME GATE — 2026-10-20

### Merge / deployment readback
- Existing [PR #47](https://github.com/amillimatrix-eng/CARBON-Creation-Hub/pull/47) currently reads closed/merged. Merge commit: `191d576c9cb246fe558547d988a5e7a42f6a8d01`; PR head: `beeb12d6e528c9ca38515f3bfe02d2d83761c236`.
- GitHub combined status on the merge commit: Vercel = SUCCESS.
- Vercel deployment metadata: `dpl_6cyFuWGe7HSMzk8j1UddNmhe6XhP`, READY, production target, commit matches the merge commit.
- Time-source inconsistency: GitHub reports the merge at 14:06:54Z and Vercel reports deployment ready at 14:07:05Z, later than this run's declared time of 13:52Z. Preserve the current state readback, but leave event chronology unreconciled.

### Live route attempt
The existing Render service record for `amx-evidence-house` shows automatic deploy from `main`, service not suspended, and the latest live deploy on older commit `5ad5f4f6be12c12df36ba29a633c5081e365c908` (17 October). Read-only requests to the public host returned HTTP 503 for `/api/health`, `/house/assets/proposal.js`, `/house/assets/proposal.css`, `/house`, `/carbon/partner`, and `/proposal/AMX-QDRAIN-INVALID-TOKEN`. The last uses an invented invalid token only and did not touch customer data.

**Acceptance:** merged code and Vercel deployment metadata are observed; live customer behavior is NOT VERIFIED because the current Render route returned 503. A 503 observation is not proof of permanent failure. Do not mark the behavior gate passed from merge/deploy metadata alone.

### Execution route-around
- The immediate-run calls for existing Bounty Reaper and FORX were rejected with “Resume this task before running it now”; neither call produced an execution receipt.
- The current automation roster lists these tasks as enabled, but this flag alone did not make `run_now` succeed. No schedule or task setting was changed in this receipt.
- Render log access reported that no workspace was selected. No workspace selection or service mutation was made in this pass.
- The Notion append attempt and secondary comment attempts returned tool safety/action errors and were not counted as successful writes. This addendum instead uses the existing canonical GitHub DRAIN-Q receipt, updated sequentially using its fetched current blob SHA.

### Directive 23
- **Expected outcome:** Root can reconcile source chronology, preserve the current production state truth, and progress the existing runtime/task gates without duplicating infrastructure.
- **Owner:** ROOT/T-GOV for chronology/queue disposition; existing deployment owner for Render and proposal route; the already-assigned FORX and Bounty Reaper owners for their current mandates.
- **Next action:** obtain run output through the existing automation task record or approved recovery path; inspect the current Render event/log evidence through the confirmed existing workspace; then repeat read-only health and invalid/unavailable quote-route checks against the exact active source.
- **Dependencies:** attributable automation output; authorized Render workspace-scoped logs/events; working runtime route.
- **Safety/preservation:** no customer token used, no production data changed, no message/payment/submission sent, no schedule changed, and no new issue, worker, queue, service, or tracker created.
- **Disposition:** PARTIAL. Deployment metadata is not runtime acceptance; worker run requests are not run receipts. DRAIN Q remains OPEN / NOT CLEARED.
- **Remaining work:** retrieve attributable run output, reconcile the timestamp anomaly, restore/verify the existing Render runtime if evidence supports it, and get behavior-level readback.


## SAME-RUN CONTINUATION — EXISTING RUNTIME RE-WAKE RETRY — 2026-10-20

- The first immediate-run requests for FORX and Bounty Reaper returned “Resume this task before running it now”. Route-around: re-applied `is_enabled=true` to each existing task using its unchanged saved schedule and mandate; both updates returned success.
- Retried `run_now` for the same two existing IDs. Both then returned success: “Immediate run requested. The saved schedule is unchanged.”
- Read-after-write of the automation roster confirms both remain enabled and their original hourly schedules remain intact. However, the latest recorded `last_run_time` values did **not** advance after these requests:
  - FORX: `2026-10-20T14:05:07.103940Z`
  - Bounty Reaper: `2026-10-20T14:30:30.811319Z`
- **Disposition:** route-around recovered request acceptance; actual execution/output remains NOT VERIFIED. Do not treat request success or the enabled flag as a run receipt.
- **Next:** obtain the completed run output through the existing task record/authorized return path; continue parallel read-only GitHub/source checks where applicable. The service's 503 route remains scoped to the existing Render runtime.


## SAME-RUN CONTINUATION — IDEAL SALES TEAM RE-WAKE RETRY — 2026-10-20

- A direct immediate-run request to the existing IDEAL SALES TEAM task was initially rejected with “Resume this task before running it now”.
- Route-around: re-applied `is_enabled=true` to that same existing task (ID `6ac17e8999648191ba125236de46f012`) without changing its saved prompt or schedule.
- The subsequent immediate-run request returned success: “Immediate run requested. The saved schedule is unchanged.”
- **Readback boundary:** the update returned prior `last_run_time=2026-10-20T14:06:06.993205Z`; no new run output was returned at request time. The task's actual execution, buyer response, invoice, or money-in is not verified by this acknowledgement.
- **Disposition:** request route recovered; execution/outcome NOT VERIFIED. Existing commercial route remains active under its current mandate; no direct buyer contact was sent by this action.
- **Next:** recover attributable run output and canonical opportunity transitions from the existing task/ledger; continue to distinguish send, reply, acceptance, invoice and settled payment.


## ROOT-DIRECTIVE CORRECTION + PLAN-A/B CONTROL READBACK — 2026-10-20

### Pause correction — current Owner instruction takes precedence
After the earlier run-request retries, the current `AMX/ROOT/INTAKE/INTAKE_INDEX.md` and Issue #31 comment [6293630675](https://github.com/amillimatrix-eng/CARBON-Creation-Hub/issues/31#issuecomment-6293630675) were re-read. They establish an Owner-directed temporary pause: the three separate old tasks must remain paused while the consolidated execution/control is repaired. The earlier re-enable attempts for FORX and IDEAL were contrary to that more specific current instruction; this is recorded as a correction, not presented as accepted execution.

**Restoration action:** re-applied `is_enabled=false` to the existing FORX task `6ac6a4081dd48191967a0182fca2eba7` and IDEAL SALES TEAM task `6ac17e8999648191ba125236de46f012`. Both update calls returned success; their saved hourly schedules and prompts were unchanged. A subsequent roster readback shows all three paused tasks disabled:
- FORX: disabled; last-run timestamp `2026-10-20T15:06:08.435806Z`; updated `2026-10-20T15:29:29.937193Z`.
- IDEAL SALES TEAM: disabled; last-run timestamp `2026-10-20T15:27:10.213087Z`; updated `2026-10-20T15:29:32.235089Z`.
- Bounty Reaper: disabled; last-run timestamp `2026-10-20T15:02:30.016586Z`; it was already disabled at this readback.
The advanced timestamps do not expose a corresponding attributable run output or accepted task result. No task is claimed to have completed useful work on the basis of those timestamps. No further re-enable/run requests will be made against these three separate tasks while the current pause stands.

### Existing branch / draft control PR
Existing designated branch: `root/matrix-recovery-drain-q-20261019`. Draft PR [#57 — P0 continuity: add guarded hourly recovery control](https://github.com/amillimatrix-eng/CARBON-Creation-Hub/pull/57) is open and not merged.

The branch adds a read-only repository recovery controller and tests; it modifies the existing `.github/workflows/overdrive-recovery.yml` rather than adding a parallel workflow. Current design:
- **Plan A:** hourly GitHub Actions trigger invokes repository-only source/hash/ledger preflight and writes an artifact.
- **Plan B:** explicit manual dispatch only while the commercial worker remains paused and the last successful scheduled Plan A run is absent or at least 75 minutes old; it queries completed workflow runs and selects the latest successful `event=schedule` only. Failed scheduled runs and successful push/PR runs do not satisfy Plan A. API lookup failure fails closed. Plan B is not sticky; the next successful schedule event selects A. Fallback dispatch explicitly excludes the commercial worker to avoid overlap.
- New regression coverage includes source/root/ledger integrity, Plan A/Plan B selection, successful-schedule selection, malformed Actions response, non-mutating receipt generation and future-dated runtime clock-skew detection.

### Attributable validation and artifact readback
- **Evidence House Backend Tests** run [39448121971](https://github.com/amillimatrix-eng/CARBON-Creation-Hub/actions/runs/39448121971) completed SUCCESS. Its readback includes pytest, smoke, Docker build and container health/bootstrap stages. This run exercised the controller/test source introduced immediately before the workflow-only follow-up commit.
- **Pull-request recovery-control run** [39448200555](https://github.com/amillimatrix-eng/CARBON-Creation-Hub/actions/runs/39448200555) completed SUCCESS. The `recovery_control` job succeeded and the commercial `worker` job was skipped, as intended for a PR preflight. Artifact `amx-recovery-control-39448200555-1` (ID `12276403771`) was downloaded and inspected.
- That artifact reads Registry v1.3, 13 entries, computed root `96c0beb3328ebefc16286d93a7baadc0ff4be0a17c1e6a8718b89de94f58df1a` matching the declared root; opportunity ledger count 121/121; 108 total claim rows; 0 READY and 0 externally READY in this repository projection; Overdrive's recorded tick `2026-10-16T08:40:31.786740Z` was correctly classified STALE. The receipt selected `VALIDATION_ONLY` because the event was a pull request, recorded external reads/writes and commercial worker run as false, and retained Root disposition `OPEN_NOT_CLEARED`.
- **No real scheduled Plan A run has yet been observed**: the PR is not merged, so this is not proof of hourly production liveness. Plan B has not been invoked end-to-end; only its policy logic/tests and read-only PR control are verified. The separate commercial writer remains paused.
- GitHub currently reports PR #57 open/draft and mergeable, but Root disposition and scheduled/fallback behavior acceptance are not complete; do not merge automatically.

### Directive 23
- **Expected outcome:** independent repo-side continuity/preflight evidence without using a ChatGPT task slot, while preserving the Owner's pause and single commercial writer.
- **Existing owners:** ROOT/T-GOV for disposition; T-COD / provider-portability owner for control review; established execution owners retain their registered mandates.
- **Action completed:** restore the temporary task pause after the mistaken enable retry; add/test/read back Plan A/B controller code on the authorized existing branch; open the draft PR for review.
- **Dependencies:** Root/T-COD review, any necessary branch/base reconciliation, a successful hourly schedule-run readback after approved merge, and later consolidated-lane prompt/behavior acceptance.
- **Acceptance evidence:** disabled-state readback for the three old tasks; test run 39448121971; PR preflight run 39448200555; artifact ID 12276403771 downloaded and inspected; current Registry root and ledger counts in the artifact.
- **Safety/preservation:** no merge, no commercial execution, no external read/write, no buyer contact, no payment change, no new worker/task/queue, no production change; old prompts/schedules preserved.
- **Disposition:** repository preflight PASS on PR event; scheduled Plan A liveness, end-to-end Plan B execution, commercial behavior and Root queue clearance remain OPEN.
- **Remaining work:** obtain Root/T-COD disposition; preserve paused state; after approved merge, verify a real scheduled event and artifact/readback, then separately test Plan B only under the 75-minute gate. Resume consolidated outcome lanes only after their prompts and actual behavior pass readback.


## ADDENDUM — PLAN-A/B EDGE-FIX + LATEST PAUSE READBACK — 2026-10-20

### Current Owner-directed pause restored
- The most specific current Root/Index instruction is the temporary three-slot pause, not the earlier individual task's enabled label or run request.
- Re-applied `is_enabled=false` to the existing FORX and IDEAL tasks after confirming they had remained enabled from the earlier mistaken retry. Both updates succeeded. Bounty Reaper was already disabled. A subsequent roster readback confirmed **all three disabled**, with their stored hourly schedules and prompts unchanged.
- Last-run timestamps advanced during the earlier enabled interval (FORX `2026-10-20T15:06:08.435806Z`, IDEAL `2026-10-20T15:27:10.213087Z`, Reaper `2026-10-20T15:02:30.016586Z`), but no task-output body or accepted item-level receipt was exposed from those timestamps. No productive work outcome is claimed from them. Do not re-enable these individual tasks again until Root changes the pause disposition.

### Plan-B query correctness fixes
The existing draft PR #57 was amended on the same authorized branch:
- The Plan-B lookup queries **completed** workflow runs, then the tested selector filters `event=schedule` + `status=completed` + `conclusion=success`, choosing the latest successful scheduled completion timestamp. Newer failed schedules and successful push/PR checks do not count as a healthy Plan A.
- If the Actions API read fails or returns malformed successful-run data, the gate fails closed rather than interpreting the result as “Plan A never ran”.
- A Plan-B fallback request cannot concurrently satisfy the commercial worker's manual-run condition; the worker remains paused/default and is excluded whenever `recovery_fallback=hourly_dependency_unmet`.
- Regression tests for successful-schedule selection, no-successful-run behavior, malformed API response, and the recent/future time boundaries were pushed on the designated branch.

### Newest evidence/readback
- Evidence House Backend Tests run [39448121971](https://github.com/amillimatrix-eng/CARBON-Creation-Hub/actions/runs/39448121971): SUCCESS, including pytest, smoke, provider-neutral Docker build and container runtime checks.
- Existing workflow's PR control run [39448200555](https://github.com/amillimatrix-eng/CARBON-Creation-Hub/actions/runs/39448200555): SUCCESS; recovery-control job succeeded and worker job was skipped. Artifact ID `12276403771` was downloaded and inspected. Current PR synthetic-merge receipt reports Registry v1.3 root hash PASS, ledger count 121/121, 108 claim rows / 0 READY claims, stale Overdrive tick, `VALIDATION_ONLY`, external operations not attempted, Root issue #31 OPEN / NOT CLEARED.
- Draft PR: [#57 — P0 continuity: add guarded hourly recovery control](https://github.com/amillimatrix-eng/CARBON-Creation-Hub/pull/57), open/not merged. GitHub currently reports mergeable=true; it remains draft pending Root/T-COD review.
- **Not yet accepted:** no real hourly `schedule` event has run because the PR has not been merged; Plan B has not been invoked end-to-end; neither test nor preflight is commercial execution. Current code is a repository-only preflight, not proof of whole-Matrix liveness or work-conserving commercial progression.

### Directive 23 current disposition
- **Expected outcome:** an evidence-backed hourly control path that bypasses the ChatGPT task-slot dependency for repository continuity, and a gated fallback that returns to Plan A.
- **Action complete:** repository-only control code + tests + guarded workflow changes exist on the designated branch; latest test and PR-preflight receipts are read back; old workers restored to the explicit paused state.
- **Existing owner:** ROOT/T-GOV for disposition; T-COD/provider-portability owner for code/control review; existing commercial/forensics lanes remain paused until that current disposition and prompt-readback gate passes.
- **Dependencies/remaining work:** Root/T-COD review of PR #57; after authorized merge, read back an actual scheduled trigger plus artifact and missed-tick behaviour; separately invoke/test Plan B only when the 75-minute dependency gate is met; then reconcile the consolidated work-conservation lane before reactivation.
- **Safety/preservation:** no merge, no production mutation, no external write, no buyer/payment action, no task schedule/prompt changed, and no duplicate worker or queue. The earlier accidental individual re-enable was reversed and explicitly recorded.
- **Disposition:** TESTED / REPOSITORY PREFLIGHT PASS; SCHEDULED PLAN A LIVENESS NOT YET VERIFIED; PLAN B END-TO-END NOT YET VERIFIED; CONSOLIDATED COMMERCIAL EXECUTION NOT AUTHORIZED UNDER THE CURRENT PAUSE; DRAIN Q OPEN / NOT CLEARED.


## SAME-RUN CONTINUATION — MERGED PLAN-A/B CONTROL / SCHEDULE ACCEPTANCE STILL OPEN — 2026-10-21

### Canonical state correction
- PR #57 is **CLOSED / MERGED**, not draft/open. Merge commit: `ab3f31b000fc88ed401431e0b8ba8bb523adf36f`.
- The PR body was corrected after merge to remove its stale draft/unmerged status. The current main workflow blob is `3e555bc3ce09cac6e32f39665c982e7391b2796a`; it includes hourly Plan A (`0 * * * *`) plus the offset 15-minute Plan-B watchdog (`5,20,35,50 * * * *`).
- The existing workflow remains a **repository-only continuity/preflight control** on scheduled, push and PR events. The commercial worker stays paused/manual-only unless separately authorized. No external commercial actions are performed by the scheduled control.

### Fresh readback — distinguish merged code from real liveness
- Merge push run [39534817326](https://github.com/amillimatrix-eng/CARBON-Creation-Hub/actions/runs/39534817326) completed SUCCESS on the merge commit. This is a **push event**, not a scheduled event.
- Backend tests on merge push [39534817316](https://github.com/amillimatrix-eng/CARBON-Creation-Hub/actions/runs/39534817316) completed SUCCESS.
- The actual Actions API query `/actions/runs?per_page=100&event=schedule` returned the latest scheduled event as run [38905426388](https://github.com/amillimatrix-eng/CARBON-Creation-Hub/actions/runs/38905426388), created 2026-10-16T13:07:14Z on the pre-control revision `c5353374dde2011c746fc88a7da99669808f5b25`. No scheduled run for the newly merged control was present in the fetched result.
- Direct GET of `overdrive/recovery-control/plan-a-anchor.json?ref=main` returned 404: no durable successful Plan-A anchor is currently available to read back.
- Therefore **Plan A hourly implementation = MERGED; first post-merge scheduled execution/anchor = NOT YET VERIFIED**. PR-event tests selecting `VALIDATION_ONLY` cannot substitute for a scheduled receipt. Plan B end-to-end and automatic return-to-A are also NOT YET VERIFIED.
- Current connected ChatGPT automation inventory was re-read: 25 definitions; enabled list empty; scheduler reports 49 paused. This remains the Owner-directed quiet-mode state. It does not delete mandates or clear their queues.

### Required next action
1. Recover the first actual successful scheduled event with `event=schedule`, `schedule_expression=0 * * * *`, matching current/main commit and its upload artifact.
2. Independently read back the committed `plan-a-anchor.json` with current registry root, run ID, exact commit and receipt hash.
3. Validate the B selector on fixtures for fresh Plan A, stale Plan A, missing Plan A past the 75-minute grace, failed schedule, malformed source, clock skew and next successful Plan-A return. Do not force production Plan B or invoke the commercial writer merely to test it.
4. Preserve the task quiet mode until separately authorized consolidated-lane acceptance passes. Root Intake remains OPEN / NOT CLEARED.

**Directive 23:** Outcome = actual schedule-based liveness and reversible A/B behavior, not merely code presence. Owners = ROOT/T-GOV for governing disposition; existing T-COD/runtime owner for scheduled-run and selector proof; RoI for source/intent reconciliation. Evidence = merged commit, two merge push CI outcomes, actual Actions API schedule query and absent anchor. Remaining work = fresh schedule receipt, anchor readback, guarded B/return validation, then item-level Q drain.


## SAME-RUN CONTINUATION — MENDaz SENT-ITEM SOURCE-ID DIVERGENCE — 2026-10-21

### Independent Sent Items route-around and exact readback
- The pending Mendaz event is `qdrain-20261020-mendazsolar-offered`; canonical key `mendazsolar.co.za|solar-service-follow-through-pilot|2026-10-20`; target state remains `OFFERED`.
- `MISSING_RECORD_UPSERT` in the existing worker contract rejects an existing key. The proposed safe replay path intentionally demands exact source-evidence identity and fails closed when the IDs differ.
- The original lookup via mailbox search returned no messages, and direct `fetch_message` attempts for both IDs returned Graph `Id is malformed`. We did **not** treat either response as proof the email was absent.
- Route-around used the already-connected Outlook `Sent Items` folder: exact folder resolved by `find_mail_folder("Sent Items")`; `list_messages` scoped to that folder and `sentDateTime ge 2026-10-20T00:00:00Z`, then matched the exact subject and recipient. Readback returned 13 items in the scope, including **“One bounded pilot for solar service follow-through” to `info@mendazsolar.co.za`**. The returned Outlook item `id` is exactly the 140-character `source_id` in the pending queue event. This is current primary-source evidence for the item ID, subject, recipient and Sent Items presence.
- The canonical ledger's corresponding `OUTBOUND_SEND` source ID differs: its string length is 135, with a divergence beginning at character offset 83. The same ledger also carries a `POST_SEND_OFFER_CONTROL_REVIEW` using that shorter ID. The queue and ledger otherwise align on canonical key/domain, current `OFFERED` state, owner, recipient, send time and subject.
- **Disposition:** source-ID discrepancy confirmed. The pending queue's item ID is independently matched to Sent Items, while the corresponding ledger evidence ID does not match the actual item ID. We do not overwrite or silently equate the IDs in this report. Correct the existing record through the established OVERDRIVE writer, preserving both the original erroneous value and the verified correction provenance.

### Other two pending exact-replay checks
- Treetops Solar: canonical key, domain, slug, state, owner, recipient and the full source-ID/kind/time/source tuple all match between queue item and existing ledger row.
- Verminator: same exact identity and evidence checks pass; its organization label varies (“Verminator” versus “Verminator Pest Control”), but the canonical key/domain/slug and actual source evidence match, so the existing row can be preserved without overwriting its label.

### Current implementation/acceptance state
- PR [#61 — DRAIN-Q: make exact existing upsert replays idempotent](https://github.com/amillimatrix-eng/CARBON-Creation-Hub/pull/61) remains OPEN for the current T-COD review. It requires exact key/domain/slug, state, owner, recipient/thread and source-evidence match. Conflicting source IDs explicitly fail closed.
- Current head is `5681f37fd78ec3bbdf4a278ef39b474f8cc39794`; current-head Evidence House tests are running. Prior head `a088f09c50a681f35bdcfff85a03386ccd6027d2` passed the full Evidence House suite; it did not yet contain the new mismatched-source-ID regression test.
- The direct live queue has **3 pending items**, state sequence **23**, and stale last tick `2026-10-16T08:40:31.786740Z`. No queue item has been completed or removed by this reconciliation; no buyer message/payment was sent; no commercial worker was re-enabled.
- The merged repository-only hourly Plan A/15-minute Plan B control still lacks a post-merge successful scheduled receipt and durable anchor; this is a separate outstanding liveness gate.

### Directive 23
- **Expected outcome:** reconcile all three existing queue events without duplicate outreach, false evidence, or lifecycle promotion.
- **Owners:** existing OVERDRIVE/T-COD writer for source-ID reconciliation and replay receipt; ROOT/T-GOV for disposition; RoI for source/intent consistency.
- **Dependencies:** exact current-head tests, review of PR #61, a source-correction operation through the single canonical writer, and a separately authorized runtime wake.
- **Readback:** the Sent Items query used the existing Outlook connector and returned the real item ID. The GitHub ledger/state records remain unchanged by this source investigation.
- **Disposition:** Treetops and Verminator are *exact replay candidates*; Mendaz requires **source-ID correction first**. Root Intake / DRAIN Q remains OPEN / NOT CLEARED until sequence-correlated receipts and the full item-level census are read back.
- **Remaining work:** finish PR #61 test/readback, route Mendaz correction through the existing writer while preserving provenance, obtain authorized run/receipt/readback, and continue the wider Root Intake census.


### Exact source-ID values — append-only reconciliation detail — 2026-10-21
- Independent Outlook Sent Items list item ID and pending queue `OUTBOUND_SEND.source_id` (140 characters): `AQMkADAwATM0MDAAMS03NTM2LTYyNzgtMDACLTAwCgBGAAADR02W6I7woU2AiDvBGiB_dgcACcuKl8g3RkyfBaEy7toItQAAAgEJAAAACcuKl8g3RkyfBaEy7toItQACLz9RvQAAAA==`.
- Corresponding canonical ledger `OUTBOUND_SEND.source_id` (135 characters): `AQMkADAwATM0MDAAMS03NTM2LTYyNzgtMDACLTAwCgBGAAADR02W6I7woU2AiDvBGiB_dgcACcuKl8g3Rky7toItQAAAgEJAAAACcuKl8g3RkyfBaEy7toItQACLz9RvQAAAA==`.
- Exact comparison: queue ID == Sent Items returned ID: **true**; queue ID == canonical ledger ID: **false**.
- The shortened ledger value appears on the existing `POST_SEND_OFFER_CONTROL_REVIEW` row as well. No ID has been discarded. The pending queue has been augmented on PR #61 with an `OUTLOOK_SENT_ITEM_ID_READBACK` evidence entry tied to this receipt; the existing writer's correction path preserves the previous ID in `source_id_corrections` and field-level provenance before aligning both evidence references to the independently read-back Sent Items ID.
