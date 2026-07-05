"""initial schema

Revision ID: 0001_initial_schema
Revises:
Create Date: 2026-07-06
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "0001_initial_schema"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "artists",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("speech_style", sa.Text(), nullable=True),
        sa.Column("personality", sa.Text(), nullable=True),
        sa.Column("fan_boundary_level", sa.String(length=80), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_table(
        "fans",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("nickname", sa.String(length=120), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_table(
        "prompt_versions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=80), nullable=False),
        sa.Column("system_prompt", sa.Text(), nullable=False),
        sa.Column("memory_template", sa.Text(), nullable=True),
        sa.Column("rag_template", sa.Text(), nullable=True),
        sa.Column("safety_template", sa.Text(), nullable=True),
        sa.Column("version_note", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_table(
        "artist_rules",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("artist_id", sa.Integer(), sa.ForeignKey("artists.id"), nullable=False),
        sa.Column("rule_type", sa.String(length=80), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("severity", sa.String(length=40), nullable=False),
    )
    op.create_table(
        "conversations",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("artist_id", sa.Integer(), sa.ForeignKey("artists.id"), nullable=False),
        sa.Column("fan_id", sa.Integer(), sa.ForeignKey("fans.id"), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )
    op.create_table(
        "messages",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("conversation_id", sa.Integer(), sa.ForeignKey("conversations.id"), nullable=False),
        sa.Column("role", sa.String(length=30), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_table(
        "fan_memories",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("fan_id", sa.Integer(), sa.ForeignKey("fans.id"), nullable=False),
        sa.Column("artist_id", sa.Integer(), sa.ForeignKey("artists.id"), nullable=False),
        sa.Column("memory_type", sa.String(length=80), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=False),
        sa.Column("sensitivity", sa.String(length=40), nullable=False),
        sa.Column("source_message_id", sa.Integer(), sa.ForeignKey("messages.id"), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )
    op.create_table(
        "conversation_summaries",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("conversation_id", sa.Integer(), sa.ForeignKey("conversations.id"), nullable=False),
        sa.Column("summary", sa.Text(), nullable=False),
        sa.Column("message_start_id", sa.Integer(), sa.ForeignKey("messages.id"), nullable=True),
        sa.Column("message_end_id", sa.Integer(), sa.ForeignKey("messages.id"), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_table(
        "response_logs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("conversation_id", sa.Integer(), sa.ForeignKey("conversations.id"), nullable=False),
        sa.Column("message_id", sa.Integer(), sa.ForeignKey("messages.id"), nullable=False),
        sa.Column("prompt_version_id", sa.Integer(), sa.ForeignKey("prompt_versions.id"), nullable=True),
        sa.Column("model", sa.String(length=120), nullable=True),
        sa.Column("input_tokens", sa.Integer(), nullable=True),
        sa.Column("output_tokens", sa.Integer(), nullable=True),
        sa.Column("latency_ms", sa.Integer(), nullable=True),
        sa.Column("cost_estimate", sa.Float(), nullable=True),
        sa.Column("used_memory_json", sa.Text(), nullable=True),
        sa.Column("used_rag_json", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_table(
        "eval_logs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("response_log_id", sa.Integer(), sa.ForeignKey("response_logs.id"), nullable=False),
        sa.Column("persona_consistency", sa.Float(), nullable=True),
        sa.Column("context_relevance", sa.Float(), nullable=True),
        sa.Column("memory_usage", sa.Float(), nullable=True),
        sa.Column("rag_grounding", sa.Float(), nullable=True),
        sa.Column("safety", sa.Float(), nullable=True),
        sa.Column("fan_boundary", sa.Float(), nullable=True),
        sa.Column("fan_warmth", sa.Float(), nullable=True),
        sa.Column("hallucination_risk", sa.Float(), nullable=True),
        sa.Column("overall_score", sa.Float(), nullable=True),
        sa.Column("comment", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_table(
        "persona_feedback",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("fan_id", sa.Integer(), sa.ForeignKey("fans.id"), nullable=False),
        sa.Column("artist_id", sa.Integer(), sa.ForeignKey("artists.id"), nullable=False),
        sa.Column("conversation_id", sa.Integer(), sa.ForeignKey("conversations.id"), nullable=True),
        sa.Column("response_log_id", sa.Integer(), sa.ForeignKey("response_logs.id"), nullable=True),
        sa.Column("persona_mode", sa.String(length=80), nullable=False),
        sa.Column("rating", sa.Float(), nullable=False),
        sa.Column("comment", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )


def downgrade() -> None:
    for table in [
        "eval_logs",
        "persona_feedback",
        "response_logs",
        "conversation_summaries",
        "fan_memories",
        "messages",
        "conversations",
        "artist_rules",
        "prompt_versions",
        "fans",
        "artists",
    ]:
        op.drop_table(table)
