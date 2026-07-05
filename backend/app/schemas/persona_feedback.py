from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class PersonaFeedbackCreate(BaseModel):
    fan_id: int = Field(default=1, ge=1)
    artist_id: int = Field(default=1, ge=1)
    conversation_id: int | None = None
    response_log_id: int | None = None
    persona_mode: str = Field(min_length=1, max_length=80)
    rating: float = Field(ge=1, le=5)
    comment: str | None = Field(default=None, max_length=2000)


class PersonaFeedbackRead(BaseModel):
    id: int
    fan_id: int
    artist_id: int
    conversation_id: int | None = None
    response_log_id: int | None = None
    persona_mode: str
    rating: float
    comment: str | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
