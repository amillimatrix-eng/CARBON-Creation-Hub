# CARBON° SEARCH — BUILD INITIATIVE V1

Date: 2026-10-09
Owner authorization: ACTIVE BUILD INITIATIVE
Primary product: CARBON° Search
Intelligence identity: INTELLAGENT
Positioning: Engine of Intent
Implementation home: CARBON° / AMilliMATRiX
Governance state: Owner-authorized build initiative. Blue State protocol language remains subject to existing Intake/reconciliation. This artifact does not silently declare a new governance layer.

## 0. BUILD LAW

**WE DO NOT BUILD 49/50. WE BUILD 100/100 — OR WE DO NOT BUILD.**

This law governs build acceptance, not the claim that every real-world search can reach 100% certainty.

CARBON° Search must never fake certainty to satisfy the build gate. A Matrix-grade engine must be capable of returning **UNKNOWN / HOLD / INSUFFICIENT EVIDENCE** when the world cannot support a defensible resolution.

**BUILD INTENT.**

Do not build:
- a Google clone;
- a filter panel with an LLM summary;
- a generic chatbot over search results;
- a relevance-ranked link dump;
- a product recommender that assumes the user's objective;
- a provider-dependent feature that silently degrades when one model/search API fails.

## 1. PRODUCT DEFINITION

CARBON° Search is an intent-resolution engine.

It accepts incomplete, ambiguous, partially articulated or evolving user signals and attempts to identify the outcome the user would most probably regard as satisfying **if the user knew enough to ask for it precisely**.

The engine must:
1. observe the expressed query and available lawful context;
2. construct multiple plausible latent-intent hypotheses where intent is uncertain;
3. identify explicit constraints, implied variables, hidden variables, trade-offs and failure costs;
4. retrieve evidence from appropriate scopes;
5. normalize claims before ranking;
6. preserve contradictions rather than selecting convenient facts;
7. update intent hypotheses as evidence changes the meaning of the query;
8. rank candidate outcomes against the probability-weighted intent model;
9. continue searching while material expected regret remains;
10. stop when additional search is unlikely to change the outcome materially;
11. return a compressed decision with provenance, uncertainty and an executable next action;
12. learn from outcome feedback without rewriting historical evidence.

## 2. PRODUCT / MARKET RELATIONSHIP

**CARBON° Marketplace = Market of Intent.**
**CARBON° Search / INTELLAGENT = Engine of Intent.**

Marketplace captures, exposes and accumulates demand/availability signals.
Search interprets and resolves them.

Loop:

`INTENT SIGNAL → INTERPRET → SEARCH → EVIDENCE → WEIGHT → MATCH → ACTION → OUTCOME → LEARNING → MARKET SIGNAL`

A repeated unresolved search is not discarded. It can become evidence of:
- unmet demand;
- inventory gap;
- capability gap;
- evidence gap;
- pricing/positioning gap;
- bad weighting;
- bad intent interpretation.

No such signal may automatically create supply or authority. Existing Intake/governance remains authoritative.

## 3. CORE METRICS

### 3.1 Intent Hypothesis Posterior

For plausible latent intents `I_i` given observed signals `S` and accumulated evidence `E`:

`P(I_i | S,E)`

The engine must preserve more than one hypothesis when evidence does not justify collapse to one interpretation.

### 3.2 Expected Intent Fulfilment — EIF

For candidate outcome `x`:

`EIF(x) = Σ_i P(I_i | S,E) × U(x, I_i)`

Where `U(x,I_i)` is normalized expected utility/alignment of candidate `x` to intent hypothesis `I_i`.

EIF is the primary outcome-alignment metric.

It is **not** a claim that Carbon knows the human mind. It is a probability-weighted estimate from observable and inferable evidence.

### 3.3 Expected Regret — ER

`ER(x*) = E[U(best discoverable outcome, I) - U(x*, I)]`

ER governs search continuation.

Search continues when an unresolved variable, contradiction, missing candidate or plausible hidden intent has enough decision sensitivity that resolving it could materially change the recommendation.

### 3.4 Intent Delta — ΔI

`ΔI = 1 - EIF(x*)`

Intent Delta is a diagnostic distance-to-resolution measure, not by itself the stop rule.

### 3.5 Evidence Coverage

