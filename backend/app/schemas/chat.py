from pydantic import BaseModel, Field


class ChatStreamRequest(BaseModel):
    artist_id: int = Field(default=1)
    fan_id: int = Field(default=1)
    conversation_id: int = Field(default=1)
    message: str = Field(min_length=1, max_length=4000)

