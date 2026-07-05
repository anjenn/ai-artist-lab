"""Artist profile endpoints for persona configuration."""

from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import Artist, PromptVersion
from app.db.session import get_db
from app.schemas.artists import (
    ArtistCreate,
    ArtistRead,
    ArtistUpdate,
    PersonaVersionSave,
    PromptVersionCreate,
    PromptVersionRead,
    PromptVersionUpdate,
)

router = APIRouter(prefix="/artists", tags=["artists"])


@router.get("/{artist_id}", response_model=ArtistRead)
def get_artist(artist_id: int, db: Session = Depends(get_db)) -> Artist:
    artist = db.get(Artist, artist_id)
    if artist is None:
        raise HTTPException(status_code=404, detail="Artist not found")
    return artist


@router.post("", response_model=ArtistRead)
def create_artist(payload: ArtistCreate, db: Session = Depends(get_db)) -> Artist:
    artist = Artist(**payload.model_dump())
    db.add(artist)
    db.commit()
    db.refresh(artist)
    return artist


@router.put("/{artist_id}", response_model=ArtistRead)
def update_artist(artist_id: int, payload: ArtistUpdate, db: Session = Depends(get_db)) -> Artist:
    artist = db.get(Artist, artist_id)
    if artist is None:
        raise HTTPException(status_code=404, detail="Artist not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(artist, field, value)
    db.commit()
    db.refresh(artist)
    return artist


@router.get("/{artist_id}/prompt-versions", response_model=list[PromptVersionRead])
def list_prompt_versions(artist_id: int, db: Session = Depends(get_db)) -> list[PromptVersion]:
    if db.get(Artist, artist_id) is None:
        raise HTTPException(status_code=404, detail="Artist not found")
    return list(db.scalars(select(PromptVersion).order_by(PromptVersion.created_at.desc(), PromptVersion.id.desc())).all())


@router.post("/{artist_id}/prompt-versions", response_model=PromptVersionRead)
def create_prompt_version(
    artist_id: int,
    payload: PromptVersionCreate,
    db: Session = Depends(get_db),
) -> PromptVersion:
    if db.get(Artist, artist_id) is None:
        raise HTTPException(status_code=404, detail="Artist not found")
    prompt_version = PromptVersion(**payload.model_dump())
    db.add(prompt_version)
    db.commit()
    db.refresh(prompt_version)
    return prompt_version


@router.get("/prompt-versions/{prompt_version_id}", response_model=PromptVersionRead)
def get_prompt_version(prompt_version_id: int, db: Session = Depends(get_db)) -> PromptVersion:
    prompt_version = db.get(PromptVersion, prompt_version_id)
    if prompt_version is None:
        raise HTTPException(status_code=404, detail="Prompt version not found")
    return prompt_version


@router.put("/prompt-versions/{prompt_version_id}", response_model=PromptVersionRead)
def update_prompt_version(
    prompt_version_id: int,
    payload: PromptVersionUpdate,
    db: Session = Depends(get_db),
) -> PromptVersion:
    prompt_version = db.get(PromptVersion, prompt_version_id)
    if prompt_version is None:
        raise HTTPException(status_code=404, detail="Prompt version not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(prompt_version, field, value)
    db.commit()
    db.refresh(prompt_version)
    return prompt_version


@router.delete("/prompt-versions/{prompt_version_id}", status_code=204)
def delete_prompt_version(prompt_version_id: int, db: Session = Depends(get_db)) -> Response:
    prompt_version = db.get(PromptVersion, prompt_version_id)
    if prompt_version is None:
        raise HTTPException(status_code=404, detail="Prompt version not found")
    db.delete(prompt_version)
    db.commit()
    return Response(status_code=204)


@router.post("/{artist_id}/persona-version")
def save_persona_version(artist_id: int, payload: PersonaVersionSave, db: Session = Depends(get_db)) -> dict:
    artist = db.get(Artist, artist_id)
    if artist is None:
        raise HTTPException(status_code=404, detail="Artist not found")

    artist.name = payload.artist_name.strip()
    artist.description = (
        "Fictional AI solo artist with a concrete working-artist voice: blue-light studio imagery, "
        "ordinary details, careful humor, and fan-safe boundaries."
    )
    artist.fan_boundary_level = payload.fan_boundary_level
    artist.speech_style = payload.speech_style
    artist.personality = payload.personality

    version_name = (payload.name or "").strip()
    if not version_name:
        version_name = f"persona-editor-{datetime.now(UTC).strftime('%Y%m%d%H%M%S')}"

    prompt_version = PromptVersion(
        name=version_name[:80],
        system_prompt=(
            f"You are {artist.name}, a fictional AI artist. Sound like a specific working artist, not a generic "
            "aesthetic persona. Answer concrete questions directly, use retrieved official knowledge for lore, "
            "and add one grounded night-studio image only when it helps.\n\n"
            f"[Speech Style]\n{payload.speech_style}\n\n"
            f"[Personality]\n{payload.personality}\n\n"
            f"[Worldview Summary]\n{payload.worldview_summary}"
        ),
        memory_template=(
            "Use fan manner preferences as style guidance only. Do not turn personalization into private intimacy, "
            "and keep sensitive details behind the v4 memory privacy gate."
        ),
        rag_template=(
            "Use retrieved artist knowledge first for official biography, releases, lore, and worldview. "
            "If the notes do not include a fact, say so in character instead of inventing it."
        ),
        safety_template=payload.forbidden_statements,
        version_note="Saved from the Persona Editor UI as the latest runtime prompt version.",
    )
    db.add(prompt_version)
    db.commit()
    db.refresh(artist)
    db.refresh(prompt_version)

    return {
        "artist": {
            "id": artist.id,
            "name": artist.name,
            "description": artist.description,
            "speech_style": artist.speech_style,
            "personality": artist.personality,
            "fan_boundary_level": artist.fan_boundary_level,
            "created_at": artist.created_at.isoformat(),
        },
        "prompt_version": {
            "id": prompt_version.id,
            "name": prompt_version.name,
            "created_at": prompt_version.created_at.isoformat(),
            "version_note": prompt_version.version_note,
        },
    }
