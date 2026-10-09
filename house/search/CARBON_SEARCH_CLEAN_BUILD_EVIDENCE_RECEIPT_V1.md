# CARBON° SEARCH — CLEAN BUILD EVIDENCE RECEIPT V1

**Purpose:** Preserve the original CARBON° Search implementation event as a professional and governance-grade evidence artifact without allowing later UI/copy/package work to rewrite the build record.

## 1. Commissioned baseline

Commissioning / acceptance baseline:
- Repository: `amillimatrix-eng/CARBON-Creation-Hub`
- Commissioned acceptance commit: `519b643b2f49e0b563f8b34f954230834495a3bc`
- Frozen Matrix-grade contract: **35/35 mandatory gates + deployed-runtime readback against the same build/config**
- Build branch: `build/carbon-search-intention-v1`

## 2. Original implementation commit

Original implementation commit:
`7ef32c8bf7eac7e3c6993fbfceac898eb326606f`

Commit message:
`CARBON Search: implement INTENTION V1 core and premium WebGL surface`

Git comparison against the commissioned baseline shows:
- **1 implementation commit**
- **19 changed files**
- **2,203 additions**
- **2 deletions**
- approximately **1,641 backend Search implementation lines**
- **411 Search-specific test lines**
- premium WebGL reference surface, canonical directory, CI/container changes, and integration glue included in the same implementation slice.

## 3. Search-specific acceptance suite

At the original implementation commit:
- `tests/test_carbon_search.py` contains **36 Search-specific test functions**
- The test suite covers the commissioned gates plus API/surface integration checks.
- The Search-specific suite was hardened locally before publication.
- Development history is preserved honestly: the first local behavioral pass exposed **3 defects**; those defects were corrected before the implementation commit was published.
- Therefore the professional claim is **not** “no defect was ever discovered.”
- The stronger evidence-backed claim is:

> **The first committed GitHub CI run of the commissioned implementation passed cleanly after pre-commit local hardening.**

## 4. First committed CI run

GitHub Actions:
- Run: `37938409610`
- Commit: `7ef32c8bf7eac7e3c6993fbfceac898eb326606f`
- Conclusion: **SUCCESS**

Pytest evidence from the CI job log:
- **81 passed**
- **0 failed**
- **1 warning**
- runtime: **1.24s**

The 81 total tests include the **36 Search-specific tests** plus the existing CARBON regression suite.

Additional CI/runtime steps also passed:
- repository smoke test
- Docker build
- provider-neutral container startup
- CARBON backend health readback
- House bootstrap readback
- Search health readback
- Search contract readback
- Search public surface readback
- WebGL2 presence check
- INTELLAGENT surface identity check

Container runtime receipt:
- `container_health: PASS`
- `container_bootstrap: PASS`
- `search_health: PASS`
- `search_surface: PASS`

## 5. First deployment of the clean implementation

Render service:
`carbon-search-intention-v1`

Original deployment:
`dep-db4etmhsrm7s73at92gg`

Exact deployed commit:
`7ef32c8bf7eac7e3c6993fbfceac898eb326606f`

Deploy created:
`2026-10-09T13:40:42.820533Z`

Deploy finished:
`2026-10-09T13:41:33.634031Z`

The deployment later became deactivated only because subsequent successful UI/capability refinements superseded it. Its historical deployment record remains evidence of the clean implementation event.

## 6. Evidence boundary

The following later commits are **post-baseline refinements** and must not rewrite the original build evidence:
- `69834610dfb0945490b5d6f8047c8d99a0f83477` — exposed Evidence / Correct / Confirm / Action controls on the premium public surface.
- `80d42fabe29265eda10b1887edc4bd2f5e7b152f` — opening-copy refinement.

Both later commits also received successful GitHub CI runs.

## 7. Professional-positioning wording

Defensible wording:

> **CARBON° Search was implemented from a frozen commissioning contract in one build branch. The original implementation landed as a single commit containing 36 Search-specific acceptance tests and passed its first committed CI run cleanly: 81/81 repository tests passed, the container/runtime checks passed, and the same commit was deployed. Later UI refinements were kept separate from the original implementation evidence.**

Do not collapse this into “perfect from first keystroke.” The evidence supports a stronger engineering story: defects were found during local hardening, resolved before publication, and the first committed implementation boundary was clean.

## 8. Preservation law

**BASELINE EVIDENCE IS IMMUTABLE.**
Post-build packages may extend CARBON° Search, but they may not:
- change the historical acceptance count;
- rewrite the original commit;
- reclassify local pre-commit defects as if they never happened;
- merge later UI polish into the original implementation event;
- weaken the distinction between Search-specific acceptance and full-repository regression evidence.

This receipt is provenance. Future work builds from it; future work does not overwrite it.
