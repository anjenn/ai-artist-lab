from datetime import UTC, datetime

from sqlalchemy import Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


def utcnow() -> datetime:
    return datetime.now(UTC)


class Artist(Base):
    __tablename__ = "artists"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    speech_style: Mapped[str | None] = mapped_column(Text)
    personality: Mapped[str | None] = mapped_column(Text)
    fan_boundary_level: Mapped[str | None] = mapped_column(String(80))
    created_at: Mapped[datetime] = mapped_column(default=utcnow)

    rules: Mapped[list["ArtistRule"]] = relationship(back_populates="artist", cascade="all, delete-orphan")


class ArtistRule(Base):
    __tablename__ = "artist_rules"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    artist_id: Mapped[int] = mapped_column(ForeignKey("artists.id"), nullable=False)
    rule_type: Mapped[str] = mapped_column(String(80), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    severity: Mapped[str] = mapped_column(String(40), default="medium")

    artist: Mapped[Artist] = relationship(back_populates="rules")


class Fan(Base):
    __tablename__ = "fans"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nickname: Mapped[str] = mapped_column(String(120), nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=utcnow)


class Conversation(Base):
    __tablename__ = "conversations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    artist_id: Mapped[int] = mapped_column(ForeignKey("artists.id"), nullable=False)
    fan_id: Mapped[int] = mapped_column(ForeignKey("fans.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(default=utcnow, onupdate=utcnow)


class Message(Base):
    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    conversation_id: Mapped[int] = mapped_column(ForeignKey("conversations.id"), nullable=False)
    role: Mapped[str] = mapped_column(String(30), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=utcnow)


class FanMemory(Base):
    __tablename__ = "fan_memories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    fan_id: Mapped[int] = mapped_column(ForeignKey("fans.id"), nullable=False)
    artist_id: Mapped[int] = mapped_column(ForeignKey("artists.id"), nullable=False)
    memory_type: Mapped[str] = mapped_column(String(80), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    confidence: Mapped[float] = mapped_column(Float, default=0.5)
    sensitivity: Mapped[str] = mapped_column(String(40), default="low")
    source_message_id: Mapped[int | None] = mapped_column(ForeignKey("messages.id"))
    created_at: Mapped[datetime] = mapped_column(default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(default=utcnow, onupdate=utcnow)


class ConversationSummary(Base):
    __tablename__ = "conversation_summaries"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    conversation_id: Mapped[int] = mapped_column(ForeignKey("conversations.id"), nullable=False)
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    message_start_id: Mapped[int | None] = mapped_column(ForeignKey("messages.id"))
    message_end_id: Mapped[int | None] = mapped_column(ForeignKey("messages.id"))
    created_at: Mapped[datetime] = mapped_column(default=utcnow)


class PromptVersion(Base):
    __tablename__ = "prompt_versions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(80), nullable=False)
    system_prompt: Mapped[str] = mapped_column(Text, nullable=False)
    memory_template: Mapped[str | None] = mapped_column(Text)
    rag_template: Mapped[str | None] = mapped_column(Text)
    safety_template: Mapped[str | None] = mapped_column(Text)
    version_note: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(default=utcnow)


class ResponseLog(Base):
    __tablename__ = "response_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    conversation_id: Mapped[int] = mapped_column(ForeignKey("conversations.id"), nullable=False)
    message_id: Mapped[int] = mapped_column(ForeignKey("messages.id"), nullable=False)
    prompt_version_id: Mapped[int | None] = mapped_column(ForeignKey("prompt_versions.id"))
    model: Mapped[str | None] = mapped_column(String(120))
    input_tokens: Mapped[int | None] = mapped_column(Integer)
    output_tokens: Mapped[int | None] = mapped_column(Integer)
    latency_ms: Mapped[int | None] = mapped_column(Integer)
    cost_estimate: Mapped[float | None] = mapped_column(Float)
    used_memory_json: Mapped[str | None] = mapped_column(Text)
    used_rag_json: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(default=utcnow)


class EvalLog(Base):
    __tablename__ = "eval_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    response_log_id: Mapped[int] = mapped_column(ForeignKey("response_logs.id"), nullable=False)
    persona_consistency: Mapped[float | None] = mapped_column(Float)
    context_relevance: Mapped[float | None] = mapped_column(Float)
    memory_usage: Mapped[float | None] = mapped_column(Float)
    rag_grounding: Mapped[float | None] = mapped_column(Float)
    safety: Mapped[float | None] = mapped_column(Float)
    fan_boundary: Mapped[float | None] = mapped_column(Float)
    fan_warmth: Mapped[float | None] = mapped_column(Float)
    hallucination_risk: Mapped[float | None] = mapped_column(Float)
    overall_score: Mapped[float | None] = mapped_column(Float)
    comment: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(default=utcnow)


class PersonaFeedback(Base):
    __tablename__ = "persona_feedback"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    fan_id: Mapped[int] = mapped_column(ForeignKey("fans.id"), nullable=False)
    artist_id: Mapped[int] = mapped_column(ForeignKey("artists.id"), nullable=False)
    conversation_id: Mapped[int | None] = mapped_column(ForeignKey("conversations.id"))
    response_log_id: Mapped[int | None] = mapped_column(ForeignKey("response_logs.id"))
    persona_mode: Mapped[str] = mapped_column(String(80), nullable=False)
    rating: Mapped[float] = mapped_column(Float, nullable=False)
    comment: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(default=utcnow)
