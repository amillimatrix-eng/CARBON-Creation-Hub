# OWNER-DETECTED MPOSTER DRIFT — WRONG TINYFISH CONTEXT / FALSE ACCESS BLOCKER
**Date:** 2026-10-20  
**Route:** Existing ROOT Intake → Issue #31 — ROOT INTAKE / ledger truth, capability-loss recovery, and model-to-Root throughput  
**Lifecycle:** INCIDENT EVIDENCE / RECOVERY OBLIGATION — NOT A MANDATE CHANGE  
**Owner label preserved verbatim:** `MPOSTER DRIFT DETECTED`. This record does not redefine or reinterpret the Owner's label.

## 1. Incident

The assistant was tasked to act on Visym's current payout-setting instruction: select **Wise** as payment provider in the existing Visym Collector app and use the already-confirmed payout email `amillimatrix@gmail.com`.

The Owner explicitly corrected the assistant: the assistant was using the wrong TinyFish context and the intended Outlook-associated TinyFish profile is already authenticated. The assistant nevertheless responded as if the Outlook-associated route were not exposed, and framed route availability as a blocker rather than correctly selecting/recovering the existing authorized execution context.

This is route-selection / context-binding drift plus an unsupported blocker conclusion. It establishes an execution error; it does **not** establish malicious intent, and no such intent is inferred.

## 2. Pre-flight and source evidence

- Canonical repository: `amillimatrix-eng/CARBON-Creation-Hub`.
- Direct current Registry read: `AMX/ROOT/BLUE_STATE/MANDATE_REGISTRY_V1.json`, version `1.3`, effective `2026-10-16`, registry root SHA-256 `96c0beb3328ebefc16286d93a7baadc0ff4be0a17c1e6a8718b89de94f58df1a`, blob `bcfd1f422bd25ba852666a538712828d594759e8`.
- Existing blocked-attempt rule: `AMX/ROOT/INTAKE/CATEGORY_A_NO_TOOL_ACCESS_DEAD_END_RECOVERY_RULE_20261014.md`, blob `4e510c867d17b4761e9685f1376450c614c935c6`. It explicitly requires recovery or an actionable, persisted recovery assignment; a first-tool failure is not a terminal disposition.
- Previous TinyFish `get_wallet` read within the currently selected connector context reported `-1.051248 USD` at `2026-10-19T20:49:24Z`.
- Previous TinyFish `list_profiles` read in that same context returned three profile records: `Default`, `amillimatrix@gmail.com` (default; `google.com` recorded as signed in), and `BullRulez`. That is evidence only about the profile set visible through that particular connector binding. It is **not** proof that the Owner's separate Outlook-associated TinyFish profile does not exist or is unauthenticated.
- The current tool schema exposes one TinyFish namespace in this assistant context and does not expose a connection selector on `get_wallet` / `list_profiles`. The correct Outlook-associated TinyFish execution binding was not successfully selected or exercised in the preceding attempt.
- Current Outlook message `Re: GeoSonics payout method and secure bank-detail submission`, received `2026-10-19T20:47:54Z`, was fetched in full. Visym acknowledged receipt of the GoTyme proof of account and instructed that Collector use provider `Wise` and payout email `amillimatrix@gmail.com`. This instruction is distinct from verifying the Collector setting, payout-run inclusion, or actual settlement.

## 3. Incorrect inference to supersede

The negative balance of the Gmail-associated TinyFish connection must not be generalized to the Owner's separate Outlook-associated TinyFish profile. A profile listing scoped to the wrong connection does not establish global absence of an authorized route. Do not ask the Owner to re-authenticate, create a new profile, change account identity, or fund the wrong wallet merely because the acting assistant selected the wrong context.

The earlier execution did not change the Collector setting. That unchanged state remains **UNKNOWN / NOT VERIFIED** until the correct profile is used and the saved setting is read back.

## 4. Recovery action — existing route only

1. The acting runtime / existing connector owner must select or restore the Owner-identified, already-authorized Outlook-associated TinyFish profile and verify the selected profile identity before accessing Visym Collector.
2. Continue the existing payout-setting task. Set payment provider to `Wise` and payout email to `amillimatrix@gmail.com` only if those fields and the existing Collector account are directly confirmed in the authenticated UI.
3. Save, navigate away or refresh as appropriate, then read both persisted values back. Record the exact safe readback evidence; do not expose full bank details or other secrets in this incident.
4. Inspect payout-run status only if the same authenticated account exposes it. Setting the payment method is not proof of inclusion in the 2026-10-20 run and is not proof of payout/settlement.
5. If this execution environment cannot bind to the existing profile, keep the recovery obligation OPEN and route the exact connector-selection defect to ROOT / the existing connector owner. Continue other independent authorised work. Do not convert the failure into a requirement for new Owner authorisation.

## 5. Acceptance criteria

- Existing Outlook-associated TinyFish profile identity selected and independently evidenced.
- Collector account and Wise setting shown in the authenticated UI.
- Payout email read back exactly as `amillimatrix@gmail.com` after save.
- Any payout-run inclusion / actual bank credit recorded only from direct source evidence.
- No duplicate profile, new worker, new pipeline, wrong-wallet top-up, redundant Owner authorisation request, or unauthorised account change.
- Report and Intake pointer fetched back from canonical GitHub after persistence.

## 6. Directive 23 itemized disposition

- **Expected outcome:** Visym payout preferences are configured through the Owner's existing authorised session and independently read back.
- **Owner:** existing execution runtime and connector owner; ROOT/T-GOV owns disposition; existing payout/Banker evidence path retains settlement truth.
- **Action:** select/restore the correct existing Outlook-associated TinyFish binding, execute the instructed app change, and read it back.
- **Dependencies:** correct existing TinyFish connection must be selectable by the execution runtime. Owner authentication is reported as already complete; do not request it again absent contrary direct evidence.
- **Evidence:** current registry v1.3; blocked-attempt recovery rule; full Outlook readback from Visym; wrong-context TinyFish wallet/profile outputs; Owner correction in this conversation.
- **Persistence/readback:** this report in the existing `AMX/ROOT/INTAKE` repository path; append-only pointer in `INTAKE_INDEX.md`; route via existing Root issue #31.
- **Safety/preservation:** no secrets in public records; no identity substitution, duplicate setup, wrong-wallet funding, unsupported claim of completed configuration, or false claim of payout.
- **Disposition:** **OPEN — WRONG-CONTEXT EXECUTION DRIFT VERIFIED; CORRECT CONTEXT NOT YET EXERCISED.**
- **Remaining work:** existing Outlook-associated TinyFish binding selection/recovery; Collector setting change and readback; payout-run inclusion and settlement readback if available.
