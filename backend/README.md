# AMilliMATRiX Evidence + House Control Backend

Provider-neutral runtime for evidence retrieval and House current-state projection. It does not require an AI model or API key.

## Local

```bash
python -m venv .venv
. .venv/bin/activate
pip install -r requirements-dev.txt
uvicorn backend.app:app --reload
```

House: `http://127.0.0.1:8000/house`
Health: `http://127.0.0.1:8000/api/health`

## Tests

```bash
pytest -q
```

## Docker

```bash
docker build -t amx-evidence-house .
docker run --rm -p 8000:8000 -v amx-evidence-data:/app/data amx-evidence-house
```

No OpenAI/ChatGPT/Codex dependency exists at runtime. Set `AMX_ADMIN_TOKEN` for authorized private reads and evidence writes. Without it, those endpoints fail closed.

The API reads the durable repository state as a local snapshot. `opportunities.json` is treated as the full commercial inventory; `signals.json` and `claims.json` are routing subsets, not an inventory ceiling.

Issue #8 runtime controls:

- Operator state, opportunity reads, T10 operator data, evidence version history and customer-request details require the existing `X-AMX-Admin` credential. Public evidence requires explicit `HOUSE` or `PUBLIC` visibility. Only named CSS/JS assets are served; private registries and arbitrary configuration files are excluded.
- The optional customer portal is disabled unless `AMX_PROPOSAL_REGISTRY_PATH` points outside this repository to a private runtime registry. Published historical portal tokens must be replaced with fresh random tokens. Each configured proposal must carry `opportunity_key`, `customer_id` and the existing PRI-owned `thread_id`. Requests with unverified associations are rejected.
- Persist `AMX_CUSTOMER_REQUEST_PATH` on shared private durable storage accessible to the existing backend and OVERDRIVE executor. It defaults to `data/proposal_requests.jsonl`. Identical normalized requests reuse one ID; OVERDRIVE reconciles them into existing PRI claims. Shared claims contain the private endpoint pointer, not customer messages, contact details or bearer tokens. The sole commercial writer retrieves details at `/api/customer-requests/{request_id}` with its admin credential. An internal completion label does not close a request: `action_evidence` must identify the actual action/closure and original thread.
- Payment settlement attestations use the runtime-only `AMX_PAYMENT_VERIFICATION_KEY` (at least 32 characters). Only the authorized independent bank/provider/chain verifier may use that key. It signs the canonical JSON settlement facts described in `overdrive/payment_truth.py` with HMAC-SHA256, excluding `verification_hmac` itself. Never sign an email, invoice or internal receipt as a settlement. The receivable must specify `amount_due`, `currency`, `payer_id` and `payee_account`; settlement must match the opportunity and cover the amount. Missing verifier configuration fails closed. This repository neither fabricates settlements nor implements a new payment provider.
- BLACK shell jobs opt into retries with `max_attempts` (1–3, default 1) and `retry_delay_seconds` (10–3600, default 60). Historical maintenance jobs retain single-attempt behavior unless explicitly authorized for replay. Failure/timeout is never successful resolution; each retry has an immutable numbered receipt, task hash and predecessor hash. Changed instructions require a new job ID. Prior receipts remain intact.

Existing private registries, verifier secrets, authenticated provider sessions and shared durable storage must be provisioned in their authorized runtime. Repository changes alone do not prove deployment, a customer response or money received.

## Optional live state adapter

Set `AMX_GITHUB_REPO`, `AMX_GITHUB_REF`, and (for a private repository) `AMX_GITHUB_TOKEN` to let the control projection refresh current durable JSON state from GitHub. If live reads fail, the API labels the state as a local fallback/degraded source rather than pretending it is live.
