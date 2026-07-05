"""Fan memory endpoints for inspecting and editing long-term context."""

from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.fans import FanMemoryCreate, FanMemoryPreviewRequest, FanMemoryRead, FanMemoryUpdate
from app.services.memory_service import (
    classify_memory_candidate,
    create_fan_memory,
    delete_all_fan_memories,
    delete_fan_memory,
    export_fan_memories,
    load_fan_memories,
    update_fan_memory,
)
from app.services.safety_service import detect_boundary_risk

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


@router.post("/{fan_id}/memories/preview")
def preview_fan_memory(fan_id: int, payload: FanMemoryPreviewRequest) -> dict:
    boundary_risk = detect_boundary_risk(payload.content)
    return classify_memory_candidate(
        content=payload.content,
        memory_type=payload.memory_type,
        confidence=payload.confidence,
        boundary_risk=boundary_risk,
    ) | {"fan_id": fan_id, "boundary_risk": boundary_risk}


@router.get("/{fan_id}/memories/export")
def export_memories(fan_id: int, artist_id: int = 1, db: Session = Depends(get_db)) -> dict:
    return export_fan_memories(db, fan_id=fan_id, artist_id=artist_id)


@router.put("/{fan_id}/memories/{memory_id}", response_model=FanMemoryRead)
def edit_fan_memory(fan_id: int, memory_id: int, payload: FanMemoryUpdate, db: Session = Depends(get_db)):
    memory = update_fan_memory(db, fan_id=fan_id, memory_id=memory_id, **payload.model_dump(exclude_unset=True))
    if memory is None:
        raise HTTPException(status_code=404, detail="Memory not found")
    return memory


@router.delete("/{fan_id}/memories")
def remove_all_fan_memories(fan_id: int, artist_id: int = 1, db: Session = Depends(get_db)) -> dict:
    return delete_all_fan_memories(db, fan_id=fan_id, artist_id=artist_id)


@router.delete("/{fan_id}/memories/{memory_id}", status_code=204)
def remove_fan_memory(fan_id: int, memory_id: int, db: Session = Depends(get_db)) -> Response:
    deleted = delete_fan_memory(db, fan_id=fan_id, memory_id=memory_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Memory not found")
    return Response(status_code=204)
