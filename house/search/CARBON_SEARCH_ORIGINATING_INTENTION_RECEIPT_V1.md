# CARBON° SEARCH — ORIGINATING INTENTION RECEIPT V1

Date: 2026-10-09  
Originating interpretation instance: current CARBON° Search concept-development branch  
Status: OWNER-CORRECTED / DURABLE INTENT TRANSFER  
Purpose: preserve the first working interpretation of **INTENTION** so later builders do not reconstruct or dilute it.

## 1. Why this receipt exists

CARBON° Search did not begin as a generic search-engine idea.

It emerged from a real search interaction in which the visible query did not fully express the outcome the Owner actually hoped to achieve.

The originating phone-search case exposed the core product insight:

A search engine should not merely retrieve what was literally asked for.

It should use available signals and evidence to infer, test and continuously refine the **best defensible measured interpretation of what outcome the caller is actually trying to achieve**.

The first implementation branch must therefore inherit the **meaning** of INTENTION, not only its modules and gates.

This document records that meaning.

## 2. Originating insight

The canonical originating scenario was approximately:

- a remembered ZTE phone;
- retailer memory was imperfect;
- price near R1,200;
- advertised "12GB RAM";
- the visible task appeared to be identifying the device / validating the specification.

But the deeper useful outcome was not merely:
> "Which phone was this?"

The search revealed that the advertised 12GB likely represented physical + virtual RAM.

The Owner's actual hoped-for outcome included the possibility that an unusually strong physical-RAM configuration existed near that price.

Therefore a strong search should:
1. identify the likely device;
2. detect that the headline specification is anomalous;
3. normalize the claim;
4. discover the physical/virtual split;
5. recognize that this new evidence changes the meaning of the search;
6. update the Measured Intent model;
7. search for nearby outcomes more likely to satisfy that now-better-understood intent;
8. return the strongest result;
9. optionally expose one or two plausible parallel intent outcomes.

The product was born from that transition.

## 3. INTENTION — originating definition

**INTENTION = continuous evidence-bound orientation toward the best defensible resolution of Measured Intent.**

The word **continuous** is essential.

The engine must not form one interpretation at the start and merely execute it.

It must update its understanding as:
- evidence appears;
- hidden variables surface;
- contradictions emerge;
- user corrections arrive;
- its own intermediate assumptions are disproven;
- alternate outcomes become materially more desirable.

INTENTION is therefore a **runtime behavior**, not a one-time classification step.

## 4. Measured Intent — originating boundary

Measured Intent is not mind-reading.

It is:

**the portion of user intent CARBON° can defensibly infer, weight, test and support with evidence.**

The engine must distinguish:
- what the user explicitly said;
- what can be defensibly measured/inferred;
- what remains a plausible latent hypothesis;
- what is unknown.

Do not collapse these states.

The goal is not perfect certainty.

The goal is the best defensible resolution from the evidence currently available.

## 5. The first-instance behavioral intention

When the engine has enough evidence to produce a useful primary answer, it should do so confidently.

It should **not** default to interrogating the caller with repeated clarification questions.

Where a materially plausible nearby interpretation could produce an equally or more desirable outcome, the engine may expose one or two bounded **Intent Pivots**.

The intended interaction is:

`CONFIDENT PRIMARY RESOLUTION → OPTIONAL 1–2 INTENT PIVOTS → SAME-SESSION CONTINUATION`

The primary result is the engine saying, in effect:

> "This is what I currently believe best satisfies what you are trying to achieve."

The pivot says, in effect:

> "If this nearby interpretation is actually closer to what you wanted, continue this way."

A pivot is not evidence that Search failed.

It is controlled optionality around a strong primary resolution.

## 6. Correction is part of INTENTION

A major Owner correction during concept development established this law:

**ACTIVE ERROR != END SEARCH**

**CORRECTION != RESTART EVERYTHING**

**ROLLBACK AFFECTED STATE → REWEIGHT → CONTINUE**

The originating instance itself made a material planning mistake by treating future Search architecture outputs as though they were pre-existing dependencies that had to be discovered.

The Owner corrected that error.