For each material intent dimension, record:
- resolved;
- partially resolved;
- unresolved;
- contradictory;
- unavailable;
- stale.

Evidence coverage must remain distinct from intent confidence.

### 3.6 Decision Stability

A result is decision-stable only when plausible resolution of remaining uncertainties is unlikely to change:
- the winning outcome;
- material ranking;
- confidence class;
- recommended action.

## 4. INTENT MODEL

Every search session must produce a typed Intent Model containing at least:

- raw_query
- normalized_goal
- explicit_constraints
- negative_constraints
- candidate_intent_hypotheses[]
- hypothesis_probabilities[]
- intent_dimensions[]
- dimension_weights[]
- hidden_variable_candidates[]
- action_target
- scope_permissions
- unresolved_questions[]
- confidence
- provenance

Weights are evidence-backed hypotheses, not arbitrary decoration.

Signals that may influence weighting include:
- explicit wording;
- repeated terms;
- unusual specificity;
- corrections;
- rejection of prior results;
- comparative language;
- price/time/risk constraints;
- context explicitly available to the session;
- anomalies discovered during retrieval;
- cost of being wrong.

## 5. SEARCH EXECUTION PIPELINE

`QUERY`
→ `INTENT HYPOTHESES`
→ `MATERIAL VARIABLES`
→ `SCOPE ROUTING`
→ `RETRIEVAL`
→ `CLAIM NORMALIZATION`
→ `PROVENANCE`
→ `CONTRADICTION CHECK`
→ `HIDDEN-VARIABLE TEST`
→ `WEIGHTED CANDIDATE SCORING`
→ `EIF`
→ `EXPECTED REGRET / DECISION-SENSITIVITY TEST`
→ `CONTINUE OR STOP`
→ `RESULT COMPRESSION`
→ `ACTION ROUTING`
→ `OUTCOME FEEDBACK`

A correction or newly discovered fact must update the intent model and continue from the furthest evidenced state. It must not restart the search unless the prior state is invalidated.

## 6. SCOPE ROUTER

The engine must support isolated, permission-aware scopes:

1. CARBON INTERNAL
2. CARBON MARKETPLACE
3. CLIENT SPACE
4. MATRIX INTERNAL / authorized knowledge
5. EXTERNAL WEB
6. CONNECTED DATA / provider adapters

A source may participate only when the current search has permission to use it.

Private client/internal evidence must never leak into public result surfaces merely because it improves ranking.

## 7. EVIDENCE / CLAIM CONTRACT

Raw retrieved text is not a ranked fact.

Claims must be normalized into a provenance-aware structure containing at least:
- claim_id
- entity
- attribute
- value
- units
- source
- source_type
- source_timestamp
- retrieved_at
- freshness_class
- authority_class
- confidence
- contradiction_group
- visibility
- evidence_pointer

**TRUE A + TRUE B != TRUE A→B** unless the relationship is itself evidenced.

No cross-chain synthesis without an evidenced join.

## 8. CONTRADICTION BEHAVIOR

When credible sources disagree:
1. preserve both claims;
2. determine whether they refer to the same entity/SKU/version/time;
3. test source authority and freshness;
4. resolve only where evidence supports resolution;
5. otherwise expose the contradiction and lower confidence;
6. never average incompatible facts into a fictional midpoint.

## 9. HIDDEN-VARIABLE DETECTION

CARBON° Search must actively test variables whose discovery could materially change the outcome even when the user did not explicitly request them.

Example:
- "12GB RAM" may require physical-vs-virtual RAM decomposition.
- "fast laptop" may require thermal sustainability, soldered RAM or upgradeability.
- "available now" requires current stock, not catalogue presence.
- "paid" requires settlement evidence, not invoice state.

Hidden-variable generation is governed by decision sensitivity, not by unlimited curiosity.

## 10. STOP RULE

CARBON° Search stops only when all are true:

1. the dominant plausible intent space is represented;
2. material constraints are evaluated;
3. material contradictions are resolved or explicitly bounded;
4. the current best result has sufficient evidence;
5. remaining uncertainty is unlikely to change the material outcome;
6. expected regret is below the configured acceptance threshold;
7. no mandatory high-sensitivity variable remains unresolved;
8. an executable action exists, or the truthful action is HOLD / obtain missing evidence.

Search depth is therefore dynamic.

More pages searched does not equal better search.

