from __future__ import annotations
from typing import Literal, Optional
from pydantic import BaseModel, Field


Provider = Literal["claude", "openai"]

SentimentLabel = Literal[
    "Pro-West", "Pro-East", "Alarmist", "Measured",
    "Sympathetic", "Hostile", "Nationalist", "Neutral",
    "Critical", "Defensive",
]


# ── Request ──────────────────────────────────────────────────────────────────

class AnalyzeRequest(BaseModel):
    topic: str = Field(..., min_length=1, max_length=300, description="News topic in any language")
    outlets: list[str] = Field(..., min_length=2, description="List of outlet IDs to analyze")
    provider: Provider = "claude"
    api_key: str = Field(..., min_length=10)
    time_range_days: int = Field(7, ge=1, le=30)


# ── LLM output ───────────────────────────────────────────────────────────────

class BiasScores(BaseModel):
    emotional_tone: int = Field(..., ge=1, le=10)
    framing: int = Field(..., ge=1, le=10)
    source_selection: int = Field(..., ge=1, le=10)
    loaded_language: int = Field(..., ge=1, le=10)
    political_stance: int = Field(5, ge=1, le=10)  # 1=centrist, 10=extreme
    factual_density: int = Field(5, ge=1, le=10)   # 1=opinion-heavy, 10=highly factual
    overall: int = Field(..., ge=1, le=10)
    sentiment: SentimentLabel
    sentiment_target: str
    verdict: str
    key_phrases: list[str]


class Synthesis(BaseModel):
    synthesis: str
    consensus_facts: list[str]
    key_divergence: str


# ── Outlet config ─────────────────────────────────────────────────────────────

class Outlet(BaseModel):
    id: str
    name: str
    region: str
    lean: str
    language: str
    rss: str


# ── Response ──────────────────────────────────────────────────────────────────

class OutletResult(BaseModel):
    outlet: Outlet
    scores: Optional[BiasScores] = None
    article_count: int = 0
    error: Optional[str] = None


class AnalyzeResponse(BaseModel):
    topic: str
    provider: Provider
    time_range_days: int
    results: list[OutletResult]
    synthesis: Optional[Synthesis] = None
