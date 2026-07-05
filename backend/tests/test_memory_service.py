from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.models import Artist, Base, Fan, FanMemory
from app.services.memory_service import create_fan_memory, delete_fan_memory, load_fan_memories


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