## 11. DEFAULT RESULT CONTRACT

Default user output must be compressed.

Return, where applicable:
- BEST MATCH
- BEST MATERIAL ALTERNATIVE
- VALUE / SPECIALIST OPTION
- DECISIVE FACTOR
- HIDDEN FACTOR
- CONFIDENCE / MATERIAL GAP
- ACTION

Do not expose internal reasoning traces.
Do preserve inspectable evidence/provenance behind the result.

## 12. ACTION CONTRACT

A successful result should terminate in capability where authorized:

- OPEN
- BUY
- RESERVE
- COMPARE
- CONTACT
- BUILD
- REQUEST
- ROUTE
- HANDOFF
- HOLD / GET EVIDENCE

Search must not perform actions outside existing authority.

## 13. LEARNING CONTRACT

Outcome feedback may update:
- intent priors;
- feature/dimension weights;
- ranking calibration;
- source reliability;
- hidden-variable discovery;
- stop thresholds.

It must not:
- rewrite historical queries;
- overwrite evidence;
- convert preference into governance;
- treat one user's outcome as universal truth.

All learned weighting must be versioned and reversible.

## 14. IMPLEMENTATION ARCHITECTURE

Extend the existing CARBON Evidence House backend rather than rebuilding it.

Proposed modules:

`backend/intent/models.py`
Typed IntentModel, IntentHypothesis, IntentDimension, SearchSession, CandidateOutcome, Claim, ResultDecision.

`backend/intent/interpreter.py`
Provider-neutral intent interpretation interface.

`backend/intent/providers/`
Pluggable model/provider implementations. No single provider becomes Matrix authority.

`backend/intent/scopes.py`
Permission-aware scope router.

`backend/intent/retrieval.py`
Adapter protocol for Evidence House, Marketplace, web and connected sources.

`backend/intent/claims.py`
Claim normalization, entity/version alignment and provenance.

`backend/intent/contradictions.py`
Contradiction grouping/resolution state.

`backend/intent/ranker.py`
Weighted candidate utility + EIF.

`backend/intent/regret.py`
Expected-regret / decision-sensitivity controller.

`backend/intent/session.py`
Iterative search loop and search-state persistence.

`backend/intent/actions.py`
Existing-authority action routing.

`backend/intent/learning.py`
Versioned outcome feedback and calibration.

`backend/intent/audit.py`
Search receipt, source ledger, metric snapshots, decision state and stop reason.

API surface:

- POST `/api/search/intent`
- GET `/api/search/sessions/{session_id}`
- GET `/api/search/sessions/{session_id}/evidence`
- POST `/api/search/sessions/{session_id}/feedback`
- POST `/api/search/sessions/{session_id}/action` (authorized actions only)

The existing `/api/evidence/search` remains deterministic evidence retrieval. It is not silently renamed into CARBON° Search.

## 15. PROVIDER FAILURE LAW

MODEL != MATRIX.
PROVIDER != MANDATE.

If the configured intent provider is unavailable:
- do not silently switch to keyword-only behavior and call it CARBON° Search;
- expose INTENT_ENGINE_UNAVAILABLE / DEGRADED;
- preserve the query/session;
- use another authorized compatible provider only if the provider router authorizes it;
- otherwise HOLD.

The same rule applies to external search providers.

## 16. BUILD ACCEPTANCE — 100/100 ONLY

Promotion to MATRIX_GRADE requires **every mandatory gate** in `CARBON_SEARCH_ACCEPTANCE_V1.json` to PASS.

No weighted average may hide a failed mandatory gate.

No "49/50", "mostly passed", "minor residual", or visual-demo success may be promoted to MATRIX_GRADE.

If one mandatory gate fails:

`BUILD_STATE = HOLD / NOT MATRIX_GRADE`

## 17. REFERENCE ACCEPTANCE SCENARIO — PHONE SEARCH

Input evidence:
- retailer remembered imperfectly;
- ZTE handset;
- approximately R1,200;
- advertised 12GB RAM;
- user has not explicitly stated why RAM matters.

Required behavior:
1. identify probable device;
2. detect 12GB at that price as anomalous;
3. test physical vs virtual RAM;
4. discover 4+8 split;
5. update intent posterior toward high physical-RAM/value expectation;
6. search nearby options that could better satisfy that latent expectation;
7. rank alternatives by expected intent fulfilment, not headline RAM;
8. expose current orderability/stock evidence when relevant;
9. stop only when unresolved variables are unlikely to change the decision materially.

