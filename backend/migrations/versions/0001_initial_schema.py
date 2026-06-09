"""Initial schema.

Revision ID: 0001_initial_schema
Revises: None
Create Date: 2026-06-04

"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "0001_initial_schema"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(length=32), nullable=False),
        sa.Column("username", sa.String(length=64), nullable=False),
        sa.Column("avatar_url", sa.String(length=512), nullable=False),
        sa.Column("password_hash", sa.String(length=512), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("mfa_enabled", sa.Boolean(), nullable=False),
        sa.Column("mfa_secret", sa.String(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_users_username"), "users", ["username"], unique=True)

    op.create_table(
        "mfa_challenges",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("token_hash", sa.String(length=64), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("used_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_mfa_challenges_token_hash"),
        "mfa_challenges",
        ["token_hash"],
        unique=True,
    )
    op.create_index(
        op.f("ix_mfa_challenges_user_id"),
        "mfa_challenges",
        ["user_id"],
        unique=False,
    )

    op.create_table(
        "phoneme_memories",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("phoneme", sa.String(length=32), nullable=False),
        sa.Column("total_occurrences", sa.Integer(), nullable=False),
        sa.Column("weak_occurrences", sa.Integer(), nullable=False),
        sa.Column("average_score", sa.Float(), nullable=False),
        sa.Column("average_severity_score", sa.Float(), nullable=False),
        sa.Column("recent_weighted_score", sa.Float(), nullable=False),
        sa.Column("common_error_types", sa.JSON(), nullable=False),
        sa.Column("trend_direction", sa.String(length=32), nullable=False),
        sa.Column("consistency_score", sa.Float(), nullable=False),
        sa.Column("trend_confidence", sa.Float(), nullable=False),
        sa.Column(
            "last_seen_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_phoneme_memories_phoneme"),
        "phoneme_memories",
        ["phoneme"],
        unique=False,
    )
    op.create_index(
        op.f("ix_phoneme_memories_user_id"),
        "phoneme_memories",
        ["user_id"],
        unique=False,
    )

    op.create_table(
        "pronunciation_attempts",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("target_text", sa.Text(), nullable=False),
        sa.Column("target_difficulty", sa.String(length=32), nullable=False),
        sa.Column("overall_score", sa.Float(), nullable=False),
        sa.Column("performance_band", sa.String(length=32), nullable=False),
        sa.Column("phoneme_results", sa.JSON(), nullable=False),
        sa.Column("word_scores", sa.JSON(), nullable=False),
        sa.Column("feedback_payload", sa.JSON(), nullable=False),
        sa.Column("weak_phonemes", sa.JSON(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_pronunciation_attempts_user_id"),
        "pronunciation_attempts",
        ["user_id"],
        unique=False,
    )

    op.create_table(
        "sessions",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("session_token", sa.String(length=512), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_sessions_session_token"),
        "sessions",
        ["session_token"],
        unique=True,
    )
    op.create_index(op.f("ix_sessions_user_id"), "sessions", ["user_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_sessions_user_id"), table_name="sessions")
    op.drop_index(op.f("ix_sessions_session_token"), table_name="sessions")
    op.drop_table("sessions")
    op.drop_index(
        op.f("ix_pronunciation_attempts_user_id"),
        table_name="pronunciation_attempts",
    )
    op.drop_table("pronunciation_attempts")
    op.drop_index(op.f("ix_phoneme_memories_user_id"), table_name="phoneme_memories")
    op.drop_index(op.f("ix_phoneme_memories_phoneme"), table_name="phoneme_memories")
    op.drop_table("phoneme_memories")
    op.drop_index(op.f("ix_mfa_challenges_user_id"), table_name="mfa_challenges")
    op.drop_index(op.f("ix_mfa_challenges_token_hash"), table_name="mfa_challenges")
    op.drop_table("mfa_challenges")
    op.drop_index(op.f("ix_users_username"), table_name="users")
    op.drop_table("users")
