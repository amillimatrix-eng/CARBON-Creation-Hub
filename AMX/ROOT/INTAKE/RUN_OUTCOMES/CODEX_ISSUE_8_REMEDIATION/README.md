# Issue #8 — implemented remediation and Root handoff

Authority: [CODEX DIRECTIVE — Lean Egg Security + Revenue Run](https://github.com/amillimatrix-eng/CARBON-Creation-Hub/issues/8).
Repository: `amillimatrix-eng/CARBON-Creation-Hub`; deployment branch: `main`.
Original validated local commit: `5f8d918fce9db73a422ea9984c9606a5939c9a8c`.
Remote implementation commit: `407f1c13ae72991e116472aff8b1eb2b2ad177f1`.

The implementations are in their existing repository paths, listed below. This folder contains the handoff and validation record; it does not create another Matrix, worker, queue, CRM or commercial writer. `C:\LIB\AMX` and `/mnt/c/LIB/AMX` were not touched.

## What changed and why

| Failure | Implemented source | Result and proving tests |
| --- | --- | --- |
| Any evidence could promote a receivable to PAID; projections trusted the label | `overdrive/payment_truth.py`, `overdrive/runner.py`, `backend/state.py`, `backend/app.py` | Fail-closed, independently verified bank/provider/chain settlement; matched opportunity, payer, payee, currency and receivable amount. `tests/test_lean_egg.py::PaymentTruth` proves rejection and valid settlement. Synthetic test settlements are not money received. |
| BLACK recorded failed exits/timeouts as RESOLVED and treated receipt existence as permanent completion | `BLACK/worker.py` | Truthful failure/timeout; opt-in bounded retry; immutable historical and numbered attempt receipts with task and predecessor hashes. `BlackTruth` proves timeout, retry exhaustion, preserved historical failure and attributable later success. |
| Static mounting exposed the proposal registry/configuration; version history and operator reads bypassed privacy | `backend/app.py`, `backend/store.py`; deleted `house/remediation/proposals.json` | Explicit public evidence visibility, asset allowlist, admin-protected private reads, private runtime proposal registry, disabled portal by default. `ExposureAndIntake` proves the original exposure routes deny access. Historical published portal tokens must never be reused. |
| Customer change/callback intake only appended anonymous receipts and did not create a deduped PRI obligation | `backend/app.py`, `overdrive/runner.py` | Stable deduped request ID; verified customer/opportunity/thread association; existing PRI claim with a private request endpoint pointer. Raw message/contact/token material is excluded from shared claims. Closure requires attributable action evidence in the original thread. `CommercialTruth` and `ExposureAndIntake` prove this progression. |
| HOLD or blocked work could appear READY and obscure nearer money | `overdrive/runner.py` | Full-ledger classification, WAITING versus executable work, cash-first ordering, thread continuity and a smallest next action. `CommercialTruth` plus the existing routing tests prove blocked items do not idle unrelated work. |

Ownership is unchanged: iSCOPE discovers/verifies/dedupes/qualifies/hands off; PRI progresses and converts after handoff; iSCOPE PRI Field Force remains the sole commercial writer; OVERDRIVE transports evidence and obligations. No Gmail/browser action or payment was fabricated.

## Root's remaining deployment actions

1. Recover this change from `main` after its PR is merged. On BLACK use the existing `/home/amx/amx-black` checkout, inspect `git status` and preserve unrelated modifications before updating. Use the existing worker/service; verify its running code and subsequent attributable receipts. Do not launch another broad Codex sweep or replay the issue #8 Codex job merely to recheck these fixes.
2. Provision private runtime controls described in `backend/README.md`. The optional portal remains disabled until `AMX_PROPOSAL_REGISTRY_PATH` references a registry outside the repository with fresh random tokens and correct PRI customer/opportunity/thread associations. Keep proposal/customer secrets out of GitHub.
3. Place `AMX_CUSTOMER_REQUEST_PATH` on existing shared private durable storage accessible to the backend and current OVERDRIVE executor. The authorized commercial writer retrieves full requests through `/api/customer-requests/{request_id}` using its existing admin credential. Confirm a real request reaches one nonterminal PRI claim; do not infer action from intake alone.
4. Configure `AMX_PAYMENT_VERIFICATION_KEY` only for the authorized independent settlement verifier and validation consumers. The verifier must first read actual bank/provider/chain evidence; never sign an email, invoice, dashboard label or internal receipt as settlement. Provision the receivable's exact payer/payee/currency/amount facts. Do not publish this key or payment/customer secrets in a receipt or repository file.
5. For a known retry-safe failed BLACK job, explicitly authorize `max_attempts` of 2 or 3; `retry_delay_seconds` is bounded to 10–3600 seconds. Historical maintenance jobs default to one attempt to avoid automatically replaying potentially non-idempotent commands. Changing retry policy preserves instruction identity; changed execution instructions require a new job ID.

These are deployment/configuration checks for existing components, not authorization to create additional infrastructure or to spend money. Existing provider-enforced authentication/identity steps must be completed through their authorized executor. Continue unrelated executable opportunities while a particular provider blocks.

## Reproduce the targeted validation

With the repository's existing development requirements available:

```bash
python -m pytest -q tests/test_lean_egg.py tests/test_overdrive_claims.py tests/test_backend.py tests/test_customer_portal.py tests/test_frontend_contract.py
python tests/smoke.py
git diff --check
git status --short
```

`VALIDATION.json` records the completed run and the tested file hashes. In the managed sandbox pytest was unavailable, so the actual test methods/functions ran through a temporary unittest/direct-fixture harness. The sandbox required bounded epoll waits in that test process to wake cross-thread requests; production code was not changed for this workaround. FastAPI/HTTPX routes, authentication dependencies, file persistence and response assertions were exercised; external payments and Git execution in worker unit tests used explicit fixtures/mocks.

## Publication diagnosis and truthful limits

Authenticated GitHub read/write access worked. Shell Git could not connect to the managed environment's proxy. Non-forced API updates of `main` raced with the existing OVERDRIVE minute-tick commits and were rejected as non-fast-forward. The resolution is a stable remediation branch and GitHub's server-side PR merge, preserving concurrent Matrix state rather than force-updating `main` or creating another control plane.

Source tests are not evidence of BLACK deployment, public-host deployment, customer action or realized revenue. No verified payment evidence was recovered or created in this run.

EGG NOT BROKEN — NO VERIFIED PAYMENT EVIDENCE