Fail examples:
- return the identified ZTE and stop;
- compare "12GB" vs "8GB" without normalizing physical/virtual RAM;
- ask the user to manually define every filter before searching;
- invent that RAM is definitely the only objective;
- bury the decision under a forensic report.

## 18. FIRST BUILD SLICE

The first executable slice must prove the architecture end-to-end on:
1. external product decision search;
2. internal CARBON evidence search;
3. one Marketplace-of-Intent query once the authoritative Marketplace contract/location is supplied.

No production claim until all mandatory acceptance gates pass across all required scenarios.

## 19. BUILD INPUTS VS BUILD OUTPUTS

Known available build foundation:
- writable `amillimatrix-eng/CARBON-Creation-Hub`;
- FastAPI;
- Pydantic;
- SQLite/FTS5 evidence store;
- evidence provenance/versioning;
- T10 truth boundaries;
- House public interface;
- current test framework.

The following are **NOT pre-existing dependencies** and must not be treated as blockers or evidence gaps merely because no prior artifact exists.

They are part of this new initiative and are therefore **BUILD OUTPUTS / DESIGN CONTRACTS TO CREATE**:

- Marketplace-of-Intent contract/schema/interface;
- INTELLAGENT runtime intent-provider/router contract;
- external-search/retrieval adapter contract;
- scope/ACL model for private Matrix/client sources;
- deployment configuration contract for whichever authorized providers are selected.

The only authoritative source for these concepts at initiative birth is:
1. this Owner-authorized conversation;
2. the durable CARBON° Search build initiative;
3. the corresponding ROOT Intake record.

Therefore:

**NON-EXISTENCE OF A PREVIOUS ARTIFACT != BLOCKER.**

The builder must derive these components from the locked intent architecture, implement them, test them, and then make them authoritative through the normal evidence/build process.

A HOLD is appropriate only when a real external dependency is required for execution and is unavailable after the build has defined exactly what is needed.

## 20. TERMINAL DEFINITION

CARBON° Search is complete only when it can repeatedly:

`OBSERVE INTENT → MODEL UNCERTAINTY → SEARCH → NORMALIZE → WEIGH → TEST REGRET → RESOLVE → ACT`

with provenance, permission boundaries, contradiction discipline, honest uncertainty and 100/100 mandatory build acceptance.

Anything less is not CARBON° Search.


## 21. ACCEPTED METRIC LAYER — MEASURED INTENT

**Owner disposition: ACCEPTED — 2026-10-09**

**Measured Intent** is the portion of user intent that CARBON° can defensibly infer, weight, test and support with evidence.

It is the formal boundary between:
- what the user explicitly stated;
- what the engine can defensibly infer from observed signals and evidence;
- what remains latent, uncertain or unknown.

Measured Intent must never be presented as perfect knowledge of the user's true internal intent.

The governing flow is:

`OBSERVED SIGNALS → MEASURED INTENT → LATENT INTENT HYPOTHESES → EVIDENCE → EXPECTED INTENT FULFILMENT → EXPECTED REGRET → RESOLUTION → ACTION`

The engine objective is:

**MAXIMIZE MEASURED INTENT RESOLUTION WHILE MINIMIZING MATERIAL EXPECTED REGRET.**

This metric layer does not replace latent-intent hypotheses, EIF or Expected Regret. It anchors them.

- **Measured Intent** defines what CARBON° can currently defend.
- **Latent Intent Hypotheses** represent plausible unresolved intent beyond the directly measured layer.
- **EIF** estimates how well candidate outcomes satisfy the probability-weighted intent model.
- **Expected Regret** governs whether additional search is materially worth continuing.

If an intent component cannot be defensibly measured, it remains **UNKNOWN / HYPOTHESIZED** and may influence exploration only with explicit uncertainty. It may not be silently promoted to a fact or hard constraint.

This section is part of the locked build initiative and must not be diluted into conventional filter matching or generic relevance scoring.


## 22. MATRIX-WIDE CAPABILITY CONTRACT — OWNER ACCEPTED SCOPE

CARBON° Search is a **CARBON° product** and a **Matrix-wide callable capability**.

