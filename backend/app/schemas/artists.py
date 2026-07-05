from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ArtistRead(BaseModel):
    id: int
    name: str
    description: str | None = None
    speech_style: str | None = None
    personality: str | None = None
    fan_boundary_level: str | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ArtistCreate(BaseModel):
    name: str
    description: str | None = None
    speech_style: str | None = None
    personality: str | None = None
    fan_boundary_level: str | None = "Warm distance"


class ArtistUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    speech_style: str | None = None
    personality: str | None = None
    fan_boundary_level: str | None = None
