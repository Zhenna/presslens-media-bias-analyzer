"""
RSS fetcher.

Fetches each outlet's RSS feed, filters articles by topic keywords,
and returns the top N matching article excerpts.

Uses httpx for async fetching and feedparser for XML parsing.
"""
from __future__ import annotations

import feedparser
import httpx

from backend.core.config import settings


async def fetch_articles(rss_url: str, topic: str, time_range_days: int) -> list[str]:
    """
    Fetch an RSS feed and return article excerpts matching the topic.

    Args:
        rss_url: URL of the outlet's RSS feed
        topic: search topic (any language)
        time_range_days: not used for filtering yet (RSS feeds don't expose reliable dates)

    Returns:
        List of "Headline: ...\nSummary: ..." strings, up to max_articles_per_outlet
    """
    try:
        xml = await _fetch_xml(rss_url)
        articles = _parse_feed(xml)
        matched = _filter_by_topic(articles, topic)
        return matched[: settings.max_articles_per_outlet]
    except Exception:
        # RSS fetch is best-effort — caller falls back to LLM knowledge
        return []


async def _fetch_xml(url: str) -> str:
    headers = {"User-Agent": "PressLens/1.0 (media bias research; github.com/presslens)"}
    async with httpx.AsyncClient(timeout=settings.request_timeout_seconds) as client:
        res = await client.get(url, headers=headers, follow_redirects=True)
        res.raise_for_status()
        return res.text


def _parse_feed(xml: str) -> list[dict]:
    feed = feedparser.parse(xml)
    return [
        {
            "title": entry.get("title", ""),
            "summary": entry.get("summary", ""),
            "content": entry.get("content", [{}])[0].get("value", "") if entry.get("content") else "",
        }
        for entry in feed.entries
    ]


def _filter_by_topic(articles: list[dict], topic: str) -> list[str]:
    """
    Simple keyword filter — checks if any topic keyword appears in title or summary.
    Topic may be in any language; comparison is case-insensitive.
    """
    keywords = [kw.lower() for kw in topic.split() if len(kw) > 2]
    results = []

    for article in articles:
        text = (article["title"] + " " + article["summary"]).lower()
        if any(kw in text for kw in keywords):
            excerpt = f"Headline: {article['title']}\nSummary: {article['summary']}"
            results.append(excerpt)

    return results