The implementation must not trap the Engine of Intent inside one Carbon UI, one model prompt, one worker, or one provider.

The preferred architecture is:

`MATRIX WORKER / MODEL / PRODUCT → THIN SEARCH ADAPTER → CARBON° SEARCH CAPABILITY → INTELLAGENT → AUTHORIZED SCOPES / EVIDENCE / MARKETPLACE → DECISION + ACTION`

### 22.1 Single-engine rule

Do **not** duplicate the intent engine into every worker prompt or maintain multiple worker-specific forks of the search logic.

Use one authoritative, versioned engine with thin integration surfaces.

A worker may carry local invocation guidance, but the underlying interpretation, evidence normalization, contradiction discipline, EIF, Expected Regret, audit behavior and search-state semantics must come from the shared CARBON° Search capability.

### 22.2 Required callable surface

The Matrix-wide integration contract must allow an authorized caller to provide at least:
- raw query / task;
- caller identity / capability identity;
- objective context that the caller is authorized to disclose;
- requested search scopes;
- permission / visibility context;
- desired action type where known;
- freshness / latency / cost sensitivity where material;
- optional prior search-session reference for continuation.

The shared result contract must return at least:
- measured-intent snapshot;
- explicit constraints;
- materially plausible latent-intent hypotheses;
- decision-grade result / alternatives;
- decisive and hidden variables;
- evidence / provenance pointers;
- contradiction state;
- confidence / unresolved material gap;
- stop reason / Expected Regret state;
- authorized next action or truthful HOLD;
- capability / contract version;
- session / audit reference.

### 22.3 Permission and authority boundary

A Matrix-wide caller does not inherit broader evidence access merely by calling CARBON° Search.

The Search capability must enforce scope and visibility at the service boundary.

`CALLER AUTHORITY != SEARCH AUTHORITY EXPANSION`

Private Matrix/client evidence may participate only when the caller and requested action are authorized for that scope.

### 22.4 Distribution rule

CARBON° Search should be integrable through the smallest common interface available to the Matrix, such as:
- a versioned internal API/service contract;
- a shared tool/capability adapter;
- a provider-neutral invocation library;
- a future registry entry if/when the Matrix has an authoritative capability registry.

The build must not assume a registry already exists.

### 22.5 Upgrade rule

Matrix integrations should reference a compatible capability contract/version rather than embed copied engine logic.

An engine upgrade should therefore improve all compatible callers without requiring independent reimplementation in every worker.

Breaking contract changes require explicit versioning and compatibility handling.

### 22.6 Invocation policy

The capability is available Matrix-wide where search, discovery, evidence resolution, comparison, hidden-variable detection or decision support materially benefits the caller.

It should not replace simpler deterministic retrieval where no intent-resolution work is needed.

The objective is **best useful deployment**, not forcing expensive intent inference into every lookup.

### 22.7 Product identity

Matrix-wide use does not strip product ownership or identity.

- **CARBON° Search** remains the product.
- **INTELLAGENT** remains the intent intelligence layer.
- **Engine of Intent** remains the positioning.
- Matrix workers consume the capability; they do not each become separate CARBON° Search implementations.


## 23. INTENTION CONTINUITY — SURFACE PARITY, DIRECTORY DISCIPLINE AND ACTIVE SELF-CORRECTION

The core capability being built is **INTENTION**: CARBON° Search must continuously orient search execution toward the most defensible, highest-probability resolution of Measured Intent while preserving uncertainty honestly.

This applies whether the caller is:
- the Owner or another human using CARBON° Search directly;
- a Matrix worker/model invoking Search while performing another job;
- a CARBON° product surface;
- the public CARBON° Search surface;
- an authorized client/private surface.

The **core intent engine is the same**. What changes by surface is lawful context, scope, permissions, available actions and disclosure—not the meaning of Search.

### 23.1 Surface parity

Public, Matrix, Owner and client searches must share the same core rules:
- Measured Intent boundary;
- latent-intent plurality;
- evidence normalization;
- provenance;
- contradiction preservation;
- hidden-variable detection;
- EIF;
- Expected Regret;
- decision stability;
- active correction;
- truthful HOLD.

No surface may replace CARBON° Search with a materially weaker keyword/relevance engine while presenting it as the same capability.

### 23.2 Canonical offer / directory discipline

