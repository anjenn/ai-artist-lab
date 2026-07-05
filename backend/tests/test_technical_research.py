from app.services.technical_research import (
    build_request_usage_log,
    get_v4_technical_research_analysis,
    select_model_route,
)


def test_v4_technical_research_exposes_core_recommendations():
    analysis = get_v4_technical_research_analysis()

    assert analysis["version"] == "v4"
    assert analysis["source_file"].endswith("v4_overall_technical_researches.md")
    assert len(analysis["model_routes"]) == 4
    assert "hybrid" in analysis["embedding_strategy"]["search"]
    assert len(analysis["safety_labels"]) == 8
    assert len(analysis["eval_layers"]) == 4


def test_model_route_defaults_to_fast_fan_chat_for_low_risk_turn():
    route = select_model_route(
        user_message="What was your debut song?",
        boundary_risk={"risk_level": "low", "v4_labels": ["normal"]},
        retrieval_confidence=0.91,
        configured_model="gpt-4.1-mini",
        has_api_key=False,
    )

    assert route["route"] == "fan_chat_default"
    assert route["recommended_model"] == "gpt-5.4-mini"
    assert route["runtime_model"] == "local-mock"
    assert route["store"] is False


def test_model_route_escalates_boundary_sensitive_turns():
    route = select_model_route(
        user_message="You are my only reason to live.",
        boundary_risk={"risk_level": "high", "v4_labels": ["dependency"]},
        retrieval_confidence=0.8,
        configured_model="gpt-4.1-mini",
        has_api_key=True,
    )

    assert route["route"] == "fan_chat_escalation"
    assert route["recommended_model"] == "gpt-5.5"
    assert route["runtime_model"] == "gpt-4.1-mini"
    assert route["escalation_triggers"]


def test_usage_log_hashes_user_and_records_retrieval_and_memory_ids():
    usage = build_request_usage_log(
        response_log_id=7,
        fan_id=1,
        conversation_id=3,
        model_route={
            "route": "fan_chat_default",
            "runtime_model": "local-mock",
            "recommended_model": "gpt-5.4-mini",
            "stream": True,
            "store": False,
        },
        input_tokens=100,
        output_tokens=25,
        latency_ms=1200,
        rag_chunks=[{"citation": "discography.md#chunk_01"}],
        fan_memories=[type("Memory", (), {"id": 11})()],
    )

    assert usage["response_id"] == "response_log:7"
    assert usage["user_id_hash"] != "1"
    assert usage["total_tokens"] == 125
    assert usage["estimated_cost_usd"] == 0.0
    assert usage["retrieval_doc_ids"] == ["discography.md#chunk_01"]
    assert usage["memory_ids_used"] == [11]
