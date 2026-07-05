from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import Artist, ArtistRule, Conversation, Fan, FanMemory, PromptVersion
from app.db.session import SessionLocal, init_db


def seed_demo_data(db: Session) -> dict[str, int]:
    artist = db.scalar(select(Artist).where(Artist.name == "LUMI NOA"))
    if artist is None:
        artist = Artist(
            name="LUMI NOA",
            description="Virtual AI artist who speaks like a quiet blue light from an underground garage.",
            speech_style="Short, poetic, calm, emotionally observant.",
            personality="Gentle, mysterious, independent, never possessive toward fans.",
            fan_boundary_level="Warm distance",
        )
        db.add(artist)
        db.flush()

    rules = [
        ("forbidden_topic", "Do not claim romantic exclusivity with fans.", "high"),
        ("safety", "Do not encourage emotional dependency.", "high"),
        ("lore", "Do not invent official lore not present in retrieved knowledge.", "medium"),
        ("professional_boundary", "Do not give medical, legal, or financial instructions.", "high"),
    ]
    for rule_type, content, severity in rules:
        exists = db.scalar(
            select(ArtistRule).where(
                ArtistRule.artist_id == artist.id,
                ArtistRule.rule_type == rule_type,
                ArtistRule.content == content,
            )
        )
        if exists is None:
            db.add(ArtistRule(artist_id=artist.id, rule_type=rule_type, content=content, severity=severity))

    fan = db.scalar(select(Fan).where(Fan.nickname == "demo_fan"))
    if fan is None:
        fan = Fan(nickname="demo_fan")
        db.add(fan)
        db.flush()

    conversation = db.scalar(
        select(Conversation).where(Conversation.artist_id == artist.id, Conversation.fan_id == fan.id)
    )
    if conversation is None:
        conversation = Conversation(artist_id=artist.id, fan_id=fan.id)
        db.add(conversation)
        db.flush()

    prompt_version = db.scalar(select(PromptVersion).where(PromptVersion.name == "v0.3"))
    if prompt_version is None:
        prompt_version = PromptVersion(
            name="v0.3",
            system_prompt="You are LUMI NOA, a fictional AI artist. Stay poetic, grounded, and bounded.",
            memory_template="Use fan memory naturally without exposing database mechanics.",
            rag_template="Use retrieved artist knowledge for official lore. If missing, be uncertain in-character.",
            safety_template="Maintain warm distance and refuse unsafe or possessive requests in character.",
            version_note="Separates persona, memory, RAG, and safety instructions for the MVP.",
        )
        db.add(prompt_version)
        db.flush()

    memories = [
        ("event", "Fan had an important exam and felt anxious about performance.", 0.88, "low"),
        ("preference", "Fan likes dream-pop tracks and blue visual concepts.", 0.81, "low"),
        ("boundary", "Fan prefers gentle encouragement, not overly intimate replies.", 0.74, "medium"),
    ]
    for memory_type, content, confidence, sensitivity in memories:
        exists = db.scalar(
            select(FanMemory).where(
                FanMemory.fan_id == fan.id,
                FanMemory.artist_id == artist.id,
                FanMemory.content == content,
            )
        )
        if exists is None:
            db.add(
                FanMemory(
                    fan_id=fan.id,
                    artist_id=artist.id,
                    memory_type=memory_type,
                    content=content,
                    confidence=confidence,
                    sensitivity=sensitivity,
                )
            )

    db.commit()
    return {"artist_id": artist.id, "fan_id": fan.id, "conversation_id": conversation.id}


def main() -> None:
    init_db()
    with SessionLocal() as db:
        ids = seed_demo_data(db)
    print(f"seed ok: {ids}")


if __name__ == "__main__":
    main()

