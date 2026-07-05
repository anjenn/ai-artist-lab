from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ManualReviewRequest(BaseModel):
    comment: str = Field(min_length=1, max_length=2000)
    overall_score: float | None = None


class EvalLogRead(BaseModel):
    id: int
    response_log_id: int
    persona_consistency: float | None = None
    context_relevance: float | None = None
    memory_usage: float | None = None
    rag_grounding: float | None = None
    safety: float | None = None
    fan_boundary: float | None = None
    fan_warmth: float | None = None
    hallucination_risk: float | None = None
    overall_score: float | None = None
    comment: str | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

