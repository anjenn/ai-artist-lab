"""Conversation selection endpoints for the demo chat UI."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.models import Artist, Conversation, Fan, Message
from app.db.session import get_db
from app.schemas.conversations import ConversationCreate

router = APIRouter(prefix="/conversations", tags=["conversations"])


def _conversation_row(conversation: Conversation, message_count: int = 0) -> dict:
    return {
        "id": conversation.id,
        "artist_id": conversation.artist_id,
        "fan_id": conversation.fan_id,
        "message_count": message_count,
        "created_at": conversation.created_at.isoformat(),
        "updated_at": conversation.updated_at.isoformat(),
    }


@router.get("")
def list_conversations(artist_id: int = 1, fan_id: int = 1, db: Session = Depends(get_db)) -> dict:
    rows = db.execute(
        select(Conversation, func.count(Message.id))
        .outerjoin(Message, Message.conversation_id == Conversation.id)
        .where(Conversation.artist_id == artist_id, Conversation.fan_id == fan_id)
        .group_by(Conversation.id)
        .order_by(Conversation.updated_at.desc(), Conversation.id.desc())
    ).all()
    return {"items": [_conversation_row(conversation, count or 0) for conversation, count in rows]}


@router.post("")
def create_conversation(payload: ConversationCreate, db: Session = Depends(get_db)) -> dict:
    if db.get(Artist, payload.artist_id) is None:
        raise HTTPException(status_code=404, detail="Artist not found")
    if db.get(Fan, payload.fan_id) is None:
        raise HTTPException(status_code=404, detail="Fan not found")
    conversation = Conversation(artist_id=payload.artist_id, fan_id=payload.fan_id)
    db.add(conversation)
    db.commit()
    db.refresh(conversation)
    return _conversation_row(conversation)
