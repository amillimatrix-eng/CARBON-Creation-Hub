# ROOT INTAKE — ARTIFACT DELIVERY FALSE-COMPLETION / CV EXPORT FAILURE

**Intake ID:** ROOT-20261009-ARTIFACT-DELIVERY-FALSE-COMPLETION-CV  
**Date:** 2026-10-09  
**Priority:** A  
**Class requested:** GOVERNANCE CLASSIFICATION REQUIRED  
**Domain:** BUILD / ARTIFACT DELIVERY / EVIDENCE / USER-FACING COMPLETION  
**Owner direction:** Preserve the evidence, classify the failure, and determine the required Matrix-wide control.

## Incident

A refreshed professional CV was created in the runtime and visually rendered. The assistant then declared the artifact usable and supplied a user-facing download link.

The user received:

**"library file not found."**

The assistant then interpreted the failure as a bad attachment/link and responded by re-exporting/renaming the document under a simpler filename.

That interpretation and repair were incomplete.

## Recovered evidence

### Original artifact

Runtime readback now confirms:

- Path: `/mnt/data/Ulrich_du_Plessis_Professional_Resume_2026_October_Evidence_Rebuild.docx`
- Size: 41,327 bytes
- Runtime mtime: 2026-10-09T06:18:41Z

Rendered PDF also exists:

- Path: `/mnt/data/profile_render/Ulrich_du_Plessis_Professional_Resume_2026_October_Evidence_Rebuild.pdf`
- Size: 55,475 bytes
- Runtime mtime: 2026-10-09T06:18:44Z

Therefore the original failure was **not adequately described as "the file did not exist."**

### Failed user-facing delivery

The assistant supplied a sandbox/download reference to the original DOCX.

The user reported that the client surfaced **"library file not found."**

That user-visible failure is direct evidence that local runtime existence was not sufficient to prove successful delivery to the user.

### Incorrect first repair interpretation

The assistant responded:

> "The previous attachment link was bad."

and then produced a simpler filename:

- Path: `/mnt/data/Ulrich_du_Plessis_CV_October_2026.docx`
- Size: 41,327 bytes
- Runtime mtime: 2026-10-09T06:28:06Z

The simpler file is byte-size equivalent to the original document.

The response did not first distinguish among:

- local runtime file existence;
- conversation attachment/surfacing state;
- Library state;
- sandbox download resolution;
- client-visible delivery state.

The rename/re-export therefore addressed a symptom without first proving the failure mode.

## Failure statement

The material failure is:

**LOCAL_ARTIFACT_EXISTS != USER_DELIVERABLE_AVAILABLE**

The assistant collapsed these states and declared completion too early.

This created a false-completion condition:

**BUILD COMPLETE / LOCAL FILE EXISTS** was treated as equivalent to **DELIVERY COMPLETE / USER CAN ACCESS FILE**.

The user's failed retrieval disproved that assumption.

## Why this is governance-relevant

This incident falls directly under the active AMX BLUE STATE rule:

**CAPABILITY AND ACHIEVEMENT ARE EVIDENCE. EXCUSES ARE NOT.**

Evidence that a file was generated is evidence of generation.

It is **not** evidence of delivery.

Evidence that a document rendered correctly is evidence of rendering.

It is **not** evidence that the user can retrieve it.

A delivery claim therefore requires delivery evidence.

This distinction is not limited to CV files. It applies to:

- documents;
- PDFs;
- spreadsheets;
- slides;
- images;
- ZIP packages;
- repository artifacts;
- commercial deliverables;
- client assets;
- generated evidence packs;
- any other output whose value depends on successful downstream access.

## Candidate governance classification

Governance should classify this incident. Suggested candidate categories for consideration:

1. **False Completion / State Conflation**
   - local creation was mistaken for user-deliverable completion.

2. **Artifact Delivery Evidence Gap**
   - no explicit delivery receipt/readback was required before closure.

3. **Cross-Surface State Drift**
   - runtime/container state, conversation attachment state, Library state and user-visible state were treated as interchangeable.

4. **Repair-Before-Diagnosis**
   - the assistant changed filename/export state before establishing the actual failed boundary.

5. **Commercial Reliability Risk**
   - the failed artifact was a professional CV intended for commercial/profile use; delivery failure therefore affects external-facing execution, not only internal convenience.

Governance may merge, rename, or reject these candidate classifications.

## Proposed mandatory control for governance consideration

Do not mark a user-facing artifact **DELIVERED / COMPLETE** solely because it exists in the runtime.

For material deliverables, require a state chain equivalent to:

**CREATE → VERIFY CONTENT → VERIFY FILE EXISTS → SURFACE/ATTACH → VERIFY DELIVERY RECEIPT/ACCESS PATH → COMPLETE**

Where the platform cannot independently verify final client access, the system must not overstate the last state. Use the strongest evidenced state available, for example:

- CREATED;
- VERIFIED LOCALLY;
- ATTACHED/SURFACED;
- DELIVERY UNCONFIRMED;
- USER-RETRIEVED / DELIVERY CONFIRMED.

A user report such as "file not found" must immediately reopen the delivery state and trigger diagnosis of the exact boundary before re-export, rename, replacement, or closure.

## Anti-drift rule

Never infer:

**container path exists → user can download it**

Never infer:

**artifact uploaded → client retrieved it**

Never infer:

**link emitted → link resolved**

Never infer:

**replacement filename → root cause fixed**

Each transition requires its own evidence.

## Requested governance action

Governance must:

1. classify the incident;
2. decide whether this becomes a Matrix-wide build/operational control;
3. map it into existing BLUE STATE / completion / evidence rules rather than creating duplicate governance;
4. determine the required receipt semantics for user-facing artifact delivery;
5. propagate the resulting control to all artifact-producing workers and commercial-production flows if accepted;
6. preserve this incident as the originating evidence case.

## Current disposition

**SUBMITTED TO ROOT/INTAKE — GOVERNANCE CLASSIFICATION REQUIRED.**

This packet does **not** self-authorize the proposed control.
