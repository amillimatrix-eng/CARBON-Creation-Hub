# CODEX COMMISSIONING ORDER — MATRIX → BLACK → CODEX → RECEIPT

work_order_id: BLACK-CODEX-REMOTE-BRIDGE-COMMISSION-20261004-002
date: 2026-10-04
authority: Owner-directed / Root handoff
target: BLACK local authenticated Codex
status: READY_FOR_LOCAL_CODEX_EXECUTION
live_reaper_mutation: NOT AUTHORIZED

## Objective

Establish and prove the existing durable remote execution chain:

MATRIX -> GitHub main -> BLACK/jobs/*.json -> BLACK worker -> authenticated Codex -> material result -> BLACK/receipts/*.json -> GitHub main -> Matrix readback.

Do not invent a second transport if the existing one can be repaired.

## Known current facts

- Authoritative repository: amillimatrix-eng/CARBON-Creation-Hub
- BLACK repo root on the worker is the repository containing BLACK/worker.py.
- Current BLACK worker polls BLACK/jobs/*.json and writes BLACK/receipts/<job>.json.
- Codex CLI 0.160.0 has been installed on BLACK.
- Owner completed supported device authentication.
- A substantial authenticated local Codex sweep has already completed successfully.
- Therefore Codex installation and human authentication are not the current primary gate.
- The remote round trip remains unproven.
- Existing queued preflight with no receipt:
  BLACK/jobs/BLACK-CODEX-REMOTE-BRIDGE-PREFLIGHT-20261004-001.json
- Current diagnostic also queued:
  BLACK/jobs/BLACK-CODEX-PATH-DIAG-20261004-001.json
- Do not treat queue presence as execution proof.

## First action — inspect, do not guess

From the current local clone:

1. git status
2. git remote -v
3. git fetch origin main
4. inspect BLACK/worker.py
5. inspect the two queued Codex jobs above
6. inspect latest BLACK receipts and service state
7. confirm current Codex binary/path/version and current authenticated state without printing credentials/tokens
8. determine why the queued jobs are not producing receipts

Do not reinstall Codex and do not reauthenticate unless current evidence proves authentication was actually lost.

## Important worker defect already observed

Current BLACK/worker.py records state "RESOLVED" regardless of command exit code.

That can create false completion.

If this defect affects safe bridge commissioning, make the smallest tested repair so non-zero/timed-out jobs are not represented as successful completion and can be retried/recovered without duplicate execution. Preserve prior receipts as provenance.

Do not redesign BLACK.

## Remote invocation requirement

Use the installed Codex's supported non-interactive execution path if available (for example the locally supported `codex exec` form discovered from the installed CLI).

Do not assume current upstream flags match version 0.160.0. Inspect the installed binary's help first.

The first Codex remote invocation must be READ ONLY.

It should prove that Codex can:
- run from a BLACK job;
- identify the repository root;
- read CONTINUITY.md;
- read BLACK/worker.py;
- read the current commit SHA;
- return a concise final result;
- allow BLACK to persist and push the receipt.

No source mutation in this proof.

## Acceptance test

PASS only when a fresh job created from GitHub is observed by BLACK and produces a durable receipt showing:

- BLACK job id;
- Codex invocation actually occurred;
- Codex exit code = 0;
- repository identity = amillimatrix-eng/CARBON-Creation-Hub;
- expected read-only facts were returned;
- receipt committed/pushed to GitHub;
- Matrix can read the receipt back from GitHub.

A local Codex task alone is not PASS.
A queued job alone is not PASS.
A BLACK receipt that never invoked Codex is not PASS.

## After bridge PASS

Only after the remote Codex round trip is proven, read and execute the governed Reaper experiment inputs on main:

1. AMX/ROOT/INTAKE/ROOT-20261004-2030-001_BLUE_STATE_CANDIDATE_BOUNDARY_REAPER_ADAPTIVE_INTERROGATION.md
2. AMX/ROOT/INTAKE/ROOT-20261004-2030-002_CODEX_WORK_ORDER_BOUNDARY_REAPER_HARNESS.md

The Reaper work remains a contained experimental harness.
Do not modify the live Reaper merely because the bridge works.
Do not merge the Blue-State candidate without its test gate.

## Required receipt

Persist:
- diagnosis;
- exact files changed, if any;
- tests;
- bridge proof job id;
- resulting BLACK receipt path;
- commit SHA(s);
- remaining unproven items.

Terminal classification:
BRIDGE_PASS / BRIDGE_ITERATE / BRIDGE_HOLD

NO RECEIPT -> NO CLOSURE.
