# CARBON° App + Projects + Media — Implementation Packet V1

Date: 2026-10-09
Product owner: CARBON°
Implementation owner: T-COD
Tracking: GitHub issue #18
Status: READY FOR NON-SEARCH IMPLEMENTATION

## 0. BOUNDARY

This packet intentionally avoids changing CARBON° Search V1 semantic acceptance.

Buildable now:
- app shell;
- Projects;
- Media;
- media metadata;
- provider-neutral media actions;
- PWA installability scaffolding;
- storage adapter interface;
- simple user flow.

Do not wait for a paid custom domain.

## 1. APP NAVIGATION

Normal-user navigation:

1. Search
2. Marketplace
3. Projects
4. Media
5. Account

Keep navigation shallow. Do not expose Matrix workers, Intake, provider routing or governance internals.

## 2. PROJECT CONTRACT

A Project is the continuity container for one user objective.

Minimum fields:

- project_id
- owner_scope
- title
- description / brief
- lifecycle_state
- linked_search_session_id optional
- linked_marketplace_entity_ids[]
- media_asset_ids[]
- created_at
- updated_at
- last_action
- next_action optional

Project lifecycle:
DRAFT → ACTIVE → READY → DELIVERED → ARCHIVED

A Project does not own Search logic. It references Search session/result IDs.

## 3. MEDIA OBJECT CONTRACT

Minimum fields:

- artifact_id
- owner_scope
- workspace_id optional
- project_id optional
- media_type: IMAGE | VIDEO | AUDIO | DOCUMENT | LISTING_PACKAGE
- title
- object_reference
- preview_reference optional
- source_type: UPLOAD | GENERATED | DERIVED | EXTERNAL_REFERENCE
- provider optional
- provider_job_id optional
- version
- lifecycle_state
- visibility_acl
- rights_state
- commercial_use_state
- provenance_pointer
- content_hash optional
- created_at
- updated_at

Lifecycle:
REQUESTED → GENERATING / PROCESSING → READY_FOR_REVIEW → APPROVED → DELIVERED
with FAILED / HOLD available where truthful.

## 4. MEDIA LIBRARY

Default screen:
- grid/list toggle;
- simple search;
- media-type chip;
- project chip;
- status chip only if needed.

Do not create a heavy DAM interface.

Card:
- preview;
- title;
- type;
- project;
- state;
- modified time;
- one primary action.

Primary actions:
- Open
- Add to project
- Use in listing
- Create variant
- Download/export when permitted

## 5. CREATE MEDIA

Entry points:
- Search result
- Marketplace result
- Project
- Media library

Actions:
- Create image
- Create short video
- Create voice/audio
- Create listing package
- Upload existing media

User supplies a brief in plain language.

Provider selection is automatic by default.

Advanced/business setting may later expose provider preferences.

## 6. PROVIDER-NEUTRAL ACTION CONTRACT

POST /api/media/actions

Request:
- action_type
- project_id optional
- source_artifact_ids[]
- user_brief
- constraints
- target_format optional
- authorized_context
- storage_mode

Response:
- action_id
- state
- provider_route abstracted
- created_artifact_ids[]
- hold_reason optional
- receipt_pointer

Provider failure:
- retain action_id;
- retain completed state;
- retry/reroute if authorized;
- otherwise create OPEN EXECUTION OBLIGATION under current Blue State.

## 7. STORAGE ADAPTER

Interface:
- put
- get
- delete
- signed_access / controlled_access
- metadata
- hash/readback

Implement provider-neutral interface first.

Production provider selection may follow separately.

Frontend/static hosting must not be treated as canonical user media storage.

## 8. PWA

Required:
- web app manifest;
- icons;
- installable shell where supported;
- standalone display mode;
- responsive layout;
- service-worker strategy only where it does not risk stale commercial/search state;
- offline shell may exist, but dynamic Search/Marketplace truth must not silently appear current while offline.

App name:
CARBON°

Suggested short name:
CARBON

No custom domain dependency.

## 9. FIRST USER FLOW

New user opens CARBON:

1. sees one dominant Search field;
2. searches or browses Marketplace;
3. opens a result;
4. chooses Create / Save to Project;
5. Project is created or selected;
6. generated/uploaded media appears in Media;
7. user reviews;
8. approved asset is used/exported/delivered.

A user should understand this without documentation.

## 10. MATRIX MODE

Implement only as a theme layer.

Do not couple it to business logic.

Theme contract:
- default CARBON mode;
- optional MATRIX MODE;
- shared component tree/state;
- reduced-motion support;
- no theme-only features required for task completion.

## 11. ANALYTICS EVENTS

Minimum:
- search_started
- search_resolved
- marketplace_result_opened
- project_created
- media_action_started
- media_action_completed
- media_action_failed
- media_approved
- media_delivered
- pwa_install_prompted
- pwa_installed

No private content in analytics payloads by default.

## 12. ACCEPTANCE TEST

PASS when a deployed test user can:

1. open app shell;
2. create a project;
3. attach or generate at least one media item through the action abstraction;
4. see it in Media;
5. reopen it from the Project;
6. preserve owner/ACL/provenance state;
7. install the PWA where browser support exists;
8. complete flow without a custom domain;
9. read back persisted state after reload;
10. do all of this without changing Search #16 semantics.

## 13. OWNERSHIP CHECK

CARBON° decides what the user experience/product should do.
T-COD implements it.
ROOT/Governance arbitrates authority/conflict.
Librarian verifies continuity/readback.
No second CARBON app architecture is authorized.
