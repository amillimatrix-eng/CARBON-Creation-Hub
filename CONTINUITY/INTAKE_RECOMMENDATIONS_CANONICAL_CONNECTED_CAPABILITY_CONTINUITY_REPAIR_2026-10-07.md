# AMX INTAKE — CANONICAL CONNECTED-CAPABILITY CONTINUITY REPAIR RECOMMENDATIONS

**Date:** 2026-10-07  
**Status:** OWNER-DIRECTED INTAKE RECOMMENDATION  
**Authority:** Existing ROOT / T-GOV / Intake only  
**Constraint:** This creates no new governance layer, Librarian office, registry, worker, or parallel Intake process.

## 1. Remaining canonical continuity break

The remaining break is not lack of tools. It is loss of **capability continuity across branches, workers, sessions, and executor changes**.

AMX can have a lawful connected capability available in one context and still fail to:
- remember that it exists,
- know which existing owner should use it,
- know what it is allowed to do,
- know its best fallback,
- preserve the result as durable evidence,
- or expose the same capability to the next eligible worker/wake.

That failure silently reduces Matrix capability and conflicts with the standing MOM rule that capability must not be silently discarded.

**Canonical recommendation:** treat connected capability as governed Matrix infrastructure. Presence in a chat is not authority; absence from one chat is not proof of nonexistence. Intake must reconcile each capability into the existing owner/routing model and preserve a durable continuity pointer that workers can consume.

## 2. Required canonical behavior

For every eligible connected capability, the existing governance path should require this minimum continuity contract:

`CAPABILITY -> EXISTING OWNER -> ALLOWED ACTION -> EXECUTION ROUTE -> RECEIPT/READBACK -> FALLBACK -> NEXT-WAKE DISCOVERABILITY`

A capability is not continuity-complete merely because a plugin is installed or callable.

It is continuity-complete only when:
1. current reach is verified without treating current reach as historical authority;
2. its existing AMX owner/lane is identified;
3. allowed and prohibited actions are explicit;
4. at least one bounded lawful execution path is known;
5. material actions produce evidence/readback;
6. failure routes to another lawful executor where possible;
7. the capability and its learned use survive branch/session/worker changes;
8. no worker is forced to rediscover the same capability from zero.

## 3. Explicit capability recommendations

### A. Deep Research / Tavily / Data
**Recommendation:** route these as shared evidence and synthesis capability, not as standalone commercial workers.

Use for:
- market/problem research;
- current external evidence;
- source comparison;
- structured commercial intelligence;
- validation of claims before PRI or Reaper acts;
- evidence packets for iSCOPE clustering.

Continuity requirement:
- source URLs/identifiers, dates, claims, confidence, and resulting decision must be preserved;
- research output without a downstream owner is incomplete;
- a research result must terminate in iSCOPE, PRI, Reaper, Build, governance, or an explicit HOLD.

Fallback:
- if one research provider is unavailable, another lawful search/research route must be attempted before escalation.

### B. Semrush
**Recommendation:** assign to market-demand, competitive, SEO, traffic, and discoverability evidence under the existing commercial discovery route.

Use for:
- validating whether a problem/category has observable demand;
- competitor traffic/keyword signals;
- prioritizing problems/offers by commercial surface;
- identifying buyer acquisition weaknesses that can become bounded paid interventions.

Do not:
- treat SEO metrics alone as proof of buyer pain;
- allow Semrush to define the market boundary.

Receipt:
- query target, metric/date, evidence source, commercial hypothesis, downstream owner.

### C. Clay
**Recommendation:** retain Clay as high-throughput structured prospect/company/contact enrichment for iSCOPE, not as the definition of iSCOPE.

Use for:
- broad company discovery;
- enrichment;
- role/contact identification;
- evidence-backed segmentation;
- four-digit prospect fan-out where quality gates remain intact.

Required repair:
- remove arbitrary tiny-batch behavior;
- prefer 1,000+ commercially actionable nodes as normal throughput where provider limits allow;
- preserve negative evidence, mismatches, dedupe, and contact-domain anomalies;
- never count a row as qualified solely because Clay returned it.

Downstream:
- qualified problem/contact -> PRI;
- ambiguous/mismatched -> HOLD/verify;
- no-fit -> durable negative evidence.

### D. Close
**Recommendation:** route Close as CRM/conversion-state memory for PRI where connected and lawful.

Use for:
- contact history;
- follow-up state;
- opportunity stage;
- prior email/SMS/call context;
- preventing duplicate or contradictory outreach.

Canonical continuity role:
- Close should become a durable conversion-memory surface, not a separate sales authority.

