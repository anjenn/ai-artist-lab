from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ConversationCreate(BaseModel):
    artist_id: int = Field(default=1, ge=1)
    fan_id: int = Field(default=1, ge=1)


class ConversationRead(BaseModel):
    id: int
    artist_id: int
    fan_id: int
    message_count: int = 0
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
