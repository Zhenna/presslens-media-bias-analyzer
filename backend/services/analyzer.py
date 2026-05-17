"""
Bias analysis pipeline.

Orchestrates:
1. Parallel RSS fetching per outlet
2. Concurrent LLM bias scoring (with cache check)
3. LLM synthesis of all results
"""
from __future__ import annotations

import asyncio

from backend.core.config import OUTLET_MAP
from backend.core.prompts import (
    BIAS_SYSTEM_PROMPT,
    SYNTHESIS_SYSTEM_PROMPT,
    bias_user_prompt,
    synthesis_user_prompt,
)
from backend.models.schemas import (
    AnalyzeRequest,
    AnalyzeResponse,
    OutletResult,
    Synthesis,
)
from backend.services import cache, llm, rss


async def run_analysis(req: AnalyzeRequest) -> AnalyzeResponse:
    """Full pipeline: fetch articles → score bias → synthesize."""

    outlets = [OUTLET_MAP[oid] for oid in req.outlets if oid in OUTLET_MAP]

    # Step 1: Fetch articles for all outlets in parallel
    article_tasks = [
        rss.fetch_articles(outlet.rss, req.topic, req.time_range_days)
        for outlet in outlets
    ]
    all_articles = await asyncio.gather(*article_tasks)

    # Step 2: Score each outlet concurrently
    score_tasks = [
        _score_outlet(req, outlet, articles)
        for outlet, articles in zip(outlets, all_articles)
    ]
    results: list[OutletResult] = await asyncio.gather(*score_tasks)

    # Step 3: Synthesize
    synthesis = await _synthesize(req, results)

    return AnalyzeResponse(
        topic=req.topic,
        provider=req.provider,
        time_range_days=req.time_range_days,
        results=results,
        synthesis=synthesis,
    )


async def _score_outlet(
    req: AnalyzeRequest,
    outlet,
    articles: list[str],
) -> OutletResult:
    # Cache check
    cached = cache.get_cached(req.topic, outlet.id, req.provider)
    if cached:
        return OutletResult(outlet=outlet, scores=cached, article_count=len(articles))

    try:
        article_text = "\n\n".join(articles)
        user_prompt = bias_user_prompt(
            topic=req.topic,
            outlet_name=outlet.name,
            region=outlet.region,
            lean=outlet.lean,
            time_range_days=req.time_range_days,
            article_excerpts=article_text,
        )
        scores = await llm.analyze_bias(
            provider=req.provider,
            api_key=req.api_key,
            system_prompt=BIAS_SYSTEM_PROMPT,
            user_prompt=user_prompt,
        )
        cache.set_cached(req.topic, outlet.id, req.provider, scores)
        return OutletResult(outlet=outlet, scores=scores, article_count=len(articles))

    except Exception as e:
        return OutletResult(outlet=outlet, scores=None, error=str(e))


async def _synthesize(
    req: AnalyzeRequest,
    results: list[OutletResult],
) -> Synthesis | None:
    valid = [r for r in results if r.scores]
    if not valid:
        return None

    summaries = "\n".join(
        f"{r.outlet.name}: overall {r.scores.overall}/10, "  # type: ignore[union-attr]
        f"sentiment: {r.scores.sentiment} toward {r.scores.sentiment_target}. "  # type: ignore[union-attr]
        f"{r.scores.verdict}"  # type: ignore[union-attr]
        for r in valid
    )

    try:
        return await llm.synthesize(
            provider=req.provider,
            api_key=req.api_key,
            system_prompt=SYNTHESIS_SYSTEM_PROMPT,
            user_prompt=synthesis_user_prompt(req.topic, summaries),
        )
    except Exception:
        return None
