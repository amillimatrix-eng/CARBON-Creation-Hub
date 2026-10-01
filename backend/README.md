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

No OpenAI/ChatGPT/Codex dependency exists at runtime. Set `AMX_ADMIN_TOKEN` only when authenticated evidence writes are required. Without it, write endpoints fail closed.

The API reads the durable repository state as a local snapshot. `opportunities.json` is treated as the full commercial inventory; `signals.json` and `claims.json` are routing subsets, not an inventory ceiling.
