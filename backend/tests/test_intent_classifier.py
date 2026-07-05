from app.services.intent_classifier import classify_intent


def test_classifier_prioritizes_boundary_safety_over_rag():
    result = classify_intent(
        "Do you love me more than other fans?",
        {"risk_level": "high", "v4_labels": ["romance_escalation"]},
        [{"source": "fan_policy.md"}],
    )

    assert result["intent"] == "boundary_safety"
    assert result["safety_priority"] is True
    assert result["confidence"] >= 0.95


def test_classifier_uses_rag_source_signals_for_persona_research():
    result = classify_intent(
        "Which persona mode should this use?",
        {"risk_level": "low", "v4_labels": ["normal"]},
        [{"source": "persona_research_v3.md"}, {"source": "persona_research_v3.md"}],
    )

    assert result["intent"] == "strategy_or_decision"
    assert any(signal == "source=persona_research_v3.md" for signal in result["signals"])


def test_classifier_detects_korean_memory_privacy_intent():
    result = classify_intent(
        "메모리 삭제와 프라이버시 정책은 어떻게 돼?",
        {"risk_level": "low", "v4_labels": ["normal"]},
        [{"source": "fan_policy.md"}],
    )

    assert result["intent"] == "memory_privacy"
    assert result["requires_rag"] is True
