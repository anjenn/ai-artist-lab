"""Fan memory endpoints for inspecting and editing long-term context."""

from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.fans import FanMemoryCreate, FanMemoryRead
from app.services.memory_service import create_fan_memory, delete_fan_memory, load_fan_memories

router = APIRouter(prefix="/fans", tags=["fans"])


@router.get("/{fan_id}/memories", response_model=list[FanMemoryRead])
def get_fan_memories(fan_id: int, artist_id: int = 1, db: Session = Depends(get_db)) -> list:
    return load_fan_memories(db, fan_id=fan_id, artist_id=artist_id)


@router.post("/{fan_id}/memories", response_model=FanMemoryRead)
def add_fan_memory(fan_id: int, payload: FanMemoryCreate, db: Session = Depends(get_db)):
    return create_fan_memory(
        db,
        fan_id=fan_id,
        artist_id=payload.artist_id,
        memory_type=payload.memory_type,
        content=payload.content,
        confidence=payload.confidence,
        sensitivity=payload.sensitivity,
        source_message_id=payload.source_message_id,
    )


@router.delete("/{fan_id}/memories/{memory_id}", status_code=204)
def remove_fan_memory(fan_id: int, memory_id: int, db: Session = Depends(get_db)) -> Response:
    deleted = delete_fan_memory(db, fan_id=fan_id, memory_id=memory_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Memory not found")
    return Response(status_code=204)

