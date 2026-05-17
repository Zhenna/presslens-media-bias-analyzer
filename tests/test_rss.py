"""Tests for RSS fetching and keyword filtering."""
import pytest
import respx
import httpx

from backend.services.rss import fetch_articles, _filter_by_topic


SAMPLE_RSS = """<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <item>
      <title>Iran and US tensions escalate over nuclear deal</title>
      <description>Diplomatic efforts stall as both nations trade accusations.</description>
    </item>
    <item>
      <title>Football World Cup preview</title>
      <description>Teams prepare for the upcoming tournament in Brazil.</description>
    </item>
    <item>
      <title>US imposes new sanctions on Iran over missile programme</title>
      <description>Washington announces fresh economic measures targeting Tehran.</description>
    </item>
  </channel>
</rss>"""


@respx.mock
@pytest.mark.asyncio
async def test_fetch_articles_filters_by_topic():
    """Only articles matching topic keywords are returned."""
    respx.get("https://example-rss.com/feed.xml").mock(
        return_value=httpx.Response(200, text=SAMPLE_RSS)
    )
    articles = await fetch_articles(
        rss_url="https://example-rss.com/feed.xml",
        topic="Iran US tensions",
        time_range_days=7,
    )
    assert len(articles) == 2
    assert all("Iran" in a or "US" in a for a in articles)


@respx.mock
@pytest.mark.asyncio
async def test_fetch_articles_returns_empty_on_error():
    """RSS fetch failure returns empty list instead of raising."""
    respx.get("https://example-rss.com/feed.xml").mock(
        return_value=httpx.Response(500)
    )
    articles = await fetch_articles(
        rss_url="https://example-rss.com/feed.xml",
        topic="Iran",
        time_range_days=7,
    )
    assert articles == []


def test_filter_by_topic_multilingual():
    """Keyword filter works for short English terms that appear in any language text."""
    articles = [
        {"title": "台湾 Taiwan strait tensions", "summary": "US navy patrol", "content": ""},
        {"title": "Football news", "summary": "Premier League results", "content": ""},
    ]
    results = _filter_by_topic(articles, "Taiwan")
    assert len(results) == 1
    assert "Taiwan" in results[0]