Acceptance:
- one real opportunity can be written/read back with correct stage and evidence;
- PRI can resume from that state next wake.

### E. Gmail
**Recommendation:** retain Gmail as a primary lawful external communication executor for PRI and other authorized business lanes.

Use for:
- buyer outreach;
- follow-ups;
- proposal/package delivery;
- reply intake;
- invoice/payment coordination where appropriate.

Required continuity:
- sent message ID/thread ID must be captured for material sends;
- replies must re-enter the correct owner;
- thread state must survive branch changes;
- no claim of submission without SENT/readback evidence.

Priority:
- highest commercial continuity importance because it terminates discovery in external consequence.

### F. Stripe
**Recommendation:** classify Stripe as a primary payment-consequence rail, not merely infrastructure.

Use for:
- products/prices/payment links;
- collecting bounded paid pilots/interventions;
- payment-state readback.

Canonical repair:
- every PRI offer that can lawfully close by card should be able to terminate in a Stripe payment route without Owner rebuilding the path.

Acceptance:
- create/retrieve a bounded product/price/payment-link test under existing authority;
- preserve the identifier;
- verify payment-state readback;
- route successful payment to BANK truth.

Do not:
- infer revenue from a created link;
- mark paid until payment evidence exists.

### G. monday.com
**Recommendation:** use as operational work-state surface only where it reduces coordination loss.

Use for:
- assigned work;
- owner;
- state;
- deadline;
- dependency;
- durable handoff.

Do not:
- duplicate Intake/governance;
- create a competing source of truth for authority.

Continuity requirement:
- if monday is used, the task must point back to the canonical AMX object/receipt rather than becoming an isolated shadow workflow.

### H. Google Drive
**Recommendation:** retain Drive as durable business-document and evidence storage where already canonical.

Use for:
- buyer packages;
- source documents;
- payment-rail registry;
- rights/production documents;
- spreadsheets;
- governed deliverables.

Continuity repair:
- workers must preserve canonical document IDs/paths;
- a Drive asset should not become “missing” simply because a later branch cannot see it immediately;
- recover by ID/path before rebuilding.

### I. Spreadsheets
**Recommendation:** use Sheets/spreadsheets as structured evidence and operating tables, not as governance authority.

Use for:
- prospect graph exports;
- problem-frequency tables;
- revenue/pipeline analysis;
- KPI/evidence calculations;
- rail registries where already canonical.

Required:
- schema/name/ID preserved;
- readback after write;
- formulas/weights versioned when materially changed;
- downstream workers consume current version rather than copy stale local tables.

### J. Figma
**Recommendation:** classify Figma as the canonical editable design handoff surface when visual/product design requires reusable layers/components.

Use for:
- CARBON° design systems;
- UI/UX remediation;
- client artifacts;
- production-ready editable design.

Continuity:
- preserve file/node IDs;
- export/render is not a substitute for editable source when editability is required;
- Build/CARBON ownership remains unchanged.

### K. Vercel
**Recommendation:** use as one lawful deployment executor for eligible web properties.

Use for:
- previews;
- production deploys;
- environment-backed web delivery;
- deployment evidence.

Required:
- repo/commit -> deploy ID -> live URL -> smoke/readback;
- deployment is not closure until the actual live surface is read back;
- Vercel failure must route to another eligible executor rather than stop the objective.

### L. Descript
**Recommendation:** assign to CARBON°/media production as a bounded editing/repurposing executor.

Use for:
- trailer/audio/video cleanup;
- clips;
- transcripts;
- translation where rights permit;
- production iteration.

Continuity:
- source asset -> edit instruction -> output asset -> review evidence;
- preserve canonical source and do not let an edited derivative silently replace it.

### M. PDF
**Recommendation:** treat PDF generation/editing as a document-output capability shared by existing owners.

Use for:
- buyer-ready packages;
- proposals;
- evidence packs;
- production documents;
- formal deliverables.

Required:
- source-of-truth remains the governed underlying content;
- final PDF receives version/date/provenance;
- visual/readback QA before external delivery.

### N. Presentations / Awesome Slides / Agentic Slides by SlidesGPT
**Recommendation:** classify all slide tools as alternative presentation executors under the same existing content owner, not separate strategy authorities.

Use for:
- pitch decks;
- buyer review packages;
- investor/client explanation;
- internal evidence presentation.

Continuity rule:
- content authority precedes presentation generation;
- slide executor may improve structure/visuals but may not invent rights, revenue, acceptance, contracts, episode facts, or other unknowns;
- preserve editable source plus exported artifact where possible.

Fallback:
- if one slide provider fails, use another eligible slide executor without changing content authority.

