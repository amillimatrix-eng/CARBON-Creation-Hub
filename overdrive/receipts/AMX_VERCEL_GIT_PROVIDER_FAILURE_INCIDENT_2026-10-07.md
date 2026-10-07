# AMX VERCEL GIT-PROVIDER FAILURE — INCIDENT / QUEUE TRAINING RECEIPT

Date: 2026-10-07
Status: VERIFIED DEPENDENCY FAILURE / NO BLIND RETRY
Owner priority: P0 — stop repeated crash/failure behavior.

Owner screenshot reports Vercel preview deployment failure for project `carbon`, branch `carbon-degree-v1-20261007`, commit `731f381`: `Git provider error — A GitHub account is not connected to this Vercel account`.

Direct verification:
- repo `amillimatrix-eng/CARBON-Creation-Hub` reachable/writable;
- branch `carbon-degree-v1-20261007` exists;
- commit `731f3810cee52d35e3115b91abc2ee837f6de820` exists;
- Vercel team `team_K33bfqACbTVPQbJ89enBU4x2` visible;
- Vercel git context reports no linked projects;
- repo-linked project query returns none;
- connector project-link/create attempt returns 403 forbidden.

Classification:
`SOURCE VALID + DEPLOYMENT TRANSPORT BINDING MISSING`

Queue rule:
1. classify `DEPENDENCY_GATE — GIT_PROVIDER_BINDING`;
2. no unchanged Vercel retries while binding state is unchanged;
3. preserve branch/commit/failure evidence;
4. continue work not dependent on Vercel;
5. reattempt only after GitHub↔Vercel binding/project permission is positively verified;
6. a Vercel `Git provider error` is not source-code crash evidence.

Owner gate:
Authenticated Vercel account surface must authorize/connect GitHub `amillimatrix-eng` to the intended team/project, then return for preview-deployment readback.

Root Handoff SHA-256: `622392d94057d6979cf7d7fe19dd87dcd7831da123c1ab90b0dc72b014081320`.

NO RECEIPT → NO CLOSURE.
