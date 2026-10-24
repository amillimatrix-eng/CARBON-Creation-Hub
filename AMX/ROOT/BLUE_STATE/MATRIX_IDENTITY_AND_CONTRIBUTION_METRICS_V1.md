# AMilliMATRiX — Canonical Identity, Hash Ownership and Contribution Metrics V1

**Classification:** CATEGORY A — GOVERNANCE / CONTINUITY / IDENTITY METRICS  
**Status:** Owner-directed additive implementation binding, 2026-10-24. The current worker reasoning/mandate payloads are not modified by this document.  
**Controlling authority:** `AMX/ROOT/BLUE_STATE/BLUE_STATE_MANDATE_BINDING_AND_PREFLIGHT_V1.md` and `AMX/ROOT/BLUE_STATE/MANDATE_REGISTRY_V1.json`.  
**Current registered root SHA-256:** `96c0beb3328ebefc16286d93a7baadc0ff4be0a17c1e6a8718b89de94f58df1a` (computed from the 13 existing `ROLE_KEY=MANDATE_SHA256\n` lines; verified before metadata update).  
**Continuity:** existing ROOT Intake, Index and Dynamic Flight Path Register remain the only governing intake/routing surfaces. This file is a schema/implementation binding, not another queue or authority plane.

## 1. Two identity namespaces — do not conflate them

### A. Permanent worker / authority identity
Every worker instance and execution receipt identifies itself by the exact current registered `role_key`, `mandate_id`, and unchanged mandate SHA-256 from Registry v1.4. Labels in prompts, ecosystem names, colour, session names, model provider, or current conversational context do not create or replace authority identity.

Registry keys and the bound identity are exact:

| Role key / canonical identity | Mandate ID | Existing payload SHA-256 | Current state |
|---|---|---|---|
| `ROOT-TGOV` | `AMX-MANDATE-ROOT-TGOV-V1` | `d92852d15f66168990290aece801b8c8573d48037b88765a081a26d58e10b120` | CURRENT |
| `MASTER-LIBRARIAN` | `AMX-MANDATE-MASTER-LIBRARIAN-V1` | `f127bec771d398c7c2c3a1e746734619568b5641c91d6f810514d08f7f76b4f8` | CURRENT |
| `T-COD` | `AMX-MANDATE-TCOD-V1` | `67a9fc18adc6323ea93f86bc70bb677b7e063b5f6f6a8218d1ec2713c4f0e9b3` | CURRENT |
| `T-MED` | `AMX-MANDATE-TMED-V1` | `3204cb5d8dfcfbc1e904a4a23f0077959bb9371152a2ef32be48e7e858d148f1` | CURRENT |
| `FORX` | `AMX-MANDATE-FORX-V1` | `a9570686dae130bd36d0995d9f58dbd0f7cde1597968dc16245c94a65f0f3109` | CURRENT |
| `FORKS-ROI` | `AMX-MANDATE-FORKS-ROI-V1` | `a61aa5c535aa33be5639850590cdb911b583f8f02e6a23f4e5e6669850bf6ab9` | CURRENT |
| `ISCOPE` | `AMX-MANDATE-ISCOPE-V1` | `6371943e42023ac27c45dbeb973eb33db73843f929c48b57e32c5ee84e461bc7` | CURRENT |
| `PRI` | `AMX-MANDATE-PRI-V1` | `306a3ec9ee64b222e6e73a4e20cbccc07c3e33f7dc450509cf883e40c9fe17fd` | CURRENT |
| `BANKER` | `AMX-MANDATE-BANKER-V1` | `ba568bd0d0370abd4f3a17f3b767b5aae768e10970884acad8bfe07fb99e1daf` | CURRENT |
| `BOUNTY-REAPER` | `AMX-MANDATE-BOUNTY-REAPER-V1` | `754d8fb9b6816da1bf0013940883106e0d3928b1637526ee82b38e1792c1dcd3` | CURRENT |
| `CARBON` | `AMX-MANDATE-CARBON-V1` | `44444338f303acdd481f3a8b67ec3813701e4b655d3a14ba8af3d46350860be6` | CURRENT |
| `MATRIX-CRITIC` | `AMX-MANDATE-MATRIX-CRITIC-V1` | `d3ad5aec0d78058a7f96056808013a4c95f15b35f0f298879f24b5b1fb2f71a4` | CURRENT_WHEN_INVOKED |
| `COMMISSIONING-INSPECTOR` | `AMX-MANDATE-COMMISSIONING-INSPECTOR-V1` | `b7d1a8b6a6ea5726aba8b3043a5a60a031926acc155dc30a3ad37dc98cb4b593` | DORMANT_CAPACITY_MERGED |

