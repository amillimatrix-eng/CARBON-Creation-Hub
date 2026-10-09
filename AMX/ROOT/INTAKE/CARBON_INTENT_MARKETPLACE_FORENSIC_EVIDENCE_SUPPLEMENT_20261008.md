# AMX ROOT INTAKE — CARBON° INTENT MARKETPLACE FORENSIC EVIDENCE SUPPLEMENT

**Date:** 2026-10-08  
**Prepared by:** MASTER/COFFEE evidence-assurance support  
**Class:** P2 EVIDENCE / detached forensic supplement  
**Lifecycle effect:** Evidence only. No Canon, Merge, BUILD-release, title/credential, or authority promotion.  
**Preservation rule:** The source evidence document and implementation branch are NOT modified by this supplement.

## 1. Evidence request being satisfied

This supplement preserves and binds the currently observable evidence supporting the CARBON° intent-weighted marketplace definition-to-implementation event so the originating Intake reviewer can assess it without requiring Owner reconstruction or intervention.

The requester should evaluate the evidence under the source artifact's own Intake order:

1. Infrastructure Compatibility
2. Constitutional Compliance
3. Duplication
4. Responsibility Ownership
5. Canon Impact
6. Merge Recommendation

## 2. Primary source artifact — preserved in place

**Title:** CARBON° — Product Evidence Intake — Intent-Weighted Marketplace  
**Google Drive file ID:** `1pE4FfUd3-G3Xkzy_cJved2pa3BRLUTjRZhnPBIEKzEk`  
**Source revision observed:** `AHj4eMSBZsOKroJRz1hd0BFFzl9e3BQWsT7Igo1-rvFWR_uNjIPH39sNsgrgugyhfD-lx7BeaOlHnU6NaHQXKILqaW16pF6V-wQt8z9zZA`  
**Created:** 2026-10-08T18:59:20.296Z / 20:59:20 SAST  
**Last modified at evidence capture:** 2026-10-08T19:33:39.351Z / 21:33:39 SAST

The source itself declares:

- lifecycle = PRESENT → submitted for INDEX / evaluation;
- not Merged;
- not Canon;
- not standalone build authority;
- preserve provenance;
- implementation evidence does not itself authorize Merge/Canon.

### Product definition preserved by the source

**Product thesis:** CARBON° is an intent-weighted marketplace.

**Core chain:**
`Intent → Commitment → Bond → Time → Behaviour → History → Market Intelligence.`

**Core principle:**
`Freedom until commitment. Accountability after commitment.`

The source further distinguishes buyer/seller reciprocal obligation, bounded commitment, time as first-class, responsible exit versus breach, evidence from actual behaviour, UNKNOWN as neutral, and anti-auction / money-does-not-buy-priority controls.

## 3. Repository implementation evidence

**Repository:** `amillimatrix-eng/CARBON-Creation-Hub`  
**Implementation branch:** `build/carbon-intent-marketplace-v1`  
**Draft PR:** #14 — `CARBON°: intent-weighted marketplace vertical slice`  
**Verified evidence head:** `fd14ec8733ae1c3652c8cc5ad8424a0fd6caaffc`  
**Head commit:** `CARBON: expose separate purchase-funding clock in UI`  
**Head commit time:** 2026-10-08T19:30:32Z / 21:30:32 SAST  
**Author/committer observed:** `amillimatrix-eng`

### Main → build branch comparison at capture

**Merge/base commit:** `0e837bb4ad624fe5c5a0421ddab78ea92a35a094`  
**Base commit time:** 2026-10-08T18:02:13Z / 20:02:13 SAST  
**Branch relation:** AHEAD  
**Ahead by:** 75 commits  
**Behind by:** 0 commits  
**Changed files:** 24  
**Observed additions:** 2,455  
**Observed deletions:** 2

**Repository-bounded evidence window:** 20:02:13 → 21:30:32 SAST = **1h 28m 19s**.

