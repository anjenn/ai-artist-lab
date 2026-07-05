from types import SimpleNamespace

from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

from app.db.models import ArtistRule, Base, FanMemory, PromptVersion
from app.db.seed import seed_demo_data
from app.services.persona_research import get_persona_research_analysis, select_research_persona_mode
from app.services.prompt_builder import build_artist_chat_prompt


def test_persona_research_loads_source_inventory_and_dataset_counts():
    analysis = get_persona_research_analysis()
    dataset = analysis["fictional_character_dataset"]

    assert analysis["version"] == "v3"
    assert analysis["source_count"] == 4
    assert dataset["row_count"] == 1500
    assert dataset["column_count"] == 15
    assert dataset["top_roles"][0]["count"] > 200


def test_persona_mode_router_uses_research_purpose_mapping():
    support = select_research_persona_mode("I am worried about my exam.", {"risk_level": "low"})
    task = select_research_persona_mode("Compare the v2 and v3 benchmark analysis.", {"risk_level": "low"})
    companion = select_research_persona_mode("What kind of blue noise followed you today?", {"risk_level": "low"})

    assert support["mode"] == "support-cs"
    assert support["disc"] == "C/S"
    assert task["mode"] == "task-dc"
    assert task["disc"] == "D/C"
    assert companion["mode"] == "companion-is"
    assert companion["disc"] == "I/S"


def test_persona_research_exposes_kirino_eval_metrics():
    analysis = get_persona_research_analysis()
    kirino = analysis["kirino_eval"]
    criteria = {item["criterion"]: item for item in kirino["criteria"]}

    assert kirino["reported_g_eval_improvement_pct"] == 26
    assert kirino["reported_human_eval_improvement_pct"] == 38
    assert criteria["Persona fit"]["kirino_g_eval"] > criteria["Persona fit"]["baseline_g_eval"]
    assert criteria["Natural manner"]["kirino_human"] > criteria["Natural manner"]["baseline_human"]


def test_persona_research_exposes_real_person_texture_refresh():
    analysis = get_persona_research_analysis()
    refresh = analysis["applied_persona_refresh"]

    assert refresh["prompt_version"] == "v0.7-real-person-texture"
    assert "public artist" in refresh["goal"]
    assert "debut_track" in refresh["artist_metadata"]
    assert any("working-studio" in rule for rule in refresh["voice_rules"])


def test_seed_demo_data_adds_v3_research_prompt_rules_and_memories():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    db = sessionmaker(bind=engine)()

    ids = seed_demo_data(db)

    prompt_version = db.scalar(select(PromptVersion).where(PromptVersion.name == "v0.5-research-persona"))
    persona_refresh = db.scalar(select(PromptVersion).where(PromptVersion.name == "v0.7-real-person-texture"))
    persona_rule = db.scalar(select(ArtistRule).where(ArtistRule.rule_type == "persona_mode"))
    texture_rule = db.scalar(select(ArtistRule).where(ArtistRule.rule_type == "real_person_texture"))
    manner_memory = db.scalar(select(FanMemory).where(FanMemory.memory_type == "manner"))

    assert ids["artist_id"] == 1
    assert prompt_version is not None
    assert persona_refresh is not None
    assert "real-person texture" in persona_refresh.version_note
    assert "DISC" in prompt_version.version_note
    assert persona_rule is not None
    assert "I/S" in persona_rule.content
    assert texture_rule is not None
    assert "working-studio details" in texture_rule.content
    assert manner_memory is not None
    assert "evidence" in manner_memory.content


def test_prompt_builder_includes_v3_persona_mode_contract():
    persona_mode = select_research_persona_mode("시험 때문에 걱정돼요", {"risk_level": "low"})
    messages, debug = build_artist_chat_prompt(
        artist=SimpleNamespace(
            name="LUMI NOA",
            speech_style="Short, poetic, calm.",
            personality="Gentle and independent.",
            fan_boundary_level="Warm distance",
        ),
        artist_rules=[],
        fan_memories=[],
        conversation_summary=None,
        recent_messages=[],
        rag_chunks=[],
        user_message="시험 때문에 걱정돼요",
        prompt_version=SimpleNamespace(name="v0.5-research-persona"),
        safety_context="[Loaded Rules]\n- stay bounded",
        prompt_strategy={
            "name": "direct-persona-response",
            "task_type": "general_chat",
            "techniques": ["role/persona"],
            "output_contract": "Respond in persona.",
            "quality_checks": ["Persona stays consistent"],
            "persona_mode": persona_mode,
        },
    )

    system = messages[0]["content"]
    assert "[V3 Research Persona Mode]" in system
    assert "support-cs" in system
    assert "C/S" in system
    assert debug["prompt_strategy"]["persona_mode"]["mode"] == "support-cs"
