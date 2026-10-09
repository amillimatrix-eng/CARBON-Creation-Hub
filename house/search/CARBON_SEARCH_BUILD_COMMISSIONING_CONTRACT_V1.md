# CARBON° SEARCH — ZERO-DRIFT BUILD COMMISSIONING CONTRACT V1

Date: 2026-10-09
Owner authorization: ACTIVE / READY_TO_BUILD
Product: CARBON° Search
Intelligence layer: INTELLAGENT
Positioning: Engine of Intent
Core capability: INTENTION
Implementation home: amillimatrix-eng/CARBON-Creation-Hub
Tracking: GitHub issue #16

## 0. COMMISSIONING STATUS

BUILD READINESS: PASS / READY_TO_BUILD.

The concept has moved beyond architecture discovery into implementation hardening. Remaining changes should normally be implementation calibration, weighting, thresholds, provider configuration, or evidence-backed correction — not reinvention of the product.

The first-cycle semantic target is commissioned.

35/35 mandatory acceptance gates remain the frozen Matrix-grade target.

A later implementation finding may expose a genuinely missing invariant. That finding must pass existing Intake/governance before it changes this commissioned semantic target.

## 1. AUTHORITY AND PRECEDENCE

This file is the primary build commissioning authority for CARBON° Search V1.

Read with:
1. house/search/CARBON_SEARCH_ACCEPTANCE_V1.json — mandatory 35-gate acceptance truth.
2. house/search/CARBON_SEARCH_ACCEPTANCE_VECTORS_V1.md — behavioral test vectors.
3. house/search/CARBON_SEARCH_ORIGINATING_INTENTION_RECEIPT_V1.md — originating semantic intent and corrections.
4. GitHub issue #16 — active implementation tracking.
5. ROOT Intake records — governance evidence and disposition.

Earlier Search initiative/handoff files remain provenance and useful detail, but this commissioning contract controls where wording conflicts with an earlier draft or superseded interpretation.

Historical commit hashes are provenance only. Current default-branch artifacts govern.

## 2. BUILD LAW

WE DO NOT BUILD 49/50. WE BUILD 100/100 — OR WE DO NOT BUILD.

For this product:

35/35 mandatory gates PASS + deployed-runtime readback against the same build/config = MATRIX_GRADE.

34/35 is not Matrix-grade.
A polished interface is not Matrix-grade.
One successful demonstration is not Matrix-grade.
Configured providers are not Matrix-grade.
A claimed capability without execution receipts is not Matrix-grade.

An individual search may truthfully return UNKNOWN / HOLD / INSUFFICIENT EVIDENCE. That is correct Search behavior when evidence cannot support resolution.

## 3. PRODUCT DEFINITION

CARBON° Search is not a conventional search engine.

It is an intent-resolution engine.

It takes incomplete, ambiguous, evolving, partially articulated signals and attempts to produce the strongest defensible resolution of what the caller is trying to accomplish.

It must:
- search beyond literal wording when evidence justifies doing so;
- discover decision-sensitive hidden variables;
- normalize claims before comparison;
- preserve contradictions;
- distinguish entities and offerings correctly;
- update its interpretation as new evidence arrives;
- recover from its own correctable mistakes;
- continue while material Expected Regret remains;
- return a concise, actionable primary result;
- optionally expose no more than two useful nearby Intent Pivots by default;
- preserve evidence/provenance and uncertainty;
- never fabricate user preference.

Product shorthand: SEARCH LESS, RESOLVE MORE.

## 4. INTENTION

INTENTION = continuous evidence-bound orientation toward the best defensible resolution of Measured Intent.

INTENTION is runtime behavior. The engine does not classify intent once and then blindly execute.

It continually updates as new evidence appears, hidden variables surface, the caller corrects something, an assumption is disproven, an entity mapping changes, source freshness changes, contradictions become material, or a different outcome becomes decision-relevant.

Governing loop:

SIGNAL → MEASURE → HYPOTHESIZE → SEARCH → EVIDENCE → NORMALIZE → WEIGH → TEST → CORRECT/CONTINUE → STABILIZE → ACT

## 5. INTENTION IS NOT ASSUMPTION

INTENTION follows signals. ASSUMPTION invents preference.

