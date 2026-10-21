# Matrix Critic Release Gate — Recovery Contract (2026-10-21)

## Observed failure
PR #45 merged and was deployed despite zero GitHub reviews, no inline review threads, only a Vercel success status, and no independent proof that the stated backend pytest/container-smoke acceptance had passed before merge. The existing Evidence House test workflow was push/workflow_dispatch-only. MATRIX-CRITIC is canonically CURRENT WHEN INVOKED, but no event-driven review gate was wired to PR release.

## Plan A — intended
1. The backend test workflow runs on relevant pull requests and reports pytest + smoke + container-test status against that PR head.
2. The Matrix Critic gate runs on every opened/updated/reopened/ready PR and every critic-review change.
3. The latest review from the configured independent reviewer must be APPROVED on the exact current PR head and carry:
   - `MATRIX-CRITIC-RESULT: APPROVE`
   - `MATRIX-CRITIC-MANDATE: AMX-MANDATE-MATRIX-CRITIC-V1`
   - `MATRIX-CRITIC-MANDATE-SHA256: <current digest parsed from Blue State>`
   - `MATRIX-CRITIC-REVIEWED-HEAD: <exact current PR head SHA>`
   - `MATRIX-CRITIC-RECEIPT: <durable Root Intake or HTTPS receipt>`
4. An author cannot satisfy the gate by approving their own PR. A later HOLD/CHANGES_REQUESTED or a changed head invalidates the older approval.
5. Branch protection / ruleset must require both `Matrix Critic Release Gate / critic-approval` and `Evidence House Backend Tests / test` where applicable.

## Plan B — temporary fail-closed
Until the independent reviewer identity and required-check settings are verified, the release remains held for Root/T-GOV disposition. Do not treat Vercel deployment success, a drafted review, or an approval of an older commit as a critic pass. Keep the current live service unchanged unless a separate evidence-backed rollback is authorized.

## Configuration dependencies / readback
- Repository variable `MATRIX_CRITIC_REVIEWER`: must be set by the authorized repository/Root owner to the real reviewer identity. It is deliberately not guessed or hard-coded.
- The reviewer must perform the actual mandated evidence-bound critique and submit the required markers in the GitHub review body, including a durable receipt pointer.
- Repository rulesets API returned an empty list at audit time. The branch-protection endpoint returned 403 `Resource not accessible by integration`; actual branch protection settings remain unverified. Required checks must be configured and independently read back by a principal with the needed repository administration permission.

## Status
This branch implements a fail-closed gate and PR-triggered tests. It is not effective against other PRs until merged into `main`, `MATRIX_CRITIC_REVIEWER` is configured, and main's branch protection/ruleset requires the named checks. Do not claim the governance repair complete before those actions and negative/positive acceptance tests are recorded.