This interval supports a bounded claim that the implementation delta represented by the current branch was produced within a sub-three-hour repository window. It does **not** prove that every conceptual precursor began at 20:02:13, and it must not be expanded into such a claim.

### Principal implementation files in the branch delta

- `backend/carbon_app.py`
- `backend/marketplace.py`
- `backend/marketplace_money.py`
- `backend/marketplace_participant.py`
- `backend/marketplace_time.py`
- `marketplace/index.html`
- `marketplace/app.js`
- `marketplace/styles.css`
- `marketplace/README.md`
- `tests/test_marketplace.py`
- `tests/test_marketplace_abuse.py`
- `tests/test_marketplace_evidence.py`
- `tests/test_marketplace_extensions.py`
- `tests/test_marketplace_messages.py`
- `tests/test_marketplace_money.py`
- `tests/test_marketplace_open_gate.py`
- `tests/test_marketplace_participant.py`
- `tests/test_marketplace_queue.py`
- `tests/test_marketplace_terms.py`
- `tests/test_marketplace_time.py`
- Docker / CI / environment / deployment configuration changes.

## 4. CI, runtime and preview evidence

The source Intake artifact records:

- branch-head CI run `37830184039` — PASS;
- later verified CI run `37832482959` — SUCCESS;
- complete pytest suite passes;
- existing smoke suite passes;
- provider-neutral Docker image builds;
- container runtime starts;
- existing AMX Evidence House health/bootstrap remains valid;
- `/api/carbon/bootstrap` responds;
- `/market` responds;
- `money_moved=false`;
- production demo mode false by default in the build;
- core law `freedom_until_commitment` exposed by bootstrap.

**Dedicated preview:**  
`https://carbon-intent-marketplace-v1-preview.onrender.com/market`

The source records independent public preview readback with:

- `product=CARBON°`;
- `money_adapter=SANDBOX_NO_MONEY_MOVED`;
- `money_moved=false`;
- `custody=false`;
- `production_provider_connected=false`;
- `demo_mode=true`;
- `freedom_until_commitment=true`;
- `unknown_is_not_bad=true`;
- `money_does_not_buy_priority=true`;
- `bilateral_commitment=true`;
- `proper_exit_is_not_breach=true`.

A current GitHub combined-status check on the evidence head separately reports **Vercel failure: build-rate-limit / upgradeToPro**. This is recorded as a provider-specific deployment-rate status, not as evidence that the branch tests failed. It must not overwrite the separately recorded GitHub Actions/Render evidence above.

## 5. Executable slice evidenced

The source + PR evidence supports the following implemented scope at this branch state:

- seller intent and bounded bond configuration;
- buyer bonded interest;
- cap on commitment considered for intent weighting;
- no richest-first ordering;
- bond-gated private contact;
- seller-side qualification filters;
- seller selection without activating buyer consequence;
- bilateral activation only after buyer review/confirmation;
- hashed reciprocal commitment terms;
- time-bound expiry / performance review;
- responsible exit separated from breach;
- mutual extension with provenance-preserving term rehash;
- buyer and seller performance evidence;
- separate bond-funding and purchase-funding clocks;
- inspection only after purchase funds are secured;
- independent buyer/seller deal acceptance;
- explicit no-deal path;
- BONDED_DEAL state;
- deterministic pseudonymous C° actor references;
- append-only marketplace event history;
- role-specific factual evidence with UNKNOWN neutral and no public score;
- provider-neutral reserve/release/hold/settlement boundary;
- fail-closed production-write posture;
- sandbox provider incapable of moving real money.

## 6. Intake-request satisfaction map

### 6.1 Infrastructure Compatibility — EVIDENCE PRESENT

The implementation extends the existing FastAPI / SQLite / Evidence House spine rather than introducing an unrelated replacement architecture. Existing Evidence House health/bootstrap is recorded as remaining valid. Main-branch services were not modified by the dedicated preview deployment.