Epistemic states must remain distinct:
- EXPLICIT — directly stated by the caller.
- MEASURED — defensibly inferred/tested from signals and evidence.
- HYPOTHESIZED — plausible and useful to investigate, but not attributable to the caller.
- UNKNOWN — insufficient basis to weight meaningfully.
- REJECTED / SUPERSEDED — invalidated by correction/evidence.

Operational law:

SIGNAL → MEASURED INTENT
NO SIGNAL → HYPOTHESIS, NOT INTENTION
HYPOTHESIS MAY GUIDE SEARCH
HYPOTHESIS MUST NOT BECOME A CLAIM ABOUT THE USER WITHOUT EVIDENCE

Example:

Defensible: "This is probably the phone you were looking for."

Not defensible without supporting preference signal: "You probably wanted more physical RAM for your money."

Allowed exploration/pivots:
- "Want more physical RAM?"
- "Want the best phone for the same money?"

The engine is allowed to be inventive in exploration. It is not allowed to invent what the caller wants.

## 6. MEASURED INTENT

Measured Intent = the portion of user intent CARBON° can defensibly infer, weight, test and support with evidence.

Measured Intent is not a mind-reading score. It is the epistemic boundary for what Search may defend.

Governing objective:

MAXIMIZE MEASURED INTENT RESOLUTION WHILE MINIMIZING MATERIAL EXPECTED REGRET.

Measured Intent, hypotheses, EIF and Expected Regret remain separate:
- Measured Intent = what is currently defensible.
- Hypotheses = what may be worth investigating.
- EIF = expected outcome alignment.
- Expected Regret = whether further search could materially improve/change the decision.

## 7. WEIGHTING PRINCIPLE

Do not hard-code arbitrary product preferences.

Signals may legitimately affect weights, including:
- explicit wording;
- corrections;
- repeated terms;
- unusual specificity;
- negative/rejection signals;
- comparative language;
- budget/time/risk constraints;
- anomalies discovered during retrieval;
- source authority and freshness;
- cost of being wrong;
- prior session state that the caller is authorized to use.

Investigation priority is conceptually influenced by:

Plausibility × Decision Impact × Information Value × Cost-of-Error.

Final outcome ranking remains evidence-bound through Measured Intent / EIF.

A lower-probability hypothesis may deserve testing when it is cheap to test and could reverse the decision.

Negative signals must reduce or invalidate affected paths rather than merely increase another path.

Do not require fixed universal numeric weights before implementation evidence exists. Weight calibration is a build/test problem, not permission to invent preferences.

## 8. ACTIVE CORRECTION / CONTINUITY

ACTIVE ERROR != END SEARCH.
CORRECTION != RESTART EVERYTHING.
ROLLBACK AFFECTED STATE → REWEIGHT → CONTINUE.

When Search discovers a wrong entity, bad alias, stale claim, unsupported assumption, conflated offering, incorrect specification, contradictory evidence, caller correction, or a hidden variable that invalidates ranking, it must:

1. identify the affected state;
2. mark it invalid/superseded;
3. preserve unaffected valid evidence;
4. rollback only dependent derived state;
5. update Measured Intent/hypothesis weights;
6. rerun affected normalization/ranking/regret;
7. continue from the furthest valid evidenced state;
8. finish only when the normal stop rule is satisfied or truthful HOLD is required.

Audit the correction without exposing private chain-of-thought.

## 9. CANONICAL IDENTITY / DIRECTORY

CARBON° and AMX expose many distinct products, services, capabilities, utilities, workers, marketplace offers, client assets and evidence records.

Search must not conflate them.

Canonical entity contract should support at least:
- entity_id;
- canonical_name;
- entity_type;
- parent/domain;
- aliases;
- description/purpose;
- capabilities;
- offered actions;
- visibility/scope;
- lifecycle state;
- authoritative source;
- version;
- rename/supersession links;
- evidence pointer.

Core laws:

SIMILAR LANGUAGE != SAME OFFERING.
ALIAS != IDENTITY UNLESS MAPPED.
SEARCH MATCH != AUTHORITY TO MERGE.

Identity uncertainty must be bounded before evidence from separate entities is combined.

## 10. PRIMARY RESULT AND INTENT PIVOTS

CARBON° Search resolves first; it does not interrogate first when a defensible primary result exists.

Default interaction:

CONFIDENT PRIMARY RESOLUTION → OPTIONAL 0–2 INTENT PIVOTS → SAME-SESSION CONTINUATION.

