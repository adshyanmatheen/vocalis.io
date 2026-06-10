from __future__ import annotations

from datetime import datetime

from sqlalchemy import (
    JSON,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    func,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
)

from app.domain.database.base import Base


class PhonemeMemory(Base):
    __tablename__ = "phoneme_memories"
    __table_args__ = (Index("idx_phoneme_memory_user_phoneme", "user_id", "phoneme"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )

    phoneme: Mapped[str] = mapped_column(String(32), nullable=False, index=True)

    total_occurrences: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    weak_occurrences: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    average_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)

    average_severity_score: Mapped[float] = mapped_column(
        Float, nullable=False, default=0.0
    )

    recent_weighted_score: Mapped[float] = mapped_column(
        Float, nullable=False, default=0.0
    )

    common_error_types: Mapped[list[str]] = mapped_column(
        JSON, nullable=False, default=list
    )

    trend_direction: Mapped[str] = mapped_column(
        String(32), nullable=False, default="stable"
    )

    consistency_score: Mapped[float] = mapped_column(Float, nullable=False, default=1.0)

    trend_confidence: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)

    last_seen_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
