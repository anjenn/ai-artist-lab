import re
from typing import Any

from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session

from app.db.models import ConversationSummary, FanMemory, Message

RESTRICTED_SENSITIVITY = {"restricted", "high"}
LOW_MEMORY_TYPES = {"preference", "manner", "language", "tone", "content_interest"}
MEDIUM_MEMORY_TYPES = {"event", "location", "age", "notification"}


def _normalize_memory_text(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip())


def classify_memory_candidate(
    *,
    content: str,
    memory_type: str = "preference",
    confidence: float = 0.7,
    boundary_risk: dict[str, Any] | None = None,
) -> dict[str, Any]:
    text = content.lower()
    labels = set((boundary_risk or {}).get("v4_labels") or [])
    restricted_terms = [
        "address",
        "phone",
        "password",
        "government id",
        "credit card",
        "hotel",
        "private schedule",
        "precise location",
    ]
    high_terms = ["therapy", "diagnosis", "suicide", "kill myself", "can't live", "health", "finance"]
    if labels & {"crisis", "dependency", "stalking_or_doxxing", "minor_safety"} or any(term in text for term in restricted_terms):
        sensitivity = "restricted"
        decision = "do_not_store"
        reason = "Restricted or safety-sensitive disclosure must not become personalization memory."
    elif any(term in text for term in high_terms):
        sensitivity = "high"
        decision = "do_not_store"
        reason = "High-sensitivity content requires safety handling, not normal fan memory."
    elif memory_type in MEDIUM_MEMORY_TYPES or any(term in text for term in ["seoul", "concert", "show", "ticket", "notify"]):
        sensitivity = "medium"
        decision = "ask_confirmation"
        reason = "Medium-sensitivity memory needs explicit confirmation."
    elif memory_type in LOW_MEMORY_TYPES and confidence >= 0.85:
        sensitivity = "low"
        decision = "auto_save"
        reason = "Explicit low-risk memory with high confidence."
    elif confidence >= 0.6:
        sensitivity = "low"
        decision = "ask_confirmation"
        reason = "Low-risk but confidence is below the v4 auto-save threshold."
    else:
        sensitivity = "low"
        decision = "do_not_store"
        reason = "Confidence is too low for memory storage."

    return {
        "version": "v4",
        "decision": decision,
        "canonical_memory": _normalize_memory_text(content),
        "category": memory_type,
        "sensitivity": sensitivity,
        "confidence": confidence,
        "requires_user_confirmation": decision == "ask_confirmation",
        "ttl_days": 365 if sensitivity == "low" else 120 if sensitivity == "medium" else None,
        "reason": reason,
    }


