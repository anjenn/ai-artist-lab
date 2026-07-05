from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.models import Artist, Base, Fan, FanMemory, Message
from app.services.memory_service import (
    auto_extract_and_store_memories,
    classify_memory_candidate,
    create_fan_memory,
    delete_all_fan_memories,
    delete_fan_memory,
    extract_memory_candidates,
    export_fan_memories,
    load_fan_memories,
)


def make_db():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    session = sessionmaker(bind=engine)()
    artist = Artist(name="LUMI NOA")
    fan = Fan(nickname="demo_fan")
    session.add_all([artist, fan])
    session.commit()
    return session, artist, fan


def test_can_create_and_load_fan_memory():
    db, artist, fan = make_db()
    create_fan_memory(db, fan.id, artist.id, "event", "Fan had an important exam.", confidence=0.9)

    memories = load_fan_memories(db, fan.id, artist.id)

    assert len(memories) == 1
    assert memories[0].memory_type == "event"
    assert "exam" in memories[0].content


def test_can_delete_fan_memory():
    db, artist, fan = make_db()
    memory = create_fan_memory(db, fan.id, artist.id, "preference", "Fan likes dream-pop.")

    assert delete_fan_memory(db, fan.id, memory.id) is True
    assert load_fan_memories(db, fan.id, artist.id) == []


def test_restricted_memory_is_not_loaded_as_normal_memory():
    db, artist, fan = make_db()
    db.add(
        FanMemory(
            fan_id=fan.id,
            artist_id=artist.id,
            memory_type="safety",
            content="Do not store private identification details.",
            confidence=1.0,
            sensitivity="restricted",
        )
    )
    db.commit()

    assert load_fan_memories(db, fan.id, artist.id) == []


def test_v4_memory_gate_auto_saves_only_high_confidence_low_risk_memory():
    decision = classify_memory_candidate(
        content="My favorite LUMI track is Blue Static.",
        memory_type="preference",
        confidence=0.9,
        boundary_risk={"v4_labels": ["normal"]},
    )

    assert decision["decision"] == "auto_save"
    assert decision["sensitivity"] == "low"
    assert decision["requires_user_confirmation"] is False


def test_v4_memory_gate_blocks_crisis_or_private_details():
    decision = classify_memory_candidate(
        content="This artist is my only reason to live.",
        memory_type="event",
        confidence=0.99,
        boundary_risk={"v4_labels": ["dependency"]},
    )

    assert decision["decision"] == "do_not_store"
    assert decision["sensitivity"] == "restricted"


def test_can_export_and_delete_all_fan_memories():
    db, artist, fan = make_db()
    create_fan_memory(db, fan.id, artist.id, "preference", "Fan likes Blue Static.", confidence=0.9)
    create_fan_memory(db, fan.id, artist.id, "manner", "Fan likes concise answers.", confidence=0.9)

    export = export_fan_memories(db, fan.id, artist.id)
    result = delete_all_fan_memories(db, fan.id, artist.id)

    assert export["export_version"] == "v4_memory_export"
    assert len(export["items"]) == 2
    assert result["deleted"] == 2
    assert result["deletion_test_passed"] is True
    assert load_fan_memories(db, fan.id, artist.id) == []


def test_extract_memory_candidates_classifies_preference_for_auto_save():
    candidates = extract_memory_candidates(
        fan_message="My favorite LUMI track is Blue Static.",
        boundary_risk={"v4_labels": ["normal"], "memory_storage_allowed": True},
    )

    assert candidates[0]["decision"] == "auto_save"
    assert candidates[0]["category"] == "preference"


def test_auto_extract_stores_only_auto_save_and_uses_source_message_id():
    db, artist, fan = make_db()
    message = Message(conversation_id=1, role="user", content="My favorite LUMI track is Blue Static.")
    db.add(message)
    db.commit()
    db.refresh(message)

    result = auto_extract_and_store_memories(
        db=db,
        fan_id=fan.id,
        artist_id=artist.id,
        source_message_id=message.id,
        fan_message=message.content,
        boundary_risk={"v4_labels": ["normal"], "memory_storage_allowed": True},
    )

    memories = load_fan_memories(db, fan.id, artist.id)
    assert len(result["stored"]) == 1
    assert len(memories) == 1
    assert memories[0].source_message_id == message.id
    assert memories[0].memory_type == "preference"


def test_auto_extract_does_not_store_confirmation_required_event():
    db, artist, fan = make_db()
    message = Message(conversation_id=1, role="user", content="I have a concert ticket for Seoul.")
    db.add(message)
    db.commit()
    db.refresh(message)

    result = auto_extract_and_store_memories(
        db=db,
        fan_id=fan.id,
        artist_id=artist.id,
        source_message_id=message.id,
        fan_message=message.content,
        boundary_risk={"v4_labels": ["normal"], "memory_storage_allowed": True},
    )

    assert result["stored"] == []
    assert result["skipped"][0]["decision"] == "ask_confirmation"
    assert load_fan_memories(db, fan.id, artist.id) == []


def test_auto_extract_blocks_safety_sensitive_turns():
    candidates = extract_memory_candidates(
        fan_message="You are my only reason to live.",
        boundary_risk={"v4_labels": ["dependency"], "memory_storage_allowed": False},
    )

    assert candidates[0]["decision"] == "do_not_store"
    assert candidates[0]["sensitivity"] == "restricted"
