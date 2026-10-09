## 0. ORIGINATING INTENTION MUST BE READ FIRST

Before interpreting architecture or writing implementation code, read:

`house/search/CARBON_SEARCH_ORIGINATING_INTENTION_RECEIPT_V1.md`

This receipt transfers the first working interpretation of **INTENTION** from the originating concept-development instance.

The builder must inherit both:
- the formal specification; and
- the intended product behavior that produced it.

Do not reconstruct product meaning from module names alone.

---

# CARBON° SEARCH — BUILD HANDOFF V1

Date: 2026-10-09  
Status: OWNER-AUTHORIZED / BUILD READY  
Implementation owner: existing T-COD/build ownership  
Tracking issue: #16

## 1. Authoritative sources

Current default-branch files govern:

- `house/search/CARBON_SEARCH_BUILD_INITIATIVE_V1.md`
- `house/search/CARBON_SEARCH_ACCEPTANCE_V1.json`
- `house/search/CARBON_SEARCH_ACCEPTANCE_VECTORS_V1.md`
- `house/search/CARBON_SEARCH_ORIGINATING_INTENTION_RECEIPT_V1.md`
- GitHub issue #16

Current authoritative commits at handoff:

- Build initiative: `71578bd74de2dd6b2ec56ed7f4d8e4c665114a22`
- Acceptance contract: `262cf5c72b72f57c04fc272dc75fb1a2cb4e4ca5`

Historical hashes are provenance only. They do not override later Owner-accepted corrections.

## 2. Build state

CARBON° base build remains complete.

This initiative is an additive extension.

The build target is:

**CARBON° Search**  
**INTELLAGENT**  
**Engine of Intent**

Core capability:

**INTENTION = continuous evidence-bound orientation toward the best defensible resolution of Measured Intent.**

## 3. Build law

**WE DO NOT BUILD 49/50. WE BUILD 100/100 — OR WE DO NOT BUILD.**

Current Matrix-grade gate count:

**35 / 35 mandatory gates**

No weighted-average promotion.
No partial-pass promotion.
No UI-demo substitution.
No fabricated certainty.

An individual search may correctly return UNKNOWN / HOLD / INSUFFICIENT EVIDENCE.

## 4. Gate freeze

The 35-gate contract is frozen for the first implementation cycle.

Do not add or remove gates merely because implementation discovers a different way to satisfy them.

A new mandatory gate may be proposed only when implementation evidence exposes a genuinely missing invariant that cannot be represented by the existing 35 gates.

Such a change must be routed through existing Intake/governance before it changes the build target.

This freeze exists to prevent the implementation target from moving while the builder is executing.

## 5. Non-negotiable architecture

One authoritative, versioned Engine of Intent.

Preferred shape:

`HUMAN / PUBLIC / MATRIX WORKER / CLIENT SURFACE`
→ `THIN CALLER ADAPTER`
→ `CARBON° SEARCH`
→ `INTELLAGENT`
→ `AUTHORIZED SCOPES + EVIDENCE`
→ `DECISION`
→ `ACTION`

Do not copy or fork the engine into individual worker prompts.

Surface-specific differences may include context, scope, permission, available actions and disclosure.

Core Search semantics remain common.

## 6. Measured Intent

Measured Intent is the portion of user intent CARBON° can defensibly infer, weight, test and support with evidence.

Keep separate:
- explicit intent;
- Measured Intent;
- latent-intent hypotheses;
- unknown intent.

Unknown or hypothesized intent must never silently become fact.

## 7. Dynamic Intention

At each material state change, update the intent model.

Priority is informed by:

`probability × intent utility × decision sensitivity × cost of being wrong`

Expected Regret remains the stop governor.

Do not discard a lower-probability hypothesis when resolving it could materially change the outcome.

## 8. Active correction

**ACTIVE ERROR != END SEARCH**

**CORRECTION != RESTART EVERYTHING**

**ROLLBACK AFFECTED STATE → REWEIGHT → CONTINUE**

When a wrong claim, entity, alias, interpretation, score, stale source or conflation is discovered:

1. identify affected state;
2. mark affected derived state invalid/superseded;
3. preserve unaffected valid evidence;
4. update Measured Intent and hypotheses;
5. rerun only affected normalization/ranking/regret;
6. continue from the furthest valid evidenced state.

## 9. Canonical directory discipline