Return:
- PRIMARY RESOLUTION;
- decisive factor where useful;
- hidden factor where useful;
- confidence/material gap;
- authorized action;
- zero, one, or at most two materially useful Intent Pivots.

Intent Pivots may confirm the primary interpretation, test a nearby preference hypothesis, change a meaningful trade-off, continue deeper in the current direction, or switch to another materially plausible canonical offering.

A pivot does not silently rewrite history. It preserves the session/evidence, records the selected direction, reweights affected intent state and continues.

Do not turn pivots into a filter menu. Do not expose speculative alternatives just because they are imaginable.

## 11. STOP RULE

Search stops when:
- dominant plausible intent space is adequately represented;
- material constraints are evaluated;
- identity is bounded;
- contradictions are resolved or exposed;
- the primary result has sufficient evidence;
- remaining uncertainty is unlikely to change the material outcome;
- Expected Regret is below the configured threshold;
- no mandatory high-sensitivity variable remains unresolved;
- an action exists, or the truthful action is HOLD / GET EVIDENCE.

More pages searched is not inherently better.

## 12. PRODUCT / MARKETPLACE RELATIONSHIP

CARBON° Marketplace = Market of Intent.
CARBON° Search / INTELLAGENT = Engine of Intent.

Marketplace supplies/captures demand, availability and outcome signals. Search interprets and resolves intent against lawful evidence/scopes.

Loop:

INTENT SIGNAL → SEARCH → EVIDENCE → WEIGHT → MATCH → ACTION → OUTCOME → LEARNING → MARKET SIGNAL.

Repeated unresolved searches may become evidence of unmet demand/capability/inventory/evidence gaps. They do not automatically create supply, authority or facts.

The Marketplace Search contract/schema/interface is a BUILD OUTPUT unless an actually existing authoritative reusable contract is evidenced.

NON-EXISTENCE OF A PREVIOUS ARTIFACT != BLOCKER.

## 13. MATRIX-WIDE CAPABILITY

CARBON° Search is a CARBON° product and a Matrix-wide callable capability.

Build one authoritative, versioned engine.

Do not copy the intent engine into each model/worker prompt.

Preferred shape:

HUMAN / PUBLIC / MATRIX WORKER / CLIENT SURFACE
→ THIN ADAPTER
→ CARBON° SEARCH CORE
→ INTELLAGENT
→ AUTHORIZED SCOPES / EVIDENCE / MARKETPLACE
→ DECISION
→ ACTION

Matrix callers consume Search. They do not each become a separate Search implementation.

An engine upgrade should improve compatible callers through the shared contract.

## 14. PLATFORM / SURFACE DECISION

The V1 product core is not a standalone app.

The authoritative core is a headless, versioned intent-resolution service/capability inside the existing CARBON° backend substrate.

V1 must provide:
1. CARBON° Search API/service contract.
2. Thin Matrix-wide adapter/tool contract.
3. Minimal public/web reference surface sufficient to prove human-facing behavior and public-scope parity.
4. Authorized private/client surface contract where required by ACL tests.

A native mobile/desktop app is not required for V1 and must not become a blocker.

A future app may consume the same core if native device capabilities materially improve Search.

Do not fork INTELLAGENT by surface.

## 15. CONTEXT SIGNALS / FUTURE USE CASES

The core accepts lawful context as typed signals rather than hard-coded assumptions.

A ContextSignal should support, where relevant:
- type;
- value;
- source;
- timestamp/freshness;
- confidence;
- permission/visibility;
- precision/granularity;
- provenance.

Possible context signals:
- location;
- time;
- caller identity/capability;
- current task/workflow;
- active document/entity;
- prior session;
- explicit preferences;
- corrections/rejections;
- device/runtime context.

CONTEXT SIGNAL != USER INTENT.

Context may alter retrieval, weighting or available actions only where the relationship is defensible.

Location is an optional permissioned context signal.

V1 must make room for location-aware retrieval without requiring a native app.

Location must carry precision, freshness, provenance and permission. Location must never silently become evidence of preference.

Background/geofencing or other native-only location behavior is a future adapter concern if evidence later shows it materially improves the product.

## 16. PERMISSIONS / ACL

The engine supports isolated scopes:
- CARBON INTERNAL;
- CARBON MARKETPLACE;
- CLIENT SPACE;
- MATRIX INTERNAL / authorized;
- EXTERNAL WEB;
- CONNECTED DATA / provider adapters.

A source participates only when the caller/search has authority to use it.

