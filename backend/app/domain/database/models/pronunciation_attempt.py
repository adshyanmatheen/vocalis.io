from __future__ import annotations

from datetime import datetime

from sqlalchemy import (
    JSON,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
)

from app.domain.database import Base


class PronunciationAttempt(Base):
    __tablename__ = "pronunciation_attempts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )

    target_text: Mapped[str] = mapped_column(Text, nullable=False)

    target_difficulty: Mapped[str] = mapped_column(String(32), nullable=False)

    overall_score: Mapped[float] = mapped_column(Float, nullable=False)

    performance_band: Mapped[str] = mapped_column(String(32), nullable=False)

    phoneme_results: Mapped[dict] = mapped_column(JSON, nullable=False)

    word_scores: Mapped[dict] = mapped_column(JSON, nullable=False)

    feedback_payload: Mapped[dict] = mapped_column(JSON, nullable=False)

    weak_phonemes: Mapped[list[str]] = mapped_column(JSON, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
