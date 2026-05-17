from fastapi import APIRouter, HTTPException

from backend.core.config import OUTLETS
from backend.models.schemas import AnalyzeRequest, AnalyzeResponse, Outlet
from backend.services.analyzer import run_analysis
from backend.services.demo_cache import get_demo, list_demo_topics

router = APIRouter()


@router.get("/outlets", response_model=list[Outlet])
async def list_outlets():
    """Return all supported outlets."""
    return OUTLETS


@router.get("/demo/topics", response_model=list[str])
async def demo_topics():
    """Return list of pre-cached demo topic names."""
    return list_demo_topics()


@router.get("/demo/{topic}", response_model=AnalyzeResponse)
async def demo_result(topic: str):
    """
    Return a pre-cached analysis result for a demo topic.
    No API key required — for unauthenticated visitors.
    """
    result = get_demo(topic)
    if not result:
        raise HTTPException(status_code=404, detail=f"No demo available for topic: '{topic}'")
    return result


@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze(req: AnalyzeRequest):
    """
    Run live bias analysis for a topic across selected outlets.
    The user's API key is used directly for LLM calls and never stored.
    Falls back to demo cache if topic matches and no key provided.
    """
    unknown = [oid for oid in req.outlets if oid not in {o.id for o in OUTLETS}]
    if unknown:
        raise HTTPException(status_code=422, detail=f"Unknown outlet IDs: {unknown}")

    demo = get_demo(req.topic)
    if demo and not req.api_key:
        return demo

    try:
        return await run_analysis(req)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
