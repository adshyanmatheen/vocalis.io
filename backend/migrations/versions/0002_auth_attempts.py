"""Add auth attempt tracking.

Revision ID: 0002_auth_attempts
Revises: 0001_initial_schema
Create Date: 2026-06-04

"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "0002_auth_attempts"
down_revision = "0001_initial_schema"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "auth_attempts",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("identifier", sa.String(length=255), nullable=False),
        sa.Column(
            "attempted_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_auth_attempts_attempted_at"),
        "auth_attempts",
        ["attempted_at"],
        unique=False,
    )
    op.create_index(
        op.f("ix_auth_attempts_identifier"),
        "auth_attempts",
        ["identifier"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_auth_attempts_identifier"), table_name="auth_attempts")
    op.drop_index(op.f("ix_auth_attempts_attempted_at"), table_name="auth_attempts")
    op.drop_table("auth_attempts")
