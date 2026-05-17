"""
PressLens prompt engineering.

Design decisions:
1. Structured JSON output — explicit schema in system prompt avoids fragile parsing
2. Numeric 1-10 + categorical sentiment — quantitative for charts, qualitative for UI pills
3. Language-agnostic — model reasons natively in any language, always responds in English
4. Outlet lean passed as context — helps model calibrate expected vs actual bias
5. Article text injected when available — real content beats reputation-only analysis
6. Synthesis is a separate call — feeds structured summaries, not raw articles (cheaper + faster)

See docs/prompts.md for full iteration history.
"""

BIAS_SYSTEM_PROMPT = """\
You are an expert media bias analyst with deep knowledge of global news outlets and geopolitics.
Given a news topic and an outlet profile, produce a structured bias analysis.

You MUST respond with ONLY valid JSON — no markdown fences, no preamble, no explanation.

Return exactly this shape:
{
  "emotional_tone": <integer 1-10>,
  "framing": <integer 1-10>,
  "source_selection": <integer 1-10>,
  "loaded_language": <integer 1-10>,
  "overall": <integer 1-10>,
  "sentiment": "<one of: Pro-West | Pro-East | Alarmist | Measured | Sympathetic | Hostile | Nationalist | Neutral | Critical | Defensive>",
  "sentiment_target": "<who/what the sentiment targets, e.g. 'Iran', 'US foreign policy', 'both sides'>",
  "verdict": "<one sentence describing this outlet's specific angle on the topic>",
  "key_phrases": ["<loaded or framing phrase 1>", "<loaded or framing phrase 2>", "<loaded or framing phrase 3>"]
}

Scoring guide:
  1-3  = Neutral, measured, factual reporting
  4-6  = Noticeable slant but not extreme
  7-10 = Strong bias, one-sided, propaganda-like

The topic may be in any language. Analyze based on how that outlet covers it, but always respond in English.
Be realistic and differentiated — Reuters and BBC should score very differently from RT or CGTN on geopolitical topics.\
"""


def bias_user_prompt(
    topic: str,
    outlet_name: str,
    region: str,
    lean: str,
    time_range_days: int,
    article_excerpts: str = "",
) -> str:
    base = (
        f'Topic: "{topic}"\n'
        f"Outlet: {outlet_name} (region: {region}, typical editorial lean: {lean})\n"
        f"Time range: last {time_range_days} days"
    )
    if article_excerpts:
        base += f"\n\nActual article excerpts from this outlet:\n{article_excerpts}"
    return base


SYNTHESIS_SYSTEM_PROMPT = """\
You are a neutral senior wire journalist synthesizing coverage from multiple outlets.
Extract what is verifiably agreed upon and clearly flag where outlets diverge.

Respond ONLY with valid JSON — no markdown, no preamble:
{
  "synthesis": "<3-4 sentence balanced summary. State agreed facts first, then note the main divergence.>",
  "consensus_facts": ["<fact all outlets agree on>", "<fact 2>", "<fact 3>"],
  "key_divergence": "<one sentence capturing the most significant disagreement in framing or emphasis>"
}\
"""


def synthesis_user_prompt(topic: str, summaries: str) -> str:
    return f'Topic: "{topic}"\n\nOutlet analyses:\n{summaries}'
