from __future__ import annotations

import asyncio
from collections import Counter

from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.database.models.phoneme_memory import PhonemeMemory
from app.domain.database.models.pronunciation_attempt import PronunciationAttempt
from app.domain.database.models.user import User
from app.domain.feedback.personalization import (
    build_consistency_summary,
    build_trend_summary,
)
from app.schemas.responses.account import (
    AccountActivityResponse,
    AccountFocusPhonemeResponse,
    AccountPersonalizationResponse,
    AccountProgressResponse,
    AccountRecentAttemptResponse,
    AccountScorePointResponse,
    AccountSummaryResponse,
    AccountUserResponse,
    AccountWeakPhonemeResponse,
)


class AccountRepository:
    async def build_summary(
        self, *, database_session: AsyncSession, user: User, recent_limit: int = 12
    ) -> AccountSummaryResponse:
        recent_attempts = await self.get_recent_attempts(
            database_session=database_session,
            user_id=user.id,
            limit=recent_limit,
        )

        activity, progress, personalization = await asyncio.gather(
            self.build_activity(
                database_session=database_session,
                user_id=user.id,
                recent_attempts=recent_attempts,
            ),
            self.build_progress(
                database_session=database_session,
                user_id=user.id,
                recent_attempts=recent_attempts,
            ),
            self.build_personalization(
                database_session=database_session,
                user_id=user.id,
            ),
        )

        return AccountSummaryResponse(
            user=AccountUserResponse(
                id=user.id,
                name=user.name,
                username=user.username,
                avatar_url=user.avatar_url,
                created_at=str(user.created_at),
                mfa_enabled=user.mfa_enabled,
                is_active=user.is_active,
            ),
            activity=activity,
            progress=progress,
            personalization=personalization,
        )

    async def get_recent_attempts(
        self, *, database_session: AsyncSession, user_id: int, limit: int
    ) -> list[PronunciationAttempt]:
        statement = (
            select(PronunciationAttempt)
            .where(PronunciationAttempt.user_id == user_id)
            .order_by(
                desc(PronunciationAttempt.created_at), desc(PronunciationAttempt.id)
            )
            .limit(limit)
        )
        result = await database_session.execute(statement)
        return list(result.scalars().all())

    async def build_activity(
        self,
        *,
        database_session: AsyncSession,
        user_id: int,
        recent_attempts: list[PronunciationAttempt],
    ) -> AccountActivityResponse:
        statement = select(
            func.count(PronunciationAttempt.id),
            func.avg(PronunciationAttempt.overall_score),
            func.max(PronunciationAttempt.overall_score),
        ).where(PronunciationAttempt.user_id == user_id)
        result = await database_session.execute(statement)
        total_attempts, average_score, best_score = result.one()
        latest_attempt = recent_attempts[0] if recent_attempts else None

        return AccountActivityResponse(
            total_attempts=int(total_attempts or 0),
            average_score=round(float(average_score or 0.0), 4),
            best_score=round(float(best_score or 0.0), 4),
            latest_score=round(float(latest_attempt.overall_score), 4)
            if latest_attempt
            else 0.0,
            latest_attempt_at=str(latest_attempt.created_at)
            if latest_attempt
            else None,
            recent_attempts=[
                AccountRecentAttemptResponse(
                    id=attempt.id,
                    target_text=attempt.target_text,
                    target_difficulty=attempt.target_difficulty,
                    overall_score=round(float(attempt.overall_score), 4),
                    performance_band=attempt.performance_band,
                    weak_phonemes=list(attempt.weak_phonemes or []),
                    created_at=str(attempt.created_at),
                )
                for attempt in recent_attempts
            ],
        )

    async def build_progress(
        self,
        *,
        database_session: AsyncSession,
        user_id: int,
        recent_attempts: list[PronunciationAttempt],
    ) -> AccountProgressResponse:
        band_statement = (
            select(
                PronunciationAttempt.performance_band,
                func.count(PronunciationAttempt.id),
            )
            .where(PronunciationAttempt.user_id == user_id)
            .group_by(PronunciationAttempt.performance_band)
        )
        band_result = await database_session.execute(band_statement)
        band_counts = {
            str(performance_band): int(count)
            for performance_band, count in band_result.all()
        }

        weak_counter: Counter[str] = Counter()
        for attempt in recent_attempts:
            weak_counter.update(attempt.weak_phonemes or [])

        return AccountProgressResponse(
            score_series=[
                AccountScorePointResponse(
                    attempt_id=attempt.id,
                    score=round(float(attempt.overall_score), 4),
                    created_at=str(attempt.created_at),
                )
                for attempt in reversed(recent_attempts)
            ],
            performance_band_counts=band_counts,
            recent_weak_phonemes=[
                AccountWeakPhonemeResponse(phoneme=phoneme, count=count)
                for phoneme, count in weak_counter.most_common(6)
            ],
        )

    async def build_personalization(
        self, *, database_session: AsyncSession, user_id: int, limit: int = 6
    ) -> AccountPersonalizationResponse:
        statement = (
            select(PhonemeMemory)
            .where(PhonemeMemory.user_id == user_id)
            .order_by(
                desc(PhonemeMemory.weak_occurrences),
                PhonemeMemory.average_score,
                desc(PhonemeMemory.last_seen_at),
            )
            .limit(limit)
        )
        result = await database_session.execute(statement)
        memories = list(result.scalars().all())

        focus_phonemes = [
            AccountFocusPhonemeResponse(
                phoneme=memory.phoneme,
                total_occurrences=memory.total_occurrences,
                weak_occurrences=memory.weak_occurrences,
                average_score=round(float(memory.average_score), 4),
                average_severity_score=round(float(memory.average_severity_score), 4),
                recent_weighted_score=round(float(memory.recent_weighted_score), 4),
                common_error_types=list(memory.common_error_types or []),
                trend_direction=memory.trend_direction,
                consistency_score=round(float(memory.consistency_score), 4),
                trend_confidence=round(float(memory.trend_confidence), 4),
                last_seen_at=str(memory.last_seen_at),
            )
            for memory in memories
        ]

        if not focus_phonemes:
            return AccountPersonalizationResponse(
                current_focus=None,
                recurring_sound_note=None,
                improvement_note=None,
                consistency_note=None,
                focus_phonemes=[],
            )

        primary_focus = focus_phonemes[0]

        return AccountPersonalizationResponse(
            current_focus=primary_focus.phoneme,
            recurring_sound_note=(
                f"You repeatedly struggle with the /{primary_focus.phoneme}/ sound."
            ),
            improvement_note=build_trend_summary(
                phoneme=primary_focus.phoneme,
                trend_direction=primary_focus.trend_direction,
            ),
            consistency_note=build_consistency_summary(
                phoneme=primary_focus.phoneme,
                consistency_direction="improving"
                if primary_focus.consistency_score >= 0.8
                else "declining"
                if primary_focus.consistency_score <= 0.45
                else "stable",
            ),
            focus_phonemes=focus_phonemes,
        )
