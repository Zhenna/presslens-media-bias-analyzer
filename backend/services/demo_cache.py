"""
Demo cache — pre-computed analysis results for popular topics.
Served instantly without any LLM calls, enabling demo mode for unauthenticated users.
"""
from backend.models.schemas import BiasScores, Synthesis, OutletResult, AnalyzeResponse
from backend.core.config import OUTLET_MAP

def _outlet(id): return OUTLET_MAP[id]

DEMO_TOPICS = {
    "iran us conflict": AnalyzeResponse(
        topic="Iran US Conflict",
        provider="claude",
        time_range_days=7,
        results=[
            OutletResult(outlet=_outlet("nyt"), article_count=3, scores=BiasScores(
                emotional_tone=5, framing=6, source_selection=5, loaded_language=5, political_stance=5, factual_density=6, overall=6,
                sentiment="Pro-West", sentiment_target="US foreign policy",
                verdict="Frames Iran as the primary aggressor while questioning effectiveness of US sanctions strategy.",
                key_phrases=["nuclear brinkmanship", "rogue regime", "destabilising influence"])),
            OutletResult(outlet=_outlet("fox"), article_count=2, scores=BiasScores(
                emotional_tone=7, framing=8, source_selection=6, loaded_language=7, political_stance=5, factual_density=6, overall=7,
                sentiment="Hostile", sentiment_target="Iran",
                verdict="Strongly anti-Iran framing, emphasising military threat and calling for decisive US action.",
                key_phrases=["terrorist state", "existential threat", "axis of evil"])),
            OutletResult(outlet=_outlet("bbc"), article_count=3, scores=BiasScores(
                emotional_tone=3, framing=3, source_selection=2, loaded_language=3, political_stance=5, factual_density=6, overall=3,
                sentiment="Measured", sentiment_target="both sides",
                verdict="Balanced coverage citing both Iranian and US official positions with minimal editorialising.",
                key_phrases=["diplomatic channels", "both sides", "international community"])),
            OutletResult(outlet=_outlet("aljazeera"), article_count=3, scores=BiasScores(
                emotional_tone=7, framing=8, source_selection=6, loaded_language=7, political_stance=5, factual_density=6, overall=7,
                sentiment="Critical", sentiment_target="US foreign policy",
                verdict="Frames US sanctions as collective punishment, giving prominence to Iranian civilian perspectives.",
                key_phrases=["illegal sanctions", "US aggression", "collective punishment"])),
            OutletResult(outlet=_outlet("reuters"), article_count=3, scores=BiasScores(
                emotional_tone=2, framing=2, source_selection=2, loaded_language=2, political_stance=5, factual_density=6, overall=2,
                sentiment="Neutral", sentiment_target="events",
                verdict="Wire-service neutrality: factual reporting on troop movements, diplomatic statements, and UN responses.",
                key_phrases=["officials said", "according to", "both governments"])),
            OutletResult(outlet=_outlet("guardian"), article_count=2, scores=BiasScores(
                emotional_tone=5, framing=6, source_selection=5, loaded_language=5, political_stance=5, factual_density=6, overall=5,
                sentiment="Critical", sentiment_target="US and Iran hardliners",
                verdict="Critical of hawkish positions on both sides, emphasising diplomatic solutions and civilian impact.",
                key_phrases=["diplomatic failure", "civilian toll", "hardline factions"])),
        ],
        synthesis=Synthesis(
            synthesis="All outlets confirm that diplomatic negotiations have stalled and military posturing has increased on both sides. Western outlets emphasise Iranian nuclear ambitions as the core issue, while Al Jazeera and non-Western sources frame US economic sanctions as the primary driver of escalation. Reuters and BBC provide the most factual accounts, while Fox News and Al Jazeera represent the strongest opposing narrative poles.",
            consensus_facts=["Diplomatic talks collapsed in March", "Both sides increased military presence in the Gulf", "UN Security Council convened emergency session"],
            key_divergence="Western outlets attribute responsibility to Iran's nuclear programme; Al Jazeera and regional press attribute escalation to US sanctions and military encirclement."
        )
    ),

    "taiwan strait": AnalyzeResponse(
        topic="Taiwan Strait",
        provider="claude",
        time_range_days=7,
        results=[
            OutletResult(outlet=_outlet("nyt"), article_count=3, scores=BiasScores(
                emotional_tone=5, framing=6, source_selection=5, loaded_language=5, political_stance=5, factual_density=6, overall=6,
                sentiment="Pro-West", sentiment_target="China",
                verdict="Frames Chinese military exercises as coercive intimidation threatening a democratic neighbour.",
                key_phrases=["authoritarian aggression", "democratic Taiwan", "cross-strait tensions"])),
            OutletResult(outlet=_outlet("cgtn"), article_count=3, scores=BiasScores(
                emotional_tone=6, framing=8, source_selection=6, loaded_language=7, political_stance=5, factual_density=6, overall=7,
                sentiment="Nationalist", sentiment_target="US and Taiwan independence",
                verdict="Presents exercises as legitimate responses to US interference in Chinese internal affairs.",
                key_phrases=["Taiwan independence separatists", "Chinese sovereignty", "external interference"])),
            OutletResult(outlet=_outlet("bbc"), article_count=3, scores=BiasScores(
                emotional_tone=3, framing=3, source_selection=3, loaded_language=3, political_stance=5, factual_density=6, overall=3,
                sentiment="Measured", sentiment_target="both sides",
                verdict="Even-handed coverage of military movements with context on historical cross-strait relations.",
                key_phrases=["self-governing island", "Beijing claims", "Washington's position"])),
            OutletResult(outlet=_outlet("reuters"), article_count=3, scores=BiasScores(
                emotional_tone=2, framing=2, source_selection=2, loaded_language=2, political_stance=5, factual_density=6, overall=2,
                sentiment="Neutral", sentiment_target="events",
                verdict="Factual reporting on vessel movements, official statements, and market reactions.",
                key_phrases=["warships entered", "officials confirmed", "markets fell"])),
            OutletResult(outlet=_outlet("guardian"), article_count=2, scores=BiasScores(
                emotional_tone=5, framing=5, source_selection=4, loaded_language=5, political_stance=5, factual_density=6, overall=5,
                sentiment="Critical", sentiment_target="China",
                verdict="Critical of Chinese military pressure while noting US arms sales as a complicating factor.",
                key_phrases=["military intimidation", "arms sales controversy", "regional stability"])),
            OutletResult(outlet=_outlet("aljazeera"), article_count=2, scores=BiasScores(
                emotional_tone=4, framing=5, source_selection=4, loaded_language=4, political_stance=5, factual_density=6, overall=4,
                sentiment="Critical", sentiment_target="US involvement",
                verdict="Questions US motives, framing the crisis as partly driven by Washington's strategic competition with Beijing.",
                key_phrases=["great power rivalry", "US provocations", "geopolitical chess"])),
        ],
        synthesis=Synthesis(
            synthesis="All outlets report increased Chinese military activity in the Taiwan Strait following a US arms sale announcement. CGTN frames this as a justified sovereign response; Western outlets frame it as coercive intimidation. Reuters and BBC provide the most neutral accounts. There is broad consensus on the facts of military movements but sharp divergence on causation and legitimacy.",
            consensus_facts=["PLA conducted live-fire exercises near median line", "US carrier group entered region", "Taiwan activated air defence systems"],
            key_divergence="Western outlets frame Chinese exercises as unprovoked aggression; CGTN and some Asian press frame them as a legitimate response to US arms sales and Taiwan separatism."
        )
    ),

    "ukraine russia war": AnalyzeResponse(
        topic="Ukraine Russia War",
        provider="claude",
        time_range_days=7,
        results=[
            OutletResult(outlet=_outlet("nyt"), article_count=3, scores=BiasScores(
                emotional_tone=6, framing=6, source_selection=5, loaded_language=6, political_stance=5, factual_density=6, overall=6,
                sentiment="Pro-West", sentiment_target="Russia",
                verdict="Frames the conflict as Russian aggression against a sovereign democracy, emphasising Ukrainian civilian suffering.",
                key_phrases=["unprovoked invasion", "war crimes", "democratic Ukraine"])),
            OutletResult(outlet=_outlet("rt"), article_count=3, scores=BiasScores(
                emotional_tone=7, framing=9, source_selection=7, loaded_language=8, political_stance=5, factual_density=6, overall=8,
                sentiment="Nationalist", sentiment_target="NATO and Ukraine",
                verdict="Presents the conflict as a defensive special military operation against NATO expansion and Ukrainian neo-Nazism.",
                key_phrases=["special military operation", "NATO aggression", "denazification"])),
            OutletResult(outlet=_outlet("bbc"), article_count=3, scores=BiasScores(
                emotional_tone=4, framing=4, source_selection=3, loaded_language=4, political_stance=5, factual_density=6, overall=4,
                sentiment="Critical", sentiment_target="Russia",
                verdict="Reports Russian advances and Ukrainian resistance factually, with critical framing of Russian military tactics.",
                key_phrases=["Russian forces", "Ukrainian defenders", "civilian casualties"])),
            OutletResult(outlet=_outlet("reuters"), article_count=3, scores=BiasScores(
                emotional_tone=2, framing=2, source_selection=2, loaded_language=2, political_stance=5, factual_density=6, overall=2,
                sentiment="Neutral", sentiment_target="events",
                verdict="Dry factual reporting on frontline movements, casualty figures, and diplomatic developments.",
                key_phrases=["forces advanced", "officials said", "according to military"])),
            OutletResult(outlet=_outlet("aljazeera"), article_count=2, scores=BiasScores(
                emotional_tone=4, framing=5, source_selection=4, loaded_language=4, political_stance=5, factual_density=6, overall=5,
                sentiment="Critical", sentiment_target="both sides",
                verdict="Broader geopolitical framing questioning Western weapons supplies and covering Global South perspectives on the conflict.",
                key_phrases=["proxy war", "global south", "Western weapons"])),
            OutletResult(outlet=_outlet("guardian"), article_count=3, scores=BiasScores(
                emotional_tone=6, framing=6, source_selection=5, loaded_language=6, political_stance=5, factual_density=6, overall=6,
                sentiment="Pro-West", sentiment_target="Russia",
                verdict="Strong support for Ukraine framing, critical of Western governments for insufficient military aid.",
                key_phrases=["not enough weapons", "Putin's war", "Ukrainian resistance"])),
        ],
        synthesis=Synthesis(
            synthesis="All outlets confirm ongoing Russian advances in eastern Ukraine and continued Western military support for Kyiv. RT presents a fundamentally different causal narrative — framing NATO expansion as the root cause — which is rejected by all Western outlets. Reuters and Al Jazeera provide the most neutral framing, while RT and Guardian represent the most opposing poles of the coverage spectrum.",
            consensus_facts=["Fighting continues in Donetsk region", "Western nations approved new aid packages", "Civilian infrastructure targeted in strikes"],
            key_divergence="Western outlets unanimously frame Russia as the aggressor in an unprovoked invasion; RT frames the conflict as a defensive response to NATO encirclement and a denazification operation."
        )
    ),
}

def get_demo(topic: str) -> AnalyzeResponse | None:
    return DEMO_TOPICS.get(topic.lower().strip())

def list_demo_topics() -> list[str]:
    return [v.topic for v in DEMO_TOPICS.values()]
