from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class FanMemoryCreate(BaseModel):
    artist_id: int = 1
    memory_type: str = Field(min_length=1, max_length=80)
    content: str = Field(min_length=1, max_length=2000)
    confidence: float = 0.7
    sensitivity: str = "low"
    source_message_id: int | None = None


class FanMemoryPreviewRequest(BaseModel):
    memory_type: str = Field(default="preference", min_length=1, max_length=80)
    content: str = Field(min_length=1, max_length=2000)
    confidence: float = 0.7


class FanMemoryUpdate(BaseModel):
    memory_type: str | None = Field(default=None, min_length=1, max_length=80)
    content: str | None = Field(default=None, min_length=1, max_length=2000)
    confidence: float | None = None
    sensitivity: str | None = None


class FanMemoryRead(BaseModel):
    id: int
    fan_id: int
    artist_id: int
    memory_type: str
    content: str
    confidence: float
    sensitivity: str
    source_message_id: int | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