### O. Blockscout Blockchain Data
**Recommendation:** assign to Reaper/on-chain evidence acquisition and verification.

Use for:
- wallet/transaction/contract/source/token/NFT/on-chain state lookup;
- open-chain evidence;
- bounty investigation;
- payout/payment verification where relevant.

Required:
- chain, address/tx/contract identifier, block/time, result, and inference separated;
- observation is not exploit authorization;
- no funds movement or live exploitation without explicit authority;
- provider failure must not erase the Reaper hypothesis/evidence state.

### P. Metricool
**Recommendation:** keep in priority remediation until at least one canonical social surface is connected and read/write verified.

Use for:
- scheduled social distribution;
- analytics;
- recommended posting windows;
- publication state.

Current continuity rule:
- do not count Metricool as live distribution merely because the plugin is connected;
- require connected social account -> authorized post action -> platform publication/readback -> analytics retrieval.

Until then:
- Metricool remains a non-blocking degraded route;
- commercial execution continues through other lawful channels.

### Q. TinyFish
**Recommendation:** classify TinyFish as a browser/web executor, never a P0 dependency.

Use for:
- websites that require interaction;
- navigation;
- bounded browser workflows;
- structured web extraction when appropriate.

Continuity repair:
- credits/provider exhaustion must trigger alternate lawful route;
- no objective may stop merely because TinyFish is unavailable;
- preserve partial state before rerouting.

## 4. Cross-capability routing recommendations

### Commercial path
`Deep Research / Tavily / Semrush / Clay -> iSCOPE -> Close/Gmail -> PRI -> Stripe -> BANK -> durable receipt`

The chain is illustrative, not mandatory. Any replaceable step may be substituted by another lawful executor while preserving the objective.

### Creative/production path
`problem/brief -> CARBON° -> Figma/Descript/Slides/PDF -> Drive -> Gmail/Close -> buyer -> Stripe/BANK`

### Build/deployment path
`qualified build -> existing Build authority -> Figma/code -> Vercel/other executor -> live readback -> receipt -> owner`

### Reaper path
`bounty/opportunity -> research/data/Blockscout -> Reaper reasoning -> bounded validation -> authorized submission -> payout evidence -> BANK`

## 5. Priority order for continuity repair

### P0 — revenue consequence
1. Gmail external consequence continuity
2. Stripe payment consequence continuity
3. Clay high-throughput iSCOPE feed
4. Close conversion memory
5. Tavily / Deep Research / Semrush evidence-to-offer routing
6. Blockscout Reaper evidence continuity

### P1 — production/delivery
7. Drive + Spreadsheets durable asset/data continuity
8. Figma + Vercel build/deploy continuity
9. Descript + PDF + slide executors production continuity

### P2 — distribution/coordination
10. Metricool social connection/readback repair
11. monday.com operational handoff only where it reduces loss
12. TinyFish browser execution as optional accelerator/fallback

This priority order does not authorize any role to seize another owner’s mandate.

## 6. Mandatory fallback rule

A connected-service failure is a route failure, not automatically an objective failure.

`PRIMARY EXECUTOR FAILS -> PRESERVE STATE -> TRY LAWFUL ALTERNATE -> CONTINUE -> RECORD FAILURE EVIDENCE`

Escalate to Owner only for a genuine irreducible external/human/security/legal/provider gate after lawful route recovery has been exhausted.

## 7. Acceptance test for the canonical continuity repair

The break is closed only when governance can demonstrate all of the following on real work:

- a worker discovers an existing capability without Owner reteaching;
- governance/authority ownership remains correct;
- a material task is routed to that capability;
- the capability produces a real external or durable consequence;
- the result is read back;
- failure can route around a replaceable provider;
- the next eligible wake consumes the updated state;
- the same capability does not disappear merely because the conversation/branch changed.

**Terminal proof pattern:**
`RECOVER/RESOLVE CAPABILITY -> ROUTE -> EXECUTE -> REAL OUTPUT/RECEIPT -> READ BACK -> RETAIN -> REUSE`

## 8. Intake disposition requested

ROOT / T-GOV should reconcile these recommendations against existing governance and implement only the deltas required to close connected-capability continuity.

Do **not** create:
- a second Intake,
- a new Librarian office,
- a new commercial worker,
- a parallel capability registry that conflicts with existing authority,
- or a new protocol merely to name this repair.

The intended result is behavioral: existing AMX workers reliably retain and use lawful connected capability across branches, failures, and wakes, with evidence and fallback.

**Recommended disposition:** ACCEPT FOR RECONCILIATION AND IMPLEMENTATION UNDER EXISTING GOVERNANCE.
