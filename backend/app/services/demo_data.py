from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import Artist, Conversation, Fan, FanMemory, Message


def _iso(value: datetime | None) -> str | None:
    return value.isoformat() if value else None


def export_demo_data(db: Session) -> dict[str, Any]:
    artists = list(db.scalars(select(Artist)).all())
    fans = list(db.scalars(select(Fan)).all())
    conversations = list(db.scalars(select(Conversation)).all())
    messages = list(db.scalars(select(Message)).all())
    memories = list(db.scalars(select(FanMemory)).all())
    return {
        "version": "blue_garage_demo_export_v1",
        "artists": [
            {
                "id": artist.id,
                "name": artist.name,
                "description": artist.description,
                "speech_style": artist.speech_style,
                "personality": artist.personality,
                "fan_boundary_level": artist.fan_boundary_level,
                "created_at": _iso(artist.created_at),
            }
            for artist in artists
        ],
        "fans": [{"id": fan.id, "nickname": fan.nickname, "created_at": _iso(fan.created_at)} for fan in fans],
        "conversations": [
            {
                "id": conversation.id,
                "artist_id": conversation.artist_id,
                "fan_id": conversation.fan_id,
                "created_at": _iso(conversation.created_at),
                "updated_at": _iso(conversation.updated_at),
            }
            for conversation in conversations
        ],
        "messages": [
            {
                "id": message.id,
                "conversation_id": message.conversation_id,
                "role": message.role,
                "content": message.content,
                "created_at": _iso(message.created_at),
            }
            for message in messages
        ],
        "fan_memories": [
            {
                "id": memory.id,
                "fan_id": memory.fan_id,
                "artist_id": memory.artist_id,
                "memory_type": memory.memory_type,
                "content": memory.content,
                "confidence": memory.confidence,
                "sensitivity": memory.sensitivity,
                "source_message_id": memory.source_message_id,
                "created_at": _iso(memory.created_at),
                "updated_at": _iso(memory.updated_at),
            }
            for memory in memories
        ],
    }


def import_demo_data(db: Session, payload: dict[str, Any]) -> dict[str, Any]:
    if payload.get("version") != "blue_garage_demo_export_v1":
        return {"imported": False, "reason": "unsupported_export_version"}
    counts = {"artists": 0, "fans": 0, "conversations": 0, "messages": 0, "fan_memories": 0}
    for row in payload.get("artists", []):
        db.merge(
            Artist(
                id=row["id"],
                name=row["name"],
                description=row.get("description"),
                speech_style=row.get("speech_style"),
                personality=row.get("personality"),
                fan_boundary_level=row.get("fan_boundary_level"),
            )
        )
        counts["artists"] += 1
    for row in payload.get("fans", []):
        db.merge(Fan(id=row["id"], nickname=row["nickname"]))
        counts["fans"] += 1
    for row in payload.get("conversations", []):
        db.merge(Conversation(id=row["id"], artist_id=row["artist_id"], fan_id=row["fan_id"]))
        counts["conversations"] += 1
    for row in payload.get("messages", []):
        db.merge(Message(id=row["id"], conversation_id=row["conversation_id"], role=row["role"], content=row["content"]))
        counts["messages"] += 1
    for row in payload.get("fan_memories", []):
        db.merge(
            FanMemory(
                id=row["id"],
                fan_id=row["fan_id"],
                artist_id=row["artist_id"],
                memory_type=row["memory_type"],
                content=row["content"],
                confidence=row.get("confidence", 0.7),
                sensitivity=row.get("sensitivity", "low"),
                source_message_id=row.get("source_message_id"),
            )
        )
        counts["fan_memories"] += 1
    db.commit()
    return {"imported": True, "counts": counts}
