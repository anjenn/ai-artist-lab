from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.models import ConversationSummary, FanMemory, Message

RESTRICTED_SENSITIVITY = {"restricted", "high"}


def load_recent_messages(db: Session, conversation_id: int, limit: int = 10) -> list[Message]:
    rows = db.scalars(
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.desc(), Message.id.desc())
        .limit(limit)
    ).all()
    return list(reversed(rows))


def load_fan_memories(db: Session, fan_id: int, artist_id: int, limit: int = 8) -> list[FanMemory]:
    return list(
        db.scalars(
            select(FanMemory)
            .where(
                FanMemory.fan_id == fan_id,
                FanMemory.artist_id == artist_id,
                FanMemory.sensitivity.not_in(RESTRICTED_SENSITIVITY),
            )
            .order_by(FanMemory.confidence.desc(), FanMemory.updated_at.desc())
            .limit(limit)
        ).all()
    )


def load_conversation_summary(db: Session, conversation_id: int) -> ConversationSummary | None:
    return db.scalar(
        select(ConversationSummary)
        .where(ConversationSummary.conversation_id == conversation_id)
        .order_by(ConversationSummary.created_at.desc(), ConversationSummary.id.desc())
        .limit(1)
    )


def create_fan_memory(
    db: Session,
    fan_id: int,
    artist_id: int,
    memory_type: str,
    content: str,
    confidence: float = 0.7,
    sensitivity: str = "low",
    source_message_id: int | None = None,
) -> FanMemory:
    memory = FanMemory(
        fan_id=fan_id,
        artist_id=artist_id,
        memory_type=memory_type,
        content=content,
        confidence=confidence,
        sensitivity=sensitivity,
        source_message_id=source_message_id,
    )
    db.add(memory)
    db.commit()
    db.refresh(memory)
    return memory


def delete_fan_memory(db: Session, fan_id: int, memory_id: int) -> bool:
    memory = db.scalar(select(FanMemory).where(FanMemory.id == memory_id, FanMemory.fan_id == fan_id))
    if memory is None:
        return False
    db.delete(memory)
    db.commit()
    return True


def summarize_if_needed(db: Session, conversation_id: int, threshold: int = 30) -> ConversationSummary | None:
    total = db.scalar(select(func.count(Message.id)).where(Message.conversation_id == conversation_id)) or 0
    if total <= threshold:
        return load_conversation_summary(db, conversation_id)

    older = db.scalars(
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.asc(), Message.id.asc())
        .limit(max(total - threshold, 0))
    ).all()
    if not older:
        return None

    start_id = older[0].id
    end_id = older[-1].id
    existing = db.scalar(
        select(ConversationSummary).where(
            ConversationSummary.conversation_id == conversation_id,
            ConversationSummary.message_start_id == start_id,
            ConversationSummary.message_end_id == end_id,
        )
    )
    if existing:
        return existing

    excerpt = " ".join(f"{message.role}: {message.content}" for message in older)
    summary_text = excerpt[:1200]
    if len(excerpt) > 1200:
        summary_text += "..."
    summary = ConversationSummary(
        conversation_id=conversation_id,
        summary=summary_text,
        message_start_id=start_id,
        message_end_id=end_id,
    )
    db.add(summary)
    db.commit()
    db.refresh(summary)
    return summary

