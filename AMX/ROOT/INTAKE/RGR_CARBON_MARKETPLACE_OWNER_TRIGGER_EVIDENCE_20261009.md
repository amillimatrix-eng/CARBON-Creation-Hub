# RGR EVIDENCE — OWNER-TRIGGERED CORRECTION / CARBON° MARKETPLACE

**Date:** 2026-10-09  
**Intake ID:** ROOT-20261009-RGR-CARBON-MARKETPLACE-OWNER-TRIGGER  
**Class:** RGR EVIDENCE / EXECUTION-BEHAVIOR DEFECT  
**Lifecycle effect:** Evidence only. No Merge, Canon, credential, or build authority promotion.

## Observed sequence

1. CARBON° Marketplace implementation was inspected.
2. The implementation itself was found to be substantial and materially aligned with the intent-weighted marketplace product.
3. The live public deployment was then checked.
4. The public Vercel root served the older CARBON° Creation House rather than the Marketplace.
5. The intended `/market` route returned 404.
6. Repository comparison showed `build/carbon-intent-marketplace-v1` was 75 commits ahead and 102 commits behind current `main`.
7. The system correctly identified the necessary next corrective action: reconcile the branch with current `main`, rerun current-head validation, and deploy/read back the actual Marketplace surface.
8. Despite already identifying both the defect and the correction, the system stopped at recommendation.
9. The Owner then had to explicitly instruct: **"Then rebase reconcile"**.
10. The Owner separately had to instruct that this fact itself be preserved as RGR evidence and routed to Intake in the same run.

## Evidentiary point

The defect was already known.  
The required correction was already known.  
The available execution path was within the connected GitHub capability.

The Owner was nevertheless required to convert an already-known corrective requirement into action.

That Owner-trigger dependency is the RGR evidence being preserved here.

## Why this matters

A system that can:
- detect the operational defect;
- identify the exact corrective action;
- possess the capability required to perform the correction;

but then stops at recommendation and waits for the Owner to restate the obvious next action creates avoidable Owner dependency and execution latency.

The subsequent success or failure of the reconciliation does not erase the evidence. The relevant event is the requirement for Owner prompting after the corrective path was already established.

## Requested Intake treatment

- Preserve as RGR evidence.
- Evaluate against existing execution/governance controls; do not invent a parallel governance system.
- Determine whether this behavior is already covered by an existing RGR / continuation / execution-completion control.
- If already covered, attach this as additional evidence.
- If not, classify through existing Intake protocol.
- Do not infer Canon or lifecycle promotion from this receipt.

## Immediate corrective action in the same run

The CARBON° Marketplace branch is being reconciled against current `main` in the same run in which this evidence is submitted, rather than creating another Owner handoff.


## Same-run corrective outcome

The corrective action requested by the Owner was executed in the same run.

- Reconciliation method: **non-destructive merge reconciliation** rather than history-rewriting rebase, preserving branch provenance.
- Current-main authority incorporated through: `18faf14db0a31c6e44d6fd8851c5e8e27ffdbe89`.
- Reconciliation commit: `027a699a7cd213202f66fa24a256b2fda467974d`.
- CI-trigger receipt commit: `9fe82f9398f13950732f65ca31107093b251380b`.
- Post-reconciliation comparison: **77 commits ahead / 0 behind main**.
- PR #14 state after reconciliation: **OPEN / DRAFT / MERGEABLE**.
- Conflict assessment: current-main changes since the original merge base did not overlap the 24 marketplace branch paths, so the reconciliation could preserve both main and marketplace content without semantic conflict substitution.

### Remaining unresolved execution item

GitHub Actions did **not** auto-start on the reconciled head even after a watched-path Marketplace reconciliation receipt was committed. Therefore:

- no new green CI claim is made for `9fe82f9398f13950732f65ca31107093b251380b`;
- prior green CI remains historical evidence only;
- current-head validation remains **OPEN** until an actual run/readback exists.

This unresolved item does not undo the branch reconciliation and does not erase the RGR evidence. It is preserved as the next execution dependency rather than being silently treated as complete.


## Additional RGR evidence — completion criterion required Owner correction

A second Owner-trigger event occurred after branch reconciliation.

### Sequence

1. The Marketplace branch was reconciled and returned to **ahead / 0 behind** with PR #14 mergeable.
2. The system reported the reconciliation outcome and described the live `/market` release as not yet re-claimed.
3. The Owner then asked: **"Can I open it or not yet? Because if I can't open it, then it's not done, is it?"**
4. That Owner challenge exposed a completion-control failure: a product build had been discussed as substantially completed/reconciled even though the user-facing product was still not actually openable at the expected public route.
5. Only after that Owner intervention did the system inspect the deployment infrastructure directly.
6. The Render service `carbon-intent-marketplace-v1-preview` was found to exist and to track the correct branch, but its last live deployment was still the older commit `fd14ec8733ae1c3652c8cc5ad8424a0fd6caaffc` from 2026-10-08.
7. The reconciled branch head had **not** been deployed automatically.
8. The system then manually triggered a Render deployment for reconciled commit `6e7126f0c9aed3b395a2cd93a3d8970c08eb44cb`.
9. Render deployment `dep-db4e41nlk1mc73fo6dhg` reached **live**.
10. The public route `https://carbon-intent-marketplace-v1-preview.onrender.com/market` was independently fetched and returned the actual Marketplace surface with title **"CARBON° — Intent has weight."**
11. Readback confirmed visible product copy including:
    - **"THE MARKET WHERE INTENT HAS WEIGHT"**
    - **"What's your intent?"**
    - **"Browse all you want. When you mean it, show it."**
    - **"Freedom until commitment. Accountability after commitment."**
12. Only at that point was the user correctly told that the product could actually be opened.

### Additional evidentiary point

The system required the Owner to supply the missing completion criterion:

> **If the user cannot open the product, the build is not done.**

The system had enough information and capability to verify this itself:
- the expected public route was known;
- the earlier 404 had already been observed;
- the Render service was connected and discoverable;
- deployment capability was available;
- public readback capability was available.

Nevertheless, it did not carry the execution through to a user-openable surface until the Owner explicitly challenged the completion claim.

This is stronger than a simple missed task continuation. It is evidence of a **completion-definition failure**: internal repository correctness and mergeability were allowed to substitute for the actual user-facing success condition.

### RGR implication for Intake review

This evidence should be assessed against any existing RGR / continuation / execution-completion control for the principle:

**A build whose required user-facing surface cannot be opened and independently read back must not be represented as done.**

The required completion chain for this case was:

`IMPLEMENTED → RECONCILED → DEPLOYED → PUBLICLY OPENABLE → READ BACK → COMPLETE`

Stopping at `IMPLEMENTED`, `RECONCILED`, or `MERGEABLE` was insufficient.

No new governance system is proposed here. Attach this evidence to the existing owner/control if one already governs execution completion and Owner-trigger dependency.
