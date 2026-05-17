# Prompt Engineering Log

This document tracks design decisions and iteration history for PressLens's LLM prompts.

## Design Principles

### 1. Structured JSON output
**Why:** Freeform output requires fragile regex parsing. An explicit schema gives:
- Reliable field extraction into Pydantic models
- Type safety end-to-end (validation catches hallucinated values)
- Easy to extend without breaking the pipeline

**How:** Exact JSON shape specified in the system prompt. Model instructed to return *only* JSON — no markdown fences, no preamble.

### 2. Numeric scores + categorical labels
- Numeric 1–10 scores → charts, sorting, aggregation
- Categorical sentiment (Pro-West, Alarmist, etc.) → instantly readable UI pills

### 3. Language-agnostic input
Topic may be in any language. Model instructed to reason in cultural context but respond in English. No translation layer needed — saves latency and cost.

### 4. Outlet lean as context
Each outlet's typical editorial lean is passed so the model can:
- Calibrate expected vs actual bias
- Produce more nuanced verdicts ("unusually restrained for this outlet")

### 5. Article text injection
When RSS fetching succeeds, actual article excerpts are injected into the prompt. This gives real content-based analysis rather than reputation-only scoring.

### 6. Synthesis as a separate second-stage call
Synthesis receives structured summaries (not raw articles) → shorter input, cheaper, faster. The synthesis model does meta-analysis, not article parsing.

---

## Prompt Version History

### v1 — Freeform
```
Analyze the bias of {outlet} on topic {topic}.
```
**Problem:** Inconsistent format, hard to parse, verbose.

### v2 — JSON schema
Added explicit schema to system prompt.
**Problem:** Model sometimes wrapped output in ```json fences. Added explicit "no markdown" instruction.

### v3 — Sentiment dimension
Added `sentiment` and `sentiment_target` fields.
**Problem:** Model returned out-of-enum values. Added explicit enum list.

### v4 — Scoring guide
Added explicit 1–3 / 4–6 / 7–10 bands so scores are calibrated consistently across calls.

### v5 — Current
- `key_phrases` field added (loaded language examples for UI + explainability)
- Language-agnostic instruction added
- Article excerpts injected when available
- Outlet lean passed as context

---

## Known Limitations

- **Model bias:** Claude and GPT-4o have Western/English-language training biases, likely affecting scores for non-Western outlets.
- **Reproducibility:** Same prompt may give slightly different scores across runs. For research use, consider averaging multiple calls.
- **Knowledge cutoff:** Recent events may be less accurately profiled; real article injection mitigates this.
- **Keyword matching:** RSS filtering uses simple keyword matching; semantic search (embeddings) would improve recall.