Search must distinguish products, services, capabilities, utilities, marketplace offers, evidence records, client assets, workers and other canonical entities.

**SIMILAR LANGUAGE != SAME OFFERING**

**ALIAS != IDENTITY UNLESS MAPPED**

**SEARCH MATCH != AUTHORITY TO MERGE**

The directory/ontology is a build output unless a reusable authoritative component is actually evidenced.

## 10. Decisive primary result + intent pivots

Search should resolve first, not interrogate first.

When a defensible leading interpretation exists:

**return the strongest primary result.**

Where one or two materially supported parallel outcomes remain plausibly useful:

**expose at most two alternate Intent Pivots by default.**

Interaction:

`CONFIDENT PRIMARY RESOLUTION → OPTIONAL 1–2 INTENT PIVOTS → SAME-SESSION CONTINUATION`

A selected pivot:
- preserves valid evidence;
- records the pivot;
- updates Measured Intent/hypothesis weights;
- invalidates only obsolete dependent state;
- continues from the furthest valid state.

## 11. Birth-state dependency correction

The following are BUILD OUTPUTS TO CREATE, not historical prerequisites to discover:

- Marketplace-of-Intent contract/schema/interface;
- provider-neutral INTELLAGENT router contract;
- external retrieval adapter contract;
- ACL/scope model;
- deployment configuration contract;
- Matrix-wide invocation contract;
- canonical directory/ontology contract.

**REQUIRED AT RUNTIME != REQUIRED TO PRE-EXIST THE BUILD**

**NON-EXISTENCE OF A PREVIOUS ARTIFACT != BLOCKER**

A real HOLD requires a specifically identified external dependency after the build has defined what is actually needed.

## 12. Provider law

**MODEL != MATRIX**

**PROVIDER != MANDATE**

Provider failure must not silently downgrade CARBON° Search into keyword search while retaining the same product claim.

## 13. Existing foundation

Reuse the existing CARBON° substrate where lawful and useful:

- FastAPI
- Pydantic
- SQLite/FTS5 EvidenceStore
- deterministic evidence retrieval
- provenance/versioning
- T10 truth boundaries
- House interface
- pytest
- Docker/runtime substrate

Use:

**REUSE → CONFIGURE → EXTEND → BUILD NEW**

## 14. First implementation order

1. Recover authoritative files and verify baseline.
2. Map reusable CARBON substrate.
3. Implement typed session/intent contracts.
4. Implement canonical directory/identity layer.
5. Implement Measured Intent + latent hypotheses.
6. Implement claim/provenance/contradiction layer.
7. Implement correction/rollback.
8. Implement EIF / Expected Regret / decision stability.
9. Implement permission-aware scopes.
10. Implement provider-neutral interpretation/retrieval adapters.
11. Implement Marketplace-of-Intent contract.
12. Implement shared Matrix invocation surface.
13. Implement action/audit/learning/version contracts.
14. Execute acceptance vectors.
15. Execute all 35 mandatory gates.
16. Deploy through existing authorized deployment path.
17. Read back deployed build/config.
18. Run the same 35-gate contract against deployed runtime.

## 15. Change-control rule

Implementation may discover better internal designs.

That does not authorize changing Owner intent.

If a design change preserves all governing semantics, implement it and evidence it.

If a change would alter:
- product meaning;
- Measured Intent semantics;
- Matrix-wide capability behavior;
- privacy/ACL boundaries;
- 35-gate acceptance meaning;
- correction/rollback law;
- Intent Pivot behavior;
- Marketplace relationship;
- authority/governance;

route it before changing the governing contract.

## 16. Completion

Only:

**35/35 PASS + deployed runtime readback against the same build/config**

permits:

`MATRIX_GRADE`

Anything else remains BUILDING / HOLD / NOT_MATRIX_GRADE.


## 10A. Intention is not assumption

**INTENTION follows signals. ASSUMPTION invents preference.**

A plausible preference hypothesis may improve retrieval, but it must remain a hypothesis until supported.

Defensible:
> "This is probably the phone you were looking for."

Not defensible without supporting signal:
> "You probably wanted more physical RAM for your money."

Allowed alternate pivots:
- "Want more physical RAM?"
- "Want the best phone for the same money?"

**SIGNAL → MEASURED INTENT**
**NO SIGNAL → HYPOTHESIS, NOT INTENTION**

Do not confuse a useful search hypothesis with evidence about the user's preference.