### 6.2 Constitutional Compliance — EVIDENCE PRESENT / EXTERNAL GATES HELD

The branch materially encodes the source's accepted product constraints:

- freedom until commitment;
- bilateral obligation before consequence;
- money does not buy priority;
- UNKNOWN is neutral;
- proper exit is not breach;
- factual behavioural evidence rather than unsupported public scoring;
- sandbox/no-money provider boundary.

External legal/payment/identity obligations remain explicitly held rather than simulated.

### 6.3 Duplication — NO EVIDENCE OF REQUIRED PARALLEL AUTHORITY

The implementation uses a provider-neutral money abstraction and preserves boundaries identified by the source: CARBON° may create transaction-domain evidence but does not silently become the Matrix-wide durable reputation authority. James remains associated with verification; ODA remains associated with durable reputation.

### 6.4 Responsibility Ownership — BOUNDED

CARBON° owns the marketplace/product-domain implementation represented by this branch. Provider, identity/KYC/AML, legal forfeiture/breach rules, fraud/dispute operations and live settlement remain external or separate-authority gates and are not falsely claimed complete.

### 6.5 Canon Impact — NONE FROM THIS RECEIPT

The source and this supplement both preserve the rule that coherence, CI success, a live preview, or a draft PR do not themselves create Canon or Merge authority.

### 6.6 Merge Recommendation — REVIEWABLE EVIDENCE PACKAGE READY

PR #14 is a concrete draft implementation package with a verified head, bounded branch delta, tests, preview and explicit external holds. It is therefore reviewable for governance/technical disposition without requiring the Owner to reconstruct the session. This supplement does not decide the disposition.

## 7. Claim ceiling / evidentiary integrity

### Supported

- A coherent product-definition artifact exists.
- A substantial implementation branch exists.
- The branch is 75 commits ahead of the observed main merge-base and zero behind at capture.
- The delta spans 24 files and approximately 2.4k added lines.
- Dedicated tests cover marketplace, abuse, evidence, extensions, messages, money, open-gate, participant, queue, terms and time behaviour.
- The source records successful CI and a reachable dedicated Render preview.
- A repository-bounded implementation interval of 1h28m19s is evidenced between the observed merge-base commit and the verified branch head.
- The source evidence and implementation receipt are directly linked in one durable Intake artifact.

### Not supported / not promoted

- No claim that the entire conceptual history began at the merge-base timestamp.
- No production real-money settlement.
- No production KYC/AML completion.
- No legal approval of forfeiture/breach economics.
- No production fraud/dispute-operations completion.
- No automatic Canon/Merge authority.
- No automatic professional-title or credential award from this receipt alone.

## 8. Preservation / chain of custody

This supplement is deliberately **detached** from the implementation branch and primary Drive artifact.

- The original Google Drive evidence document was read, not rewritten.
- The implementation branch `build/carbon-intent-marketplace-v1` was read, not modified.
- PR #14 was read, not modified.
- The verified head remains `fd14ec8733ae1c3652c8cc5ad8424a0fd6caaffc` at the point of this receipt.
- The Google Drive revision ID above fixes the source revision observed during evidence capture.
- This supplement exists only to prevent evidence decay, context loss, stale reconstruction, or Owner-as-transport dependency.

## 9. Requester handoff

**Disposition of this supplement:** EVIDENCE REQUEST SATISFIED — SOURCE PRESERVED / DETACHED RECEIPT.

The Intake reviewer now has a bounded, independently traceable evidence set covering:

`SOURCE DEFINITION → SOURCE REVISION → REPOSITORY → BRANCH → PR → MERGE-BASE → VERIFIED HEAD → DIFF → TEST SURFACE → PREVIEW → EXTERNAL HOLDS → CLAIM CEILING`.

No Owner action is required to reconstruct this evidence.
