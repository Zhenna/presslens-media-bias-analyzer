# Architecture

## Overview

PressLens is a Python FastAPI backend that serves a lightweight HTML/JS frontend.
All LLM calls and RSS fetching happen server-side — no CORS issues, no key exposure.

```
Browser
  └── POST /api/analyze {topic, outlets, provider, api_key}
        │
        ▼
  FastAPI (backend/main.py)
        │
        ├── rss.py ──── httpx ──────────────► RSS feeds (parallel)
        │
        ├── llm.py ──── httpx ──────────────► Anthropic API
        │           └── httpx ──────────────► OpenAI API
        │
        ├── cache.py ── SQLite ─────────────► presslens.db
        │
        └── analyzer.py (orchestrates all of the above)
```

## Key design decisions

### Server-side LLM calls
API keys go from browser → our FastAPI server → LLM provider.
Keys are never stored — used per-request only.
This avoids CORS issues with OpenAI and keeps the frontend thin.

### Async + concurrent
`asyncio.gather()` runs outlet scoring concurrently.
On 6 outlets: ~3–5s instead of ~18–30s sequential.

### SQLite cache
Simple TTL cache (default 15 min) per (topic, outlet, provider).
Avoids re-scoring the same topic within a session.
Zero infra — just a local .db file.

### RSS best-effort
RSS fetching failures don't break the pipeline — analyzer falls back to
LLM's knowledge of the outlet's coverage patterns. This is documented honestly
in the README as a limitation.

### Provider abstraction
`services/llm.py` presents a single interface — `analyze_bias()` and `synthesize()` —
that works with any provider. Adding a new provider (Gemini, Mistral) means
adding one `_call_*` function and wiring it in.

## API

### `POST /api/analyze`
```json
{
  "topic": "Iran US conflict",
  "outlets": ["bbc", "fox", "aljazeera"],
  "provider": "claude",
  "api_key": "sk-ant-...",
  "time_range_days": 7
}
```

### `GET /api/outlets`
Returns the full outlet registry.

### Auto-generated docs
FastAPI generates interactive docs at `/docs` (Swagger) and `/redoc`.

## Deployment

### Railway (recommended)
```bash
railway login
railway up
```
Set no env vars — users supply their own API keys per request.

### Render
- Build: `pip install -r requirements.txt`
- Start: `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`
