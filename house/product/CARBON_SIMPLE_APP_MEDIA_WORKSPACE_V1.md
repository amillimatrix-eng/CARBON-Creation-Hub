# CARBON° Simple App / Media Workspace V1

Date: 2026-10-09
Owner direction: ACCEPTED / EXECUTION STARTED
Primary classification: PRODUCT / ECOSYSTEM INTEGRATION
Tracking: GitHub issue #18

## 1. PURPOSE

Make CARBON° feel like one simple app rather than separate Search, Marketplace, media, storage and production surfaces.

The user should experience:

SEARCH → RESULT / MATCH → CREATE / OPEN PROJECT → MEDIA → ACTION / DELIVER

without needing to understand the internal Matrix architecture.

## 2. DISTRIBUTION DECISION

Current recommended path is accepted with one material constraint:

- PRIMARY NOW: standalone responsive web app.
- INSTALLABILITY: PWA / Add-to-home-screen when technically ready.
- LATER: Google Play / Android packaging after the web/PWA product is proven.
- OPTIONAL LATER: Telegram Mini App as a thin access/acquisition surface.
- CUSTOM DOMAIN: DEFERRED / BUDGET HOLD. Do not make a paid custom domain a launch dependency.

Current Vercel/provider URL may remain the technical host while product UI hides infrastructure branding as far as the platform legitimately permits.

A domain purchase is not required to build or prove the product.

## 3. OWNERSHIP

### CARBON° owns PRODUCT / EXPERIENCE
CARBON° owns:
- user-facing Search/Marketplace/Project/Media experience;
- media creation workflow requirements;
- image/video/audio product behavior;
- workspace information architecture;
- artifact quality and buyer/user readiness;
- provider-routing product requirements;
- storage-mode experience;
- premium Matrix Mode design requirements.

### T-COD owns IMPLEMENTATION
T-COD owns:
- app shell implementation;
- PWA manifest/service-worker/installability;
- workspace/media UI implementation;
- storage adapters/object-store integration;
- backend/API wiring;
- Search↔Marketplace↔media-action contracts;
- ACL/auth implementation;
- tests/deployment/readback.

### MATRIX / ROOT / LIBRARIAN owns CONTINUITY / GOVERNANCE
- mandate and authority;
- Intake routing;
- blocked-attempt recovery;
- evidence/readback;
- cross-product continuity;
- no duplicate implementation.

### iSCOPE / PRI
Do not build the product.
They consume buyer/market evidence and later execute GTM/commercial conversion once launch gates pass.

### Banker
Does not build the product.
Banker controls paid-spend/ROI truth and later acquisition scaling.

## 4. SIMPLE APP SHELL

Default navigation should remain small:

- Search
- Marketplace
- Projects
- Media
- Account / Settings

Do not expose internal worker names, governance surfaces or provider complexity to normal users.

### Search
One dominant search box.
Minimal filter tuning per `CARBON_SEARCH_SIMPLE_DISCOVERY_UX_V1.md`.

### Marketplace
Results/matches/offers that follow Search intent.
Marketplace is not a separate classifieds maze.

### Projects
A project is the continuity container for:
- search session;
- selected result/match;
- brief;
- generated/attached media;
- versions;
- actions;
- delivery state.

### Media
A simple media library scoped to user/workspace/project:
- Images
- Video
- Audio
- Documents / listing assets

Media items show:
- preview;
- project;
- status;
- created/updated time;
- rights/provenance state where relevant;
- primary action.

## 5. MEDIA CREATION

From a Search result, Marketplace match or Project, user can choose bounded actions:

- Create image
- Create short video
- Create voiceover/audio
- Create listing/package
- Add existing file

The system routes internally to CARBON/provider capability.
The user should not need to choose providers unless using an advanced/business setting.

## 6. STORAGE

Until Governance selects a production storage provider:

- define the object/media contract now;
- keep media storage provider-neutral;
- frontend hosting is not canonical media storage;
- support hosted mode first;
- preserve adapter path for BYO storage later;
- minimal-retention mode remains a governed product option.

Required media object fields:
- artifact_id
- workspace_id
- project_id
- owner_id / owner scope
- media_type
- object_reference
- thumbnail/reference
- version
- status
- visibility / ACL
- provider
- provider_job_id where available
- provenance
- rights/commercial_use
- created_at / updated_at
- content hash where available

## 7. FIRST BUILDABLE NON-SEARCH WORK

These items may proceed without mutating Search #16 semantics:

1. responsive app-shell information architecture;
2. Projects data contract;
3. Media object contract;
4. Media library UI contract;
5. Create-media action contract;
6. PWA installability spec;
7. storage-provider adapter interface;
8. premium Matrix Mode theme spec;
9. public demo flow;
10. analytics event contract.

## 8. SEARCH BUILD BOUNDARY

Anything that changes the frozen Search semantic core remains dependent on issue #16 completion.

However, the app shell, Projects, Media, PWA, storage contracts and non-core integration scaffolding are not blocked by Search completion.

## 9. ACCEPTANCE

A first CARBON app/workspace tranche is PASS when:

- one responsive shell exposes Search / Marketplace / Projects / Media coherently;
- user can create/open a Project;
- project can reference a Search session/result without duplicating Search logic;
- at least one media item can be attached or generated through a provider-neutral action contract;
- media metadata persists and reads back;
- ACL/ownership state is explicit;
- PWA installability works on supported browsers;
- no custom domain is required;
- internal provider/governance complexity is hidden from normal user flow;
- existing Search #16 acceptance remains unchanged.

## 10. DESIGN LAW

**ONE CARBON. MANY SURFACES. ONE CONTINUITY.**

WEB / PWA / FUTURE ANDROID / FUTURE TELEGRAM are callers of the same product core, not separate CARBON implementations.
