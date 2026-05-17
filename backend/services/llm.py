"""
Provider-agnostic LLM client.

Supports Claude (Anthropic) and GPT-4o mini (OpenAI).
Both return structured JSON parsed into Pydantic models.
"""
from __future__ import annotations

import json
import re
from typing import TypeVar, Type

import httpx
from pydantic import BaseModel

from backend.models.schemas import Provider, BiasScores, Synthesis

T = TypeVar("T", bound=BaseModel)

CLAUDE_MODEL = "claude-haiku-4-5-20251001"
OPENAI_MODEL = "gpt-4o-mini"
MAX_TOKENS = 1000


def _strip_fences(text: str) -> str:
    """Remove markdown code fences that some models add despite instructions."""
    return re.sub(r"```(?:json)?\s*|\s*```", "", text).strip()


def _parse_response(raw: str, model_class: Type[T]) -> T:
    clean = _strip_fences(raw)
    data = json.loads(clean)
    return model_class.model_validate(data)


async def _call_claude(api_key: str, system: str, user: str) -> str:
    async with httpx.AsyncClient(timeout=30) as client:
        res = await client.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
            json={
                "model": CLAUDE_MODEL,
                "max_tokens": MAX_TOKENS,
                "system": system,
                "messages": [{"role": "user", "content": user}],
            },
        )
        res.raise_for_status()
        data = res.json()
        return "".join(b["text"] for b in data["content"] if b["type"] == "text")


async def _call_openai(api_key: str, system: str, user: str) -> str:
    async with httpx.AsyncClient(timeout=30) as client:
        res = await client.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "content-type": "application/json",
            },
            json={
                "model": OPENAI_MODEL,
                "max_tokens": MAX_TOKENS,
                "messages": [
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
            },
        )
        res.raise_for_status()
        data = res.json()
        return data["choices"][0]["message"]["content"]


async def analyze_bias(
    provider: Provider,
    api_key: str,
    system_prompt: str,
    user_prompt: str,
) -> BiasScores:
    caller = _call_claude if provider == "claude" else _call_openai
    raw = await caller(api_key, system_prompt, user_prompt)
    return _parse_response(raw, BiasScores)


async def synthesize(
    provider: Provider,
    api_key: str,
    system_prompt: str,
    user_prompt: str,
) -> Synthesis:
    caller = _call_claude if provider == "claude" else _call_openai
    raw = await caller(api_key, system_prompt, user_prompt)
    return _parse_response(raw, Synthesis)
