"""Add performance indexes.

Revision ID: 0003_add_indexes
Revises: 0002_auth_attempts
Create Date: 2026-06-10

"""

from __future__ import annotations

from alembic import op

revision = "0003_add_indexes"
down_revision = "0002_auth_attempts"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_index(
        op.f("ix_pronunciation_attempts_created_at"),
        "pronunciation_attempts",
        ["created_at"],
        unique=False,
    )
    op.create_index(
        "idx_phoneme_memory_user_phoneme",
        "phoneme_memories",
        ["user_id", "phoneme"],
        unique=False,
    )
    op.create_index(
        op.f("ix_sessions_expires_at"),
        "sessions",
        ["expires_at"],
        unique=False,
    )
    op.create_index(
        op.f("ix_mfa_challenges_expires_at"),
        "mfa_challenges",
        ["expires_at"],
        unique=False,
    )
    op.create_index(
        op.f("ix_mfa_challenges_used_at"),
        "mfa_challenges",
        ["used_at"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_mfa_challenges_used_at"), table_name="mfa_challenges")
    op.drop_index(op.f("ix_mfa_challenges_expires_at"), table_name="mfa_challenges")
    op.drop_index(op.f("ix_sessions_expires_at"), table_name="sessions")
    op.drop_index("idx_phoneme_memory_user_phoneme", table_name="phoneme_memories")
    op.drop_index(
        op.f("ix_pronunciation_attempts_created_at"),
        table_name="pronunciation_attempts",
    )
