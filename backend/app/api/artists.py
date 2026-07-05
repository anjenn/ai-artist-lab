"""Artist profile endpoints for persona configuration."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.models import Artist
from app.db.session import get_db
from app.schemas.artists import ArtistCreate, ArtistRead, ArtistUpdate

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