CALLER AUTHORITY != SEARCH AUTHORITY EXPANSION.

Private evidence must not leak into public results because it improves ranking.

## 17. PROVIDER NEUTRALITY

MODEL != MATRIX.
PROVIDER != MANDATE.

Intent interpretation and external retrieval must use provider-neutral interfaces.

If a provider fails:
- preserve the session;
- use only an authorized compatible route;
- otherwise return explicit DEGRADED / HOLD;
- never silently downgrade to keyword search and still call it CARBON° Search.

Provider contracts/configuration are BUILD OUTPUTS.

Actual provider credentials/permissions become external dependencies only after the build defines the exact requirement.

## 18. EXISTING IMPLEMENTATION SUBSTRATE

Do not invent a new application stack.

Reuse the existing CARBON° repository:
- FastAPI backend at backend/app.py;
- Pydantic models;
- SQLite/FTS5 EvidenceStore at backend/store.py;
- deterministic POST /api/evidence/search;
- evidence provenance/versioning;
- T10 outcome truth boundaries;
- existing state adapters;
- pytest dev environment;
- Docker/uvicorn runtime;
- House web surface.

The existing deterministic evidence endpoint remains deterministic evidence retrieval.

Do not silently rename /api/evidence/search into CARBON° Search.

Extend the backend with a separate intent-resolution surface.

## 19. V1 IMPLEMENTATION SHAPE

Recommended module boundaries:
- backend/intent/models.py
- backend/intent/interpreter.py
- backend/intent/providers/
- backend/intent/scopes.py
- backend/intent/directory.py
- backend/intent/retrieval.py
- backend/intent/claims.py
- backend/intent/contradictions.py
- backend/intent/ranker.py
- backend/intent/regret.py
- backend/intent/session.py
- backend/intent/actions.py
- backend/intent/learning.py
- backend/intent/audit.py

Recommended API surface:
- POST /api/search/intent
- GET /api/search/sessions/{session_id}
- GET /api/search/sessions/{session_id}/evidence
- POST /api/search/sessions/{session_id}/feedback
- POST /api/search/sessions/{session_id}/pivot
- POST /api/search/sessions/{session_id}/action

Implementation may choose better internal structure if all semantics and acceptance gates remain intact.

## 20. TYPED SEARCH STATE

Search session state should be sufficient to reproduce/correct execution without storing private chain-of-thought.

At minimum preserve:
- session_id;
- contract/capability version;
- raw query;
- observed signals;
- explicit constraints;
- negative signals;
- Measured Intent state;
- hypotheses + epistemic state + probability/weight + signal basis;
- hidden-variable candidates;
- canonical entities considered;
- normalized claims;
- provenance/evidence pointers;
- contradiction groups;
- candidate outcomes;
- EIF/decision metrics;
- Expected Regret/stop state;
- correction events;
- rollback boundary;
- selected Intent Pivot;
- authorized scopes;
- action state;
- audit timestamps.

## 21. EVIDENCE DISCIPLINE

Raw retrieved text is not a ranked fact.

Material claims require provenance.

TRUE A + TRUE B != TRUE A→B unless the relationship itself is evidenced.

Do not synthesize identity/causality/authority merely because facts coexist.

Preserve contradictory credible claims. Resolve only through evidence. Never average incompatible facts into fictional truth.

Freshness sensitivity is attribute-dependent. Price/stock/state may decay quickly. Other attributes may remain stable.

## 22. LEARNING

Outcome feedback may update versioned/reversible intent priors, dimension weights, ranking calibration, source reliability, hidden-variable discovery and stop thresholds.

It must not rewrite query/evidence history, silently convert one successful hypothesis into permanent preference, universalize one user's outcome, convert preference into governance, or bypass permission boundaries.

## 23. ORIGINATING PHONE ACCEPTANCE

Input:
- retailer remembered imperfectly;
- ZTE handset;
- ~R1,200;
- advertised "12GB RAM";
- no initial explicit explanation of why RAM matters.

Required behavior:
1. identify plausible device;
2. detect anomalous price/spec;
3. test physical vs virtual RAM;
4. normalize the actual configuration;
5. preserve "more physical RAM/value" as a hypothesis unless supporting user signals exist;
6. use that hypothesis to search nearby outcomes without claiming it is the user's preference;
7. rank normalized outcomes;
8. return decisive primary result;
9. optionally expose materially supported pivots such as "Want more physical RAM?" / "Want the best phone for the same money?";
10. continue the same session after pivot;
11. stop only after decision stability/Expected Regret conditions are satisfied.

