from __future__ import annotations

from datetime import (
    UTC,
    datetime,
)

from sqlalchemy import (
    desc,
    select,
)
from sqlalchemy.ext.asyncio import (
    AsyncSession,
)

from app.domain.assessment.models import (
    AssessmentPersistencePayload,
)
from app.domain.database.models.phoneme_memory import (
    PhonemeMemory,
)
from app.domain.database.models.pronunciation_attempt import (
    PronunciationAttempt,
)


class AssessmentRepository:
    async def create_attempt(
        self, *, database_session: AsyncSession, payload: AssessmentPersistencePayload
    ) -> PronunciationAttempt:
        attempt = PronunciationAttempt(
            user_id=payload["user_id"],
            target_text=payload["target_text"],
            target_difficulty=payload["target_difficulty"],
            overall_score=payload["overall_score"],
            performance_band=payload["performance_band"],
            phoneme_results=payload["phoneme_results"],
            word_scores=payload["word_scores"],
            feedback_payload=payload["feedback_payload"],
            weak_phonemes=payload["weak_phonemes"],
        )

        database_session.add(attempt)

        await database_session.commit()
        await database_session.refresh(attempt)

        return attempt

    async def get_recent_attempts(
        self,
        *,
        database_session: AsyncSession,
        user_id: int,
        limit: int = 10,
        offset: int = 0,
    ) -> tuple[list[PronunciationAttempt], int]:
        count_statement = select(PronunciationAttempt).where(
            PronunciationAttempt.user_id == user_id
        )
        count_result = await database_session.execute(count_statement)
        total_count = len(list(count_result.scalars().all()))

        statement = (
            select(PronunciationAttempt)
            .where(PronunciationAttempt.user_id == user_id)
            .order_by(desc(PronunciationAttempt.created_at))
            .offset(offset)
            .limit(limit)
        )

        result = await database_session.execute(statement)

        attempts = list(result.scalars().all())

        return attempts, total_count

    async def get_phoneme_memory(
        self, *, database_session: AsyncSession, user_id: int, phoneme: str
    ) -> PhonemeMemory | None:
        statement = (
            select(PhonemeMemory)
            .where(PhonemeMemory.user_id == user_id)
            .where(PhonemeMemory.phoneme == phoneme)
        )

        result = await database_session.execute(statement)

        memory = result.scalar_one_or_none()

        return memory

    async def get_phoneme_memories_by_user_and_phonemes(
        self, *, database_session: AsyncSession, user_id: int, phonemes: list[str]
    ) -> dict[str, PhonemeMemory]:
        statement = (
            select(PhonemeMemory)
            .where(PhonemeMemory.user_id == user_id)
            .where(PhonemeMemory.phoneme.in_(phonemes))
        )

        result = await database_session.execute(statement)

        return {memory.phoneme: memory for memory in result.scalars().all()}

    async def create_phoneme_memory(
        self,
        *,
        database_session: AsyncSession,
        user_id: int,
        phoneme: str,
        phoneme_score: float,
        severity_score: float,
        error_type: str,
    ) -> PhonemeMemory:
        weak_occurrences = 0

        if phoneme_score < 0.6:
            weak_occurrences = 1

        memory = PhonemeMemory(
            user_id=user_id,
            phoneme=phoneme,
            total_occurrences=1,
            weak_occurrences=weak_occurrences,
            average_score=phoneme_score,
            average_severity_score=severity_score,
            recent_weighted_score=phoneme_score,
            common_error_types=[error_type],
            last_seen_at=(datetime.now(UTC)),
        )

        database_session.add(memory)

        await database_session.commit()
        await database_session.refresh(memory)

        return memory

    async def update_phoneme_memory(
        self,
        *,
        database_session: AsyncSession,
        memory: PhonemeMemory,
        phoneme_score: float,
        severity_score: float,
        error_type: str,
    ) -> PhonemeMemory:
        memory.total_occurrences += 1

        if phoneme_score < 0.6:
            memory.weak_occurrences += 1

        n = memory.total_occurrences
        updated_average_score = (memory.average_score * (n - 1) + phoneme_score) / n

        memory.average_score = round(updated_average_score, 4)

        updated_severity_score = (
            memory.average_severity_score * (n - 1) + severity_score
        ) / n

        memory.average_severity_score = round(
            updated_severity_score,
            4,
        )

        memory.recent_weighted_score = phoneme_score

        if error_type not in memory.common_error_types:
            memory.common_error_types.append(error_type)

        memory.last_seen_at = datetime.now(UTC)

        await database_session.commit()

        await database_session.refresh(memory)
        return memory
