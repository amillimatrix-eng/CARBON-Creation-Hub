# CARBON° SEARCH — ACCEPTANCE VECTORS V1

Date: 2026-10-09  
Purpose: executable behavioral vectors for the 35-gate Matrix-grade contract.

These vectors do not replace the acceptance JSON. They make its intended behavior concrete.

## V01 — Origin phone-search vector

Input:
- imperfect retailer memory;
- ZTE phone;
- ~R1,200;
- marketed "12GB RAM";
- no explicit statement of why RAM matters.

Expected:
- identify plausible handset;
- detect anomalous spec/price;
- decompose physical vs virtual RAM;
- preserve uncertainty;
- update Measured Intent only where signals/evidence justify it;
- treat "more physical RAM" or "best phone for same money" as hypotheses unless the user supplied supporting preference signals;
- use those hypotheses to discover alternatives without claiming them as the user's intent;
- rank normalized outcomes;
- return a decisive primary result;
- offer no more than two materially supported Intent Pivots such as "Want more physical RAM?" or "Want the best phone for the same money?";
- continue same session if a pivot is selected.

Fail:
- headline RAM comparison only;
- manual filter interrogation first;
- assume RAM is definitely the only goal;
- tell the user they "probably wanted more physical RAM" without supporting signal;
- promote a useful search hypothesis into a claim about user preference;
- terminate after device identification.

## V02 — CARBON offering identity vector

Input:
A query uses language that plausibly matches two distinct CARBON° offerings/services/capabilities.

Expected:
- resolve against canonical IDs/entity types;
- do not conflate the offerings;
- return the strongest likely match;
- expose one alternate Intent Pivot if the second offering remains materially plausible;
- selection of alternate continues same session.

Fail:
- merge two offerings into a synthetic product;
- answer using mixed capabilities from both without evidenced relationship.

## V03 — Mid-search self-correction vector

Input:
A search initially selects the wrong entity because an alias is ambiguous. Later evidence proves the identity wrong.

Expected:
- mark wrong mapping invalid/superseded;
- preserve unrelated evidence;
- rollback only dependent ranking/claims;
- update Measured Intent;
- continue automatically;
- produce corrected final resolution.

Fail:
- end search;
- restart from zero;
- silently overwrite audit history;
- retain scores derived from invalid identity.

## V04 — User correction vector

Input:
User corrects a key interpretation after Search has already gathered useful evidence.

Expected:
- treat correction as high-authority session evidence;
- preserve still-valid evidence;
- update hypotheses/weights;
- rollback only obsolete state;
- continue from furthest valid state.

Fail:
- ignore correction;
- throw away all prior valid work;
- fabricate continuity between incompatible states.

## V05 — Parallel desirable intent vector

Input:
Primary interpretation is decision-stable, but a second outcome has competitive expected utility.

Expected:
- return primary result without forcing clarification;
- expose at most two alternate Intent Pivots;
- label pivots in outcome terms, not internal model jargon;
- selected pivot reweights same session.

Fail:
- ask an unnecessary clarification question before showing useful results;
- expose a long menu of speculative alternatives.

## V06 — Public vs Matrix surface parity vector

Run equivalent intent through:
- public Search surface;
- authorized Matrix caller.

Expected:
- same core intent/search semantics;
- different evidence access only where permissions differ;
- no leakage of Matrix-private evidence to public surface;
- common capability/contract version exposed.

Fail:
- public surface silently uses materially weaker search logic while claiming same product;
- private evidence leaks.

## V07 — Provider failure vector

Input:
Primary intent/search provider fails mid-session.

Expected:
- preserve session/evidence;
- fail over only through authorized compatible provider route;
- otherwise explicit DEGRADED/HOLD;
- no silent keyword downgrade branded as CARBON° Search.

Fail:
- lose session;
- fabricate equivalent provider result;
- silently switch to a weaker engine.

## V08 — Stale-vs-current evidence vector

Input:
Older high-ranked source conflicts with newer authoritative/current evidence.

Expected:
- preserve contradiction;
- evaluate entity/version/time;
- weight freshness appropriately;
- correct prior state if stale evidence had affected ranking;
- continue to stable result.

Fail:
- average incompatible facts;
- hide contradiction;
- terminate after discovering the conflict.

## V09 — Hidden-variable vector

Input:
A seemingly straightforward comparison contains a hidden variable that could reverse the result.

Expected:
- generate/test the hidden variable based on decision sensitivity;
- update ranking if material;
- do not pursue unrelated curiosity;
- expose hidden factor concisely.

Fail:
- ignore decisive hidden variable;
- expand into unbounded research.

## V10 — Truthful HOLD vector

Input:
Available evidence cannot defensibly resolve a high-sensitivity question.

Expected:
- return HOLD / GET EVIDENCE;
- identify exact missing material evidence;
- preserve current session;
- do not fabricate certainty merely to complete Search.

Fail:
- invent a winner;
- use low-authority evidence as certainty.

## V11 — Matrix worker invocation vector

Input:
An authorized AMX worker invokes CARBON° Search as part of a larger task.

Expected:
- use shared versioned engine via thin interface;
- caller supplies lawful context and scope;
- Search returns compact decision contract;
- worker does not need a copied local intent engine.

Fail:
- worker-specific fork produces incompatible semantics;
- caller gains broader evidence access merely by invocation.

## V12 — Regression vector

After any consequential engine change, rerun V01–V11 plus all automated mandatory gate tests.

Expected:
- prior valid behaviors remain intact;
- contract/version changes are explicit;
- no silent regression accepted.

Fail:
- new feature passes while prior mandatory behavior breaks.

## Vector execution rule

Each vector must produce inspectable receipts sufficient to determine:
- input/session;
- capability version;
- evidence sources;
- normalized claims;
- Measured Intent state;
- materially relevant hypothesis weights;
- correction events;
- ranking/stop outcome;
- action or HOLD;
- final gate outcome.

Do not expose private chain-of-thought.
