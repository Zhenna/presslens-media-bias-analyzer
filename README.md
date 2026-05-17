# 🔍 PressLens — Media Bias Analyzer

> AI-powered media bias analyzer that compares coverage across global news outlets and synthesizes a neutral summary — powered by Claude or OpenAI.

Every outlet tells a different story. PressLens takes any news topic, pulls coverage from major global press across regions and languages, and uses large language models to score each outlet on emotional tone, framing, source selection, and loaded language. The result: a side-by-side bias comparison table, a superimposed spider chart, and a balanced synthesis that cuts through the spin.

Please [follow my blog](https://medium.com/@luzhenna) and learn how to use it. 

---

## ✨ Features

- **Multi-outlet comparison** — 12+ outlets across US, UK, Middle East, Russia, China, Europe, India, Latin America
- **Multi-dimensional bias scoring** — emotional tone, framing, source selection, loaded language (1–10)
- **Sentiment labeling** — directional label per outlet (Pro-West, Alarmist, Nationalist, Measured…)
- **Superimposed spider chart** — all outlets on one radar, toggle visibility per outlet
- **Neutral synthesis** — LLM-generated balanced summary from all polarized sources
- **Demo mode** — 3 pre-analyzed topics (Iran US conflict, Taiwan strait, Ukraine Russia war) — no API key needed
- **Multilingual** — topic input in any language; models reason natively across Arabic, Chinese, French, German…
- **Provider-agnostic** — Claude (Anthropic) or GPT-4o mini (OpenAI); your key, your cost

---

## 🏗️ Architecture

```
presslens-media-bias-analyzer/
├── backend/
│   ├── main.py              FastAPI app, serves frontend + API
│   ├── api/routes.py        POST /analyze, GET /outlets, GET /demo/*
│   ├── core/
│   │   ├── config.py        Outlet registry (12 outlets)
│   │   └── prompts.py       LLM prompts (documented with version history)
│   ├── models/schemas.py    Pydantic models
│   └── services/
│       ├── llm.py           Provider-agnostic Claude + OpenAI client
│       ├── rss.py           Async RSS fetcher + keyword filter
│       ├── analyzer.py      Pipeline orchestrator (async/concurrent)
│       ├── cache.py         SQLite TTL cache
│       └── demo_cache.py    Pre-computed demo results (no LLM calls)
├── frontend/src/
│   ├── index.html           Single-page app (Medium-style UI)
│   └── logo.svg             Prism logo mark (also used as favicon)
├── tests/
├── docs/
├── Dockerfile
├── railway.toml
└── render.yaml
```

---

## 🚀 Local development

```bash
git clone https://github.com/yourusername/presslens-media-bias-analyzer
cd presslens-media-bias-analyzer

python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate

pip install -r requirements.txt

uvicorn backend.main:app --reload
# → http://localhost:8000
```

---

## 🚢 Deploy to Railway (free public URL)

Railway gives you a live URL like `presslens-production.up.railway.app` in under 2 minutes.

```bash
# Install Railway CLI
npm i -g @railway/cli

# Login and deploy
railway login
railway init          # select "Empty project"
railway up
```

Railway auto-detects the `Dockerfile` and deploys it. Your app is live at the URL shown in the dashboard.

**Free tier:** 500 hours/month. App sleeps after inactivity, wakes in ~5 seconds.

---

## 🐳 Docker (run anywhere)

```bash
# Build
docker build -t presslens .

# Run
docker run -p 8000:8000 presslens
# → http://localhost:8000
```

The container includes everything — no environment variables needed. Users supply their own API keys through the UI.

---

## 🧩 Deploy to Render (alternative)

Connect your GitHub repo at [render.com](https://render.com) — the `render.yaml` configures everything automatically.

---

## 🧪 Tests

```bash
pytest tests/ -v
```

Tests use `respx` to mock HTTP calls — no real API keys needed.

---

## 💰 Cost per analysis

| Model | Cost (6 outlets + synthesis) |
|---|---|
| Claude Haiku | ~$0.05 |
| GPT-4o mini | ~$0.01 |

Users supply their own API keys — zero LLM cost for the host.

---

## 💡 Prompt engineering

See [`docs/prompts.md`](docs/prompts.md) for the full prompt design, iteration history, and decisions — including why structured JSON output beats freeform for bias scoring.

---

## ⚠️ Limitations

- LLMs carry their own biases; results are a starting point for critical reading, not ground truth
- Without real-time RSS, analysis draws on LLM knowledge of outlet coverage patterns — real article injection improves accuracy
- Very recent events may be less accurately profiled due to training cutoffs

---

## 📄 License
MIT
