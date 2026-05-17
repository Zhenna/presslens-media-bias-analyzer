"""
Tests for the bias analysis pipeline.

Uses respx to mock httpx calls so no real API keys are needed.
"""
import json
import pytest
import respx
import httpx

from backend.models.schemas import AnalyzeRequest, BiasScores
from backend.services import analyzer, llm


MOCK_SCORES = {
    "emotional_tone": 6,
    "framing": 7,
    "source_selection": 5,
    "loaded_language": 6,
    "overall": 6,
    "sentiment": "Pro-West",
    "sentiment_target": "US policy",
    "verdict": "Frames the conflict through a Western security lens.",
    "key_phrases": ["rogue state", "unprovoked aggression", "allied forces"],
}

MOCK_SYNTHESIS = {
    "synthesis": "Most outlets agree on the basic timeline of events. Western outlets emphasize Iranian aggression while state-backed media frames the US as the provocateur.",
    "consensus_facts": ["Conflict began on March 3", "Both sides reported casualties", "UN called for ceasefire"],
    "key_divergence": "Western outlets attribute blame to Iran; RT and CGTN attribute blame to US sanctions.",
}


@pytest.fixture
def analyze_request():
    return AnalyzeRequest(
        topic="Iran US conflict",
        outlets=["bbc", "reuters"],
        provider="claude",
        api_key="sk-ant-test-key",
        time_range_days=7,
    )


@respx.mock
@pytest.mark.asyncio
async def test_analyze_bias_claude(analyze_request):
    """LLM client parses Claude response into BiasScores correctly."""
    respx.post("https://api.anthropic.com/v1/messages").mock(
        return_value=httpx.Response(
            200,
            json={"content": [{"type": "text", "text": json.dumps(MOCK_SCORES)}]},
        )
    )
    scores = await llm.analyze_bias(
        provider="claude",
        api_key="sk-ant-test",
        system_prompt="system",
        user_prompt="user",
    )
    assert isinstance(scores, BiasScores)
    assert scores.overall == 6
    assert scores.sentiment == "Pro-West"


@respx.mock
@pytest.mark.asyncio
async def test_analyze_bias_openai(analyze_request):
    """LLM client parses OpenAI response into BiasScores correctly."""
    respx.post("https://api.openai.com/v1/chat/completions").mock(
        return_value=httpx.Response(
            200,
            json={"choices": [{"message": {"content": json.dumps(MOCK_SCORES)}}]},
        )
    )
    scores = await llm.analyze_bias(
        provider="openai",
        api_key="sk-test",
        system_prompt="system",
        user_prompt="user",
    )
    assert scores.emotional_tone == 6
    assert scores.sentiment_target == "US policy"


@respx.mock
@pytest.mark.asyncio
async def test_full_pipeline(analyze_request):
    """Full pipeline returns AnalyzeResponse with results + synthesis."""
    # Mock Claude for all calls (bias + synthesis)
    respx.post("https://api.anthropic.com/v1/messages").mock(
        side_effect=[
            httpx.Response(200, json={"content": [{"type": "text", "text": json.dumps(MOCK_SCORES)}]}),
            httpx.Response(200, json={"content": [{"type": "text", "text": json.dumps(MOCK_SCORES)}]}),
            httpx.Response(200, json={"content": [{"type": "text", "text": json.dumps(MOCK_SYNTHESIS)}]}),
        ]
    )
    # Mock RSS feeds to return empty (best-effort)
    respx.get(url__regex=r".*\.xml.*").mock(return_value=httpx.Response(200, text="<rss></rss>"))

    response = await analyzer.run_analysis(analyze_request)

    assert response.topic == "Iran US conflict"
    assert len(response.results) == 2
    assert response.synthesis is not None
    assert len(response.synthesis.consensus_facts) == 3


def test_scores_validation():
    """Pydantic rejects out-of-range scores."""
    import pytest
    from pydantic import ValidationError
    with pytest.raises(ValidationError):
        BiasScores(
            emotional_tone=11,  # > 10, should fail
            framing=5, source_selection=5, loaded_language=5, overall=5,
            sentiment="Neutral", sentiment_target="both",
            verdict="test", key_phrases=[],
        )
