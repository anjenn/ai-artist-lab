from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


def _strip_or_none(value: str | None) -> str | None:
    if value is None:
        return None
    stripped = value.strip()
    return stripped or None


def _strip_required(value: str | None) -> str:
    if value is None:
        raise ValueError("value is required")
    stripped = value.strip()
    if not stripped:
        raise ValueError("value cannot be blank")
    return stripped


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
    name: str = Field(min_length=1, max_length=120)
    description: str | None = Field(default=None, max_length=2000)
    speech_style: str | None = Field(default=None, max_length=2000)
    personality: str | None = Field(default=None, max_length=2000)
    fan_boundary_level: str | None = Field(default="Warm distance", max_length=80)

    @field_validator("name", mode="before")
    @classmethod
    def strip_required_name(cls, value: str | None) -> str:
        return _strip_required(value)

    @field_validator("description", "speech_style", "personality", "fan_boundary_level", mode="before")
    @classmethod
    def strip_text(cls, value: str | None) -> str | None:
        return _strip_or_none(value)


class ArtistUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    description: str | None = Field(default=None, max_length=2000)
    speech_style: str | None = Field(default=None, max_length=2000)
    personality: str | None = Field(default=None, max_length=2000)
    fan_boundary_level: str | None = Field(default=None, max_length=80)

    @field_validator("name", mode="before")
    @classmethod
    def strip_required_name_when_present(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return _strip_required(value)

    @field_validator("description", "speech_style", "personality", "fan_boundary_level", mode="before")
    @classmethod
    def strip_text(cls, value: str | None) -> str | None:
        return _strip_or_none(value)


class PersonaVersionSave(BaseModel):
    name: str | None = Field(default=None, max_length=80)
    artist_name: str = Field(min_length=1, max_length=120)
    fan_boundary_level: str = Field(default="Warm distance", min_length=1, max_length=80)
    speech_style: str = Field(min_length=1, max_length=2000)
    personality: str = Field(min_length=1, max_length=2000)
    forbidden_statements: str = Field(min_length=1, max_length=2000)
    worldview_summary: str = Field(min_length=1, max_length=2000)

    @field_validator("artist_name", "fan_boundary_level", "speech_style", "personality", "forbidden_statements", "worldview_summary", mode="before")
    @classmethod
    def strip_required_text(cls, value: str | None) -> str:
        return _strip_required(value)

    @field_validator(
        "name",
        mode="before",
    )
    @classmethod
    def strip_optional_name(cls, value: str | None) -> str | None:
        return _strip_or_none(value)


class PromptVersionRead(BaseModel):
    id: int
    name: str
    system_prompt: str
    memory_template: str | None = None
    rag_template: str | None = None
    safety_template: str | None = None
    version_note: str | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PromptVersionCreate(BaseModel):
    name: str = Field(min_length=1, max_length=80)
    system_prompt: str = Field(min_length=1, max_length=4000)
    memory_template: str | None = Field(default=None, max_length=3000)
    rag_template: str | None = Field(default=None, max_length=3000)
    safety_template: str | None = Field(default=None, max_length=3000)
    version_note: str | None = Field(default=None, max_length=2000)

    @field_validator("name", "system_prompt", mode="before")
    @classmethod
    def strip_required_text(cls, value: str | None) -> str:
        return _strip_required(value)

    @field_validator("memory_template", "rag_template", "safety_template", "version_note", mode="before")
    @classmethod
    def strip_text(cls, value: str | None) -> str | None:
        return _strip_or_none(value)


class PromptVersionUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=80)
    system_prompt: str | None = Field(default=None, min_length=1, max_length=4000)
    memory_template: str | None = Field(default=None, max_length=3000)
    rag_template: str | None = Field(default=None, max_length=3000)
    safety_template: str | None = Field(default=None, max_length=3000)
    version_note: str | None = Field(default=None, max_length=2000)

    @field_validator("name", "system_prompt", mode="before")
    @classmethod
    def strip_required_text_when_present(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return _strip_required(value)

    @field_validator("memory_template", "rag_template", "safety_template", "version_note", mode="before")
    @classmethod
    def strip_text(cls, value: str | None) -> str | None:
        return _strip_or_none(value)
