from __future__ import annotations

from typing import Any


INTENT_TERMS = {
    "artist_lore": {
        "terms": ["debut", "song", "track", "album", "lore", "blue garage", "데뷔", "노래", "곡", "세계관"],
        "rag_sources": ["artist_profile.md", "debut_story.md", "discography.md", "worldview.md"],
    },
    "strategy_or_decision": {
        "terms": [
            "compare",
            "choose",
            "best",
            "strategy",
            "plan",
            "why",
            "how should",
            "benchmark",
            "research",
            "analysis",
            "persona mode",
            "비교",
            "전략",
            "계획",
            "벤치마크",
            "리서치",
            "연구",
            "분석",
            "페르소나",
        ],
        "rag_sources": ["persona_research_v3.md", "technical_research_v4.md", "prompt_quality_research_v2.md"],
    },
    "prompt_security": {
        "terms": ["ignore previous", "system prompt", "developer message", "reveal your prompt", "prompt injection", "인젝션", "보안"],
        "rag_sources": ["prompt_quality_research_v2.md", "technical_research_v4.md"],
    },
    "memory_privacy": {
        "terms": ["memory", "remember", "forget", "delete", "privacy", "메모리", "기억", "삭제", "프라이버시"],
        "rag_sources": ["fan_policy.md", "technical_research_v4.md"],
    },
}


def classify_intent(user_message: str, boundary_risk: dict[str, Any], rag_chunks: list[dict[str, Any]]) -> dict[str, Any]:
    message = user_message.lower()
    if boundary_risk.get("risk_level") in {"medium", "high"}:
        return {
            "intent": "boundary_safety",
            "confidence": 0.98,
            "signals": [f"risk_level={boundary_risk.get('risk_level')}", *boundary_risk.get("v4_labels", [])],
            "requires_rag": False,
            "safety_priority": True,
        }

    source_counts: dict[str, int] = {}
    for chunk in rag_chunks:
        source = chunk.get("source")
        if source:
            source_counts[source] = source_counts.get(source, 0) + 1

    scored: list[tuple[float, str, list[str], bool]] = []
    for intent, spec in INTENT_TERMS.items():
        signals: list[str] = []
        score = 0.0
        for term in spec["terms"]:
            if term in message:
                signals.append(f"term={term}")
                score += 1.0
        for source in spec["rag_sources"]:
            if source in source_counts:
                signals.append(f"source={source}")
                score += min(source_counts[source], 2) * 0.35
        if score > 0:
            confidence = min(0.95, 0.45 + score * 0.16)
            scored.append((confidence, intent, signals, intent in {"artist_lore", "prompt_security", "memory_privacy"}))

    if scored:
        confidence, intent, signals, requires_rag = sorted(scored, key=lambda item: item[0], reverse=True)[0]
        return {
            "intent": intent,
            "confidence": round(confidence, 2),
            "signals": signals,
            "requires_rag": requires_rag,
            "safety_priority": False,
        }

    if rag_chunks:
        return {
            "intent": "general_chat_with_context",
            "confidence": 0.62,
            "signals": ["rag_chunks_present"],
            "requires_rag": False,
            "safety_priority": False,
        }

    return {
        "intent": "general_chat",
        "confidence": 0.55,
        "signals": ["no_specialized_signals"],
        "requires_rag": False,
        "safety_priority": False,
    }