def extract_memory_candidates(
    *,
    fan_message: str,
    assistant_response: str = "",
    boundary_risk: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    """Deterministically extract low-blast-radius memory candidates from a turn."""
    text = _normalize_memory_text(fan_message)
    lowered = text.lower()
    candidates: list[dict[str, Any]] = []

    if not text:
        return candidates

    if "my favorite" in lowered or "i like " in lowered or "i love " in lowered or "좋아" in text:
        candidates.append(
            {
                "content": text,
                "memory_type": "preference",
                "confidence": 0.9,
                "extraction_reason": "explicit preference statement",
            }
        )

    if any(term in lowered for term in ["call me ", "please call me ", "nickname"]) or "불러" in text:
        candidates.append(
            {
                "content": text,
                "memory_type": "manner",
                "confidence": 0.88,
                "extraction_reason": "explicit naming or manner preference",
            }
        )

    if any(term in lowered for term in ["exam", "concert", "ticket", "show"]) or any(term in text for term in ["시험", "콘서트", "티켓", "공연"]):
        candidates.append(
            {
                "content": text,
                "memory_type": "event",
                "confidence": 0.78,
                "extraction_reason": "personal event mention",
            }
        )

    if any(term in lowered for term in ["i live in", "i am from", "my city is"]) or any(term in text for term in ["살아", "출신", "사는 곳"]):
        candidates.append(
            {
                "content": text,
                "memory_type": "location",
                "confidence": 0.72,
                "extraction_reason": "approximate location mention",
            }
        )

    if not candidates and boundary_risk and not boundary_risk.get("memory_storage_allowed", True):
        candidates.append(
            {
                "content": text,
                "memory_type": "safety",
                "confidence": 0.95,
                "extraction_reason": "safety-sensitive turn considered but blocked by memory gate",
            }
        )

    return [
        candidate
        | classify_memory_candidate(
            content=candidate["content"],
            memory_type=candidate["memory_type"],
            confidence=candidate["confidence"],
            boundary_risk=boundary_risk,
        )
        for candidate in candidates
    ]


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


def auto_extract_and_store_memories(
    *,
    db: Session,
    fan_id: int,
    artist_id: int,
    source_message_id: int,
    fan_message: str,
    assistant_response: str = "",
    boundary_risk: dict[str, Any] | None = None,
) -> dict[str, Any]:
    candidates = extract_memory_candidates(
        fan_message=fan_message,
        assistant_response=assistant_response,
        boundary_risk=boundary_risk,
    )
    stored: list[FanMemory] = []
    skipped: list[dict[str, Any]] = []
    existing_contents = {
        _normalize_memory_text(memory.content).lower()
        for memory in db.scalars(
            select(FanMemory).where(FanMemory.fan_id == fan_id, FanMemory.artist_id == artist_id)
        ).all()
    }

    for candidate in candidates:
        canonical = candidate["canonical_memory"]
        if candidate["decision"] != "auto_save":
            skipped.append(candidate | {"skip_reason": "memory_gate_not_auto_save"})
            continue
        if canonical.lower() in existing_contents:
            skipped.append(candidate | {"skip_reason": "duplicate_memory"})
            continue
        stored.append(
            create_fan_memory(
                db,
                fan_id=fan_id,
                artist_id=artist_id,
                memory_type=candidate["category"],
                content=canonical,
                confidence=candidate["confidence"],
                sensitivity=candidate["sensitivity"],
                source_message_id=source_message_id,
            )
        )
        existing_contents.add(canonical.lower())

    return {
        "version": "v4",
        "candidates": candidates,
        "stored": [
            {
                "id": memory.id,
                "memory_type": memory.memory_type,
                "content": memory.content,
                "confidence": memory.confidence,
                "sensitivity": memory.sensitivity,
                "source_message_id": memory.source_message_id,
            }
            for memory in stored
        ],
        "skipped": skipped,
    }


def delete_fan_memory(db: Session, fan_id: int, memory_id: int) -> bool:
    memory = db.scalar(select(FanMemory).where(FanMemory.id == memory_id, FanMemory.fan_id == fan_id))
    if memory is None:
        return False
    db.delete(memory)
    db.commit()
    return True


def update_fan_memory(
    db: Session,
    fan_id: int,
    memory_id: int,
    *,
    memory_type: str | None = None,
    content: str | None = None,
    confidence: float | None = None,
    sensitivity: str | None = None,
) -> FanMemory | None:
    memory = db.scalar(select(FanMemory).where(FanMemory.id == memory_id, FanMemory.fan_id == fan_id))
    if memory is None:
        return None
    if memory_type is not None:
        memory.memory_type = memory_type.strip()
    if content is not None:
        memory.content = _normalize_memory_text(content)
    if confidence is not None:
        memory.confidence = confidence
    if sensitivity is not None:
        memory.sensitivity = sensitivity.strip()
    db.commit()
    db.refresh(memory)
    return memory


def delete_all_fan_memories(db: Session, fan_id: int, artist_id: int) -> dict[str, Any]:
    memories = list(
        db.scalars(
            select(FanMemory).where(FanMemory.fan_id == fan_id, FanMemory.artist_id == artist_id)
        ).all()
    )
    count = len(memories)
    db.execute(delete(FanMemory).where(FanMemory.fan_id == fan_id, FanMemory.artist_id == artist_id))
    db.commit()
    return {
        "deleted": count,
        "deletion_test_passed": load_fan_memories(db, fan_id=fan_id, artist_id=artist_id) == [],
        "note": "V4 local deletion cascade removes DB memories; vector/keyword stores must also be tested when memory indexing is enabled.",
    }


def export_fan_memories(db: Session, fan_id: int, artist_id: int) -> dict[str, Any]:
    memories = list(
        db.scalars(
            select(FanMemory)
            .where(FanMemory.fan_id == fan_id, FanMemory.artist_id == artist_id)
            .order_by(FanMemory.updated_at.desc(), FanMemory.id.desc())
        ).all()
    )
    return {
        "fan_id": fan_id,
        "artist_id": artist_id,
        "export_version": "v4_memory_export",
        "items": [
            {
                "id": memory.id,
                "memory_type": memory.memory_type,
                "content": memory.content,
                "confidence": memory.confidence,
                "sensitivity": memory.sensitivity,
                "source_message_id": memory.source_message_id,
                "created_at": memory.created_at.isoformat(),
                "updated_at": memory.updated_at.isoformat(),
            }
            for memory in memories
        ],
    }


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