The `role_key` is the canonical label to display. `mandate_id` plus SHA-256 confirms which authority payload is in force. Every item/receipt has one primary accountable registered identity; secondary reviewers are explicitly linked. Root and MASTER remain separate authorities; T-COD/T-MED must retain their registered names. No identity is silently renamed, merged, promoted or inferred from a model or ecosystem.

### B. Canonical participant identity — MTXID
Every person entering through any current or future AMX ecosystem resolves to one AMX-owned, opaque MTXID. The MTXID:
- has no ecosystem/source prefix and reveals neither entry route nor referrer;
- is not an authentication secret, permission, reward, rank, contribution proof or payment receipt;
- is never reissued to a second canonical participant;
- stays stable for a participant across HOBO, JAM3S, IRIS, CARBON, Telegram, direct entry and future routes;
- keeps referral/source attribution in a separate event record, linked to a canonical MTXID only after verification.

A private preallocated reserve of **1,000 unique IDs** has been recorded in the owner-private Notion reserve page. Those identifiers are **AVAILABLE / NOT YET ISSUED** and their raw values are deliberately excluded from public repository files. The reserve is not yet connected to a verified live issuer.

### Issuance gate — exact implementation invariant
Reuse and bind the existing canonical identity/referral store (JAM3S is the existing candidate, subject to live database/runtime readback; do not clone its identity graph). The issuer must atomically claim one preallocated ID and persist the participant mapping under uniqueness constraints on both MTXID and canonical participant ID. Requests must be idempotent: a retry for an already-created participant returns the same MTXID. If the current store/route cannot prove atomic uniqueness, leave the assignment pending; do not manually hand out IDs from the reserve. Link authenticated platform identities through controlled records, never by putting raw platform IDs or referral tokens in MTXID.

## 2. Hash register and librarian attribution

The source hash is evidence of exact bytes under a stated algorithm/scope; it does not itself grant authority, decide lifecycle or prove execution. For every hash-bearing artifact in the authorized register, retain:
- stable existing artifact/item ID and exact source/path/record;
- hash algorithm and exact byte scope;
- source version/ref and read timestamp;
- canonical domain/classification;
- one primary librarian identity + mandate ID;
- secondary domain reviewers/dependencies;
- actual lifecycle/status;
- parent/addendum/supersession and previous hash provenance;
- acceptance condition, durable receipt and independent readback state.

Do not move or rename files solely to change their owner. Where the live source/hash register is inaccessible, set `HASH_UNKNOWN / SOURCE_NOT_READABLE`, keep the item open, and name a recovery owner and next action. Never fill an unavailable hash with a guessed digest.

For the 2026-10-24 bounded snapshot, each currently open GitHub issue/PR is hashed as:
`SHA-256(UTF-8(title + LF + complete current GitHub API body))`.
This is an API-body snapshot hash, **not** a Git blob SHA; comments, API metadata and future edits are outside its scope. The exact digest and source URL are in `AMX/ROOT/INTAKE/MATRIX_IDENTITY_METRICS_CURRENT_SNAPSHOT_20261024.json`. At the next census, re-read the actual source and recalculate the digest.

## 3. Contribution metrics — event evidence, not vanity totals

A contribution metric event must carry at least:
- immutable event ID and canonical actor identity (`MTXID` for participants; `role_key` for worker execution);
- source item ID/hash and exact byte scope where applicable;
- contribution type, domain, current lifecycle, timestamp and rule version;
- executor/role identity, reviewer and evidence pointer;
- observed before-state, actual after-state and independently read-back result;
- parent/supersession link, dispute/revocation state and next action.

Keep participant identity and worker authority in separate fields. A person can enter through one ecosystem and later contribute elsewhere without acquiring a second MTXID. A worker may act on a participant's item without becoming the participant.

Use distinct status stages: `OBSERVED`, `SUBMITTED`, `VALIDATED`, `ACCEPTED`, `SETTLED`, `REJECTED`, `REVOKED`, `DISPUTED`, `HOLD/UNKNOWN`. Advance only on evidence for that transition. A proposal, click, login, signup, offer, task wake, open checkout or issued invoice is not interchangeable with accepted work or settled value. BANKER remains the owner of terminal financial/settlement truth; PRI/iSCOPE and domain owners keep their mandates.

### Badges, ranks, battles and achievements
Keep the existing governed rule source, threshold, season and award logic unchanged. Every stored badge/rank/battle result must reference the exact governing rule ID/version and evidence/receipt:
- badges: `PROPOSED` / `AWARDED` / `UNDER_REVIEW` / `REVOKED`, with authority, rule version and evidence;
- rank: current rank, rule/version, evaluated window, contributing accepted events and readback;
- battle: stable battle ID, participants' MTXIDs, rule/round/version, outcome (win/loss/draw/forfeit), verifier and settlement/award status where applicable;
- disputed or unverifiable results never count as wins or final awards.