The correct behavior was:
- identify the wrong classification;
- preserve valid surrounding work;
- reclassify affected state;
- continue from the furthest valid state.

CARBON° Search must behave the same way internally.

An engine that stops because it discovers its own intermediate mistake is not implementing INTENTION.

## 7. Identity / directory intention

CARBON° and the Matrix contain many distinct:
- products;
- services;
- capabilities;
- utilities;
- marketplace offers;
- evidence records;
- workers;
- client assets.

Search must understand those distinctions.

Semantic similarity is not enough to merge them.

The Owner explicitly wants the system to avoid dilution and conflation when people search across a broad business offering.

Therefore:

**SIMILAR LANGUAGE != SAME OFFERING**

**ALIAS != IDENTITY UNLESS MAPPED**

**SEARCH MATCH != AUTHORITY TO MERGE**

The directory/ontology exists to preserve the truth of what each thing actually is.

## 8. Matrix-wide intention

CARBON° Search is a CARBON° product.

But if the capability works correctly, the same engine should materially improve the Matrix's own work.

The intended distribution is one versioned engine callable by:
- the Owner/human user;
- public users;
- Matrix workers/models;
- authorized client/private surfaces.

Do not copy the intelligence into each caller.

Use thin adapters into one authoritative engine.

The same core semantics should therefore improve every compatible caller as the engine improves.

## 9. What must NOT happen

The next branch must not reinterpret INTENTION as:

- generic semantic search;
- LLM summarization over links;
- a filter engine;
- a chatbot that asks the user to define every requirement;
- a recommendation engine with a fixed objective;
- keyword retrieval with nicer prose;
- a product-specific phone recommender;
- a CARBON-only UI feature;
- a set of copied prompts installed into every worker;
- a certainty engine that hides uncertainty;
- a branching menu that gives the user ten possibilities;
- an endless research loop;
- a system that restarts every time a correction occurs.

Those are dilutions.

## 10. What success should feel like

A successful result should feel as though the system understood enough of the caller's intention to be genuinely useful before the caller had to articulate every hidden requirement.

It should still preserve evidence truth.

The experience should be:

1. **It understood what I was probably trying to achieve.**
2. **It found something materially useful.**
3. **It noticed facts I did not know to ask about.**
4. **It corrected itself when the evidence changed.**
5. **It did not confuse different things in the business.**
6. **It gave me a strong answer without making me manage the search.**
7. **It gave me a nearby alternate path only when that path was genuinely plausible.**
8. **I could act on the result.**

## 11. Builder interpretation rule

The next builder must read this receipt before implementation.

If implementation details create ambiguity about product meaning:

1. prefer the current authoritative build spec and acceptance contract;
2. use this receipt to interpret the Owner's intended behavior;
3. preserve the originating phone-search insight;
4. preserve the Owner's later corrections;
5. do not silently reinterpret product semantics for implementation convenience;
6. route genuine semantic conflicts through existing Intake/governance.

Implementation is allowed to improve engineering.

Implementation is not allowed to weaken the intention in order to make the build easier.

## 12. First-instance continuity rule

This receipt captures the first working interpretation of INTENTION.

Later branches may refine implementation, but they should be able to answer:

> "Does this still behave like the capability that was discovered in the originating phone-search conversation?"

If not, the change must be treated as a material semantic change rather than an implementation detail.

## 13. Governing shorthand

Preserve these exact behavioral anchors:

**SEARCH LESS, RESOLVE MORE**

**INTENT → EVIDENCE → WEIGHTING → ACTION**

**ACTIVE ERROR != END SEARCH**

**CORRECTION != RESTART EVERYTHING**

**ROLLBACK AFFECTED STATE → REWEIGHT → CONTINUE**

**CONFIDENT PRIMARY RESOLUTION → OPTIONAL 1–2 INTENT PIVOTS → SAME-SESSION CONTINUATION**

**NON-EXISTENCE OF A PREVIOUS ARTIFACT != BLOCKER**

**MODEL != MATRIX**

**PROVIDER != MANDATE**

**SIMILAR LANGUAGE != SAME OFFERING**

**SEARCH MATCH != AUTHORITY TO MERGE**

And above all:

**BUILD INTENTION.**