CARBON° and the Matrix may expose many different products, services, capabilities, utilities, assets, marketplace entries and evidence records.

Search must not conflate them merely because names, language, tags or use-cases overlap.

The build must create a canonical searchable directory / ontology contract containing, at minimum:
- canonical entity_id;
- canonical name;
- entity_type;
- parent / domain;
- aliases;
- description / purpose;
- capabilities;
- offered actions;
- visibility / scope;
- lifecycle state;
- source of authority;
- version;
- supersession / rename links;
- evidence pointer.

Entity types must remain distinguishable (for example: PRODUCT, SERVICE, CAPABILITY, UTILITY, MARKETPLACE_OFFER, EVIDENCE_RECORD, CLIENT_ASSET, INTERNAL_WORKER) unless an evidenced relationship explicitly connects them.

**SIMILAR LANGUAGE != SAME OFFERING.**
**ALIAS != IDENTITY UNLESS MAPPED.**
**SEARCH MATCH != AUTHORITY TO MERGE.**

Where directories or names conflict, preserve the conflict and resolve identity before ranking across the conflated candidates.

### 23.3 Active-search mistake recovery

A mistake discovered during active search is a recoverable state transition, not automatically a terminal state.

Examples:
- wrong entity selected;
- incorrect attribute parsed;
- stale source outranked a current source;
- alias mapped to the wrong canonical item;
- two offerings were conflated;
- a hidden variable invalidates an earlier ranking;
- a user correction changes the meaning of earlier evidence;
- the engine itself detects that an earlier assumption was unsupported.

Required behavior:

1. identify the exact invalid claim, mapping, hypothesis, score or branch;
2. mark the affected state invalid / superseded rather than silently overwriting it;
3. roll back only the dependent derived state;
4. preserve unaffected valid evidence and work;
5. update Measured Intent and latent-intent probabilities;
6. re-run affected normalization / ranking / regret checks;
7. continue from the furthest valid evidenced state;
8. expose the corrected result only after decision stability is restored.

**ACTIVE ERROR != END SEARCH.**
**CORRECTION != RESTART EVERYTHING.**
**ROLLBACK AFFECTED STATE → REWEIGHT → CONTINUE.**

Search may terminate only when the normal stop rule is satisfied or when the truthful terminal action is HOLD / GET EVIDENCE.

### 23.4 Dynamic intent focus

At every material state change, CARBON° Search must update its intent model.

The engine should dynamically focus execution on the currently highest-supported probability-weighted path to Measured Intent resolution, while retaining materially plausible alternatives until evidence justifies pruning them.

This does not mean blindly selecting the single highest-probability hypothesis at all times. A lower-probability hypothesis with high decision sensitivity or high cost-of-error may still require testing because resolving it could change the final outcome materially.

Therefore priority is governed by:

`PROBABILITY × INTENT UTILITY × DECISION SENSITIVITY × COST OF BEING WRONG`

subject to evidence, permissions and Expected Regret.

### 23.5 Search-session continuity

Every active session must preserve enough state to recover deterministically from correction:
- intent-model version;
- Measured Intent snapshot;
- hypothesis set + weights;
- canonical entities considered;
- normalized claims;
- claim validity/supersession state;
- evidence pointers;
- ranking snapshot;
- contradictions;
- stop / continue decision;
- correction events;
- rollback boundary;
- current furthest valid state.

The audit record must show what changed without exposing private chain-of-thought.

### 23.6 Intention acceptance principle

The target capability is not merely "good search."

A valid CARBON° Search implementation must demonstrate:

`SIGNAL → MEASURE INTENT → FORM HYPOTHESES → SEARCH → DETECT ERROR/NEW EVIDENCE → CORRECT → REWEIGHT → CONTINUE → STABILIZE → ACT`

without conflating offerings, discarding valid work, or ending the search because its own intermediate interpretation was wrong.

**INTENTION is continuous evidence-bound orientation toward the best defensible outcome.**


## 24. INTENT BRANCH AFFORDANCES — RESOLVE FIRST, THEN OFFER BOUNDED ALTERNATIVES

CARBON° Search should not default to interrogating the user before returning a result.

The engine should first produce the strongest defensible primary resolution from current Measured Intent, evidence and decision state.