No new score weights, rank thresholds, badge meanings or battle rules are created by this implementation. If the existing canonical rule source is not available in the current read path, record `RULE_SOURCE_UNKNOWN / HOLD`; preserve the data fields and do not manufacture an award or rank.

## 4. Colour and display integrity

The authorized unique global BUILD/CANON/GOVERNANCE marker mapping has not been located. Display the textual registered identity and domain now, plus `MARKER_UNASSIGNED / REGISTRY_HOLD` where no exact registered marker is evidenced. Do not guess T-COD/T-MED colours, and do not flatten existing colour contexts (GOLD/WHITE/BLACK, MASTER=WHITE, ROOT-LIBRARIAN=RED, FORX/WHITE vs DOM8N/GOLD remain context-bound). Colour is supplementary; it never decides ownership or authority.

The public CARBON° Evidence House is not accepted as the internal Matrix dashboard. Do not expose private MTXIDs, raw reserve values, internal item ownership, run IDs, private hashes or contributor histories through public routes. The eventual internal dashboard must use the already-authorized private access boundary.

## 5. Intake metrics and daily drain

The single operational readout is derived from existing ROOT Intake / Index / source registers; it is not a second queue. On each daily census, display:
- current source coverage and read timestamp;
- count per primary librarian and the exact item keys assigned;
- domain, Category A/B/C or explicit `UNCLASSIFIED` counts;
- lifecycle counts (OPEN, HOLD, ACCEPTED, MERGED, CLOSED only as truly evidenced);
- hash matched/mismatch/unknown counts;
- unowned/untriaged item count and its recovery owner;
- badge/rank/battle evidence state and MTXID reserve/assignment state;
- the exact scope and inaccessible surfaces.

**Daily target: untriaged/unowned intake = 0 at least once per day.** This does not mean all active work must be closed; live authorized obligations remain open until actual acceptance/readback or governed cancellation. A blocked item remains open with a recovery owner, exact blocker and recheck condition. Never report global queue zero from one local subset.

## 6. Current bounded implementation readout (2026-10-24)

- Current live GitHub scope: 15 OPEN issues + 12 OPEN pull requests = **27** records in this repository.
- Each of those 27 records has a stable native key, current body-snapshot SHA-256, domain, one primary librarian identity and linked review owners in `AMX/ROOT/INTAKE/MATRIX_IDENTITY_METRICS_CURRENT_SNAPSHOT_20261024.json`.
- Category readout for the 15 issues: Category A = 1; Category B = 0 explicitly identified; Category C = 1; unclassified = 13. The 12 pull requests are engineering work items, not A/B/C intake categories.
- Current-snapshot librarian counts: T-COD = 16; ROOT-TGOV = 7; MASTER-LIBRARIAN = 1; T-MED = 2; FORX = 1. These counts apply only to the 27-record GitHub scope.
- The existing `HASH_CALIBRATION_TEMP` source is still unavailable to this runtime. Four known gate files remain pending exact-byte capture; the last evidenced OPEN count was 4 and current OPEN is UNKNOWN. Those four are not added to the GitHub count because the dedupe join is not available.
- Whole-Matrix ROOT Intake count, total Category A/B/C inventory, full colour registry and live cross-ecosystem issuer are **not verified**. Do not claim global queue = 0 or the MTXID runtime fully live until source/runtime receipts exist.

## 7. Acceptance contract
T-COD implements the identity allocation/metrics schema against the existing authorized identity store after exact target/database/runtime readback. MASTER/LIBRARIAN maintains the existing hash register/index, computes source-backed counts and independently reads back its rows. ROOT/T-GOV controls current governance/authority and category dispositions. T-MED only applies the registered markers/presentation once the exact registry is recovered. FORX independently verifies the source-to-metadata/result chain. No owner gets authority outside their registered mandate.

Acceptance requires: (1) exact live identity-store/issuer target bound; (2) MTXID uniqueness/idempotency/concurrency tests pass; (3) current role hashes/root match; (4) source-bearing items show owner+hash+scope+category+state; (5) a fresh daily item-level snapshot reconciles; (6) badges/ranks/battles resolve the current rule version and evidence, with no false awards; (7) private fields do not leak through public surfaces; (8) independent readback. Until those tests pass, this work is policy+source-metadata implementation, not a claim of runtime issuer or dashboard completion.