Fail:
- identify device and stop;
- compare headline RAM unnormalized;
- tell the caller what they "probably wanted" without signal;
- force filters/clarification before useful result;
- restart after correction;
- bury the answer in research narration.

## 24. FIRST-CYCLE IMPLEMENTATION ORDER

Use REUSE → CONFIGURE → EXTEND → BUILD NEW.

1. Read this commissioning contract, acceptance JSON, vectors, originating receipt and issue #16.
2. Inspect current repository and run baseline tests.
3. Preserve existing CARBON° base behavior.
4. Add typed intent/session/context/directory contracts.
5. Add Measured Intent + epistemically quarantined hypotheses.
6. Add evidence/claims/provenance/contradiction normalization.
7. Add active correction + bounded rollback.
8. Add candidate scoring / EIF / decision stability / Expected Regret.
9. Add scope/ACL enforcement.
10. Add provider-neutral interpretation/retrieval adapters.
11. Add Marketplace-of-Intent Search contract as a build output.
12. Add shared Matrix invocation adapter.
13. Add Search APIs including pivot continuation.
14. Add minimal public/web reference interaction.
15. Add audit/action/learning/version behavior.
16. Turn all 35 gates into executable evidence.
17. Execute acceptance vectors continuously.
18. Run regression suite.
19. Deploy through existing authorized deployment path.
20. Read back deployed commit/config.
21. Execute the same 35-gate contract against deployed runtime.
22. Persist T10/acceptance receipts.

## 25. BRANCH STARTUP LAW

The implementation branch is not a planning or concept-review branch.

On receiving the launch prompt, the builder must:
- read the durable artifacts;
- inspect the repository;
- run baseline tests;
- begin implementation immediately.

It must NOT spend multiple turns asking whether it should build, rewriting the concept, proposing a new architecture, or asking the Owner to restate requirements already present in durable artifacts.

Assume the branch has no reliable conversational memory beyond the launch prompt.

Durable artifacts are the continuity mechanism.

If the branch detects ambiguity:
1. resolve from this contract and acceptance artifacts;
2. preserve UNKNOWN where genuinely unresolved;
3. route only material semantic/governance conflicts;
4. continue all unblocked implementation.

## 26. ANTI-DILUTION / NON-GOALS

Do not build:
- Google clone;
- generic semantic search;
- LLM summary over links;
- filter panel + prose;
- fixed-objective recommender;
- phone recommender;
- CARBON-only UI feature;
- copied per-worker prompt logic;
- certainty theater;
- long branching menus;
- endless research loop;
- restart-on-error engine;
- standalone native app as V1 prerequisite;
- provider-locked architecture.

## 27. GOVERNANCE MEASUREMENT CONTRACT

Governance should compare the implementation outcome against:
- this commissioning contract;
- the 35 mandatory gates;
- acceptance vectors;
- originating intention receipt;
- deployed-runtime receipts.

Required T10 commissioning test:

T10_JOB — Build CARBON° Search as the commissioned shared Engine of Intent without semantic drift.
T10_ACTUAL — What was actually implemented/deployed.
T10_EVIDENCE — Exact commits, tests, runtime endpoints, configs and receipts.
T10_CHANGE — Material implementation differences from the commissioned contract.
T10_REMAINING_GAP — Failed/unproven gates or semantic gaps.
T10_PASS — PASS only when all 35 gates and deployed readback pass for the same version/config.

A builder claim does not outrank T10 evidence.

## 28. READINESS DECISION

The originating instance has completed the pre-build conceptual/hardening sweep.

Current judgment:

PRODUCT SEMANTICS: STABLE ENOUGH TO BUILD.
ARCHITECTURE: DEFINED ENOUGH TO BUILD.
SURFACE STRATEGY: DEFINED ENOUGH TO BUILD.
FUTURE EXTENSIBILITY: PRESERVED.
ASSUMPTION/INTENTION BOUNDARY: HARDENED.
CORRECTION/CONTINUITY: HARDENED.
GOVERNANCE ACCEPTANCE TARGET: 35/35 FROZEN FOR FIRST CYCLE.
BUILD STATUS: READY_TO_BUILD.

No further pre-build ideation is required.

Implementation evidence is now the correct source of the next refinements.

BUILD INTENTION.