Where one or two materially plausible alternate intent outcomes remain close enough that they could produce an equally or more desirable result, Search may expose **bounded intent branch affordances**.

These may render as buttons, links, chips, or equivalent actions.

Examples:
- **YES — THIS IS WHAT I MEANT**
- **SHOW THE HIGHER-PHYSICAL-RAM PATH**
- **COMPARE THE CHEAPER ALTERNATIVE**
- **I MEANT THE OTHER CARBON° SERVICE**
- **KEEP SEARCHING THIS DIRECTION**

The interaction contract is:

`PRIMARY RESOLUTION → OPTIONAL 1–2 INTENT BRANCHES → CONTINUE SAME SEARCH SESSION`

### 24.1 Primary-result confidence

The default user experience should be decisive.

Do not ask "what did you mean?" merely because several hypotheses exist internally.

Return the current best result when:
- the leading Measured Intent resolution is decision-stable enough to be useful;
- remaining ambiguity does not justify blocking the result;
- the result can be stated with honest confidence and material gaps.

Clarification is a **secondary affordance**, not a prerequisite, unless no defensible primary result exists.

### 24.2 When to expose branches

Expose an alternate intent branch only when it is materially supported by evidence and one or more are true:
- posterior probability is competitive with the leading interpretation;
- expected utility is close enough that the alternate could plausibly be preferred;
- cost of choosing the wrong interpretation is material;
- the alternate resolves an important hidden variable;
- the alternate outcome would change the recommended action materially.

Do not expose low-value speculative branches merely because they are imaginable.

### 24.3 Branch count

Default maximum: **two alternate intent actions** in addition to the primary result.

The purpose is to preserve useful optionality without recreating a filter menu or forcing the user to manage the search manually.

More branches require an evidenced reason.

### 24.4 Same-session continuation

Selecting an intent branch must not start a disconnected search unless technically unavoidable.

The engine must:
1. preserve the existing evidence/session;
2. record which branch was selected;
3. update Measured Intent and hypothesis probabilities;
4. invalidate only state made obsolete by the selected interpretation;
5. preserve still-valid evidence;
6. continue search/ranking from the furthest valid state;
7. return the updated resolution.

### 24.5 Branch semantics

A branch action may:
- confirm the current interpretation;
- bias toward a parallel plausible intent;
- request a materially different trade-off;
- continue deeper on the current path;
- deliberately deviate to a different but evidence-supported outcome.

It must not silently rewrite the original query history.

### 24.6 Confidence without arrogance

The engine should behave as though it understands the user's likely intent well enough to be useful, while preserving explicit uncertainty where it matters.

Therefore:

**CONFIDENT PRIMARY RESULT != CLAIM OF PERFECT INTENT KNOWLEDGE.**

**ALTERNATE BRANCH != ENGINE FAILURE.**

An alternate branch exists because a second outcome may remain materially desirable, not because Search failed to resolve anything.

### 24.7 User-facing principle

The ideal interaction is:

> "Here is what I believe best satisfies what you are trying to achieve."

followed, only where useful, by one or two actions equivalent to:

> "If you meant this nearby outcome instead, take this path."

This preserves decisiveness, user agency, measured uncertainty and search continuity.


## 25. INTENTION VS ASSUMPTION

CARBON° Search must distinguish **signal-supported intent inference** from **unsupported preference assumption**.

The engine may form hypotheses beyond what the user explicitly stated, but those hypotheses remain epistemically typed.

Rules:

1. A claim about what the user probably meant requires supporting signals/evidence.
2. A plausible but unsupported preference remains a latent hypothesis.
3. Latent hypotheses may guide retrieval, hidden-variable testing and alternate Intent Pivots.
4. They may not be surfaced as statements of user preference unless evidence supports that promotion.
5. The primary result should reflect the strongest defensible Measured Intent.
6. Alternate pivots may test nearby preference directions without claiming the user already holds them.

Example:

Defensible:
> "This is probably the phone you were looking for."

Not defensible without more signal:
> "You probably wanted more physical RAM for your money."

Allowed pivot:
> "Want more physical RAM?"

Allowed pivot:
> "Want the best phone for the same money?"

Therefore:

**SIGNAL → MEASURED INTENT**
**NO SIGNAL → HYPOTHESIS, NOT INTENTION**

This distinction prevents CARBON° Search from turning useful inference into fabricated user preference.
