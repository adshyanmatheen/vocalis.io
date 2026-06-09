from __future__ import annotations

import asyncio
import json
import logging
import random
from functools import lru_cache

from groq import Groq

from app.core.config import settings
from app.domain.feedback.constants import (
    DEFAULT_WEAK_PHONEME_LIMIT,
    DEFAULT_WEAK_WORD_LIMIT,
    ENCOURAGEMENT_MESSAGES,
    HIGH_PRIORITY_FEEDBACK_PHONEMES,
    MAX_FEEDBACK_ACTION_ITEMS,
    PERFORMANCE_BAND_SUMMARIES,
    PHONEME_ARTICULATION_HINTS,
)
from app.domain.feedback.exceptions import FeedbackGenerationError
from app.domain.feedback.models import (
    FeedbackPayload,
    WeakPhonemeFeedback,
    WeakWordFeedback,
)
from app.domain.phoneme.models import ScoringPayload

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """
You Are An Adaptive Pronunciation Coach For South Asian English Learners.

Rules:
- Speak Directly To The Learner Using "You".
- Focus Only On The Most Important Pronunciation ProblemsS.
- Mention Specific Phonemes When Relevant.
- Give Practical Articulation Advice.
- Match Your Tone To The Learner's Performance Level.
- Keep Responses Concise And Supportive.
- Return Valid JSON Only.
- Use This Schema:
{"summary":"...","action_items":["...","..."],"encouragement":"..."}
- Return Exactly 2 Action Items.
""".strip()


@lru_cache(maxsize=1)
def get_groq_client() -> Groq:
    return Groq(api_key=settings.app.groq_api_key)


def extract_weak_phonemes(
    scoring_payload: ScoringPayload, limit: int = DEFAULT_WEAK_PHONEME_LIMIT
) -> list[WeakPhonemeFeedback]:

    weakest_results = sorted(
        scoring_payload["phoneme_results"],
        key=lambda result: (
            result["phoneme_score"],
            -result["severity_score"],
        ),
    )[:limit]

    weak_phonemes: list[WeakPhonemeFeedback] = []

    for result in weakest_results:
        expected_phoneme = result["expected_phoneme"]

        weak_phonemes.append(
            {
                "phoneme": expected_phoneme,
                "word": result["word"],
                "severity": result["severity"],
                "error_type": result["error_type"],
                "phoneme_score": result["phoneme_score"],
                "articulation_hint": (
                    PHONEME_ARTICULATION_HINTS.get(
                        expected_phoneme, "Slow Down And Repeat The Sound Carefully."
                    )
                ),
            }
        )

    return weak_phonemes


def extract_weak_words(
    scoring_payload: ScoringPayload, limit: int = DEFAULT_WEAK_WORD_LIMIT
) -> list[WeakWordFeedback]:
    weakest_words = sorted(
        scoring_payload["word_scores"], key=lambda result: result["weighted_score"]
    )[:limit]
    return [
        {
            "word": result["word"],
            "weighted_score": result["weighted_score"],
            "average_confidence": result["average_confidence"],
            "performance_band": result["performance_band"],
        }
        for result in weakest_words
    ]


def derive_prioritized_phonemes(weak_phonemes: list[WeakPhonemeFeedback]) -> list[str]:

    prioritized: list[str] = []

    for result in weak_phonemes:
        phoneme = result["phoneme"]

        if phoneme in prioritized:
            continue

        prioritized.append(phoneme)

    prioritized.sort(key=lambda phoneme: phoneme not in HIGH_PRIORITY_FEEDBACK_PHONEMES)

    return prioritized


def build_summary(
    performance_band: str, weak_phonemes: list[WeakPhonemeFeedback]
) -> str:

    default_summary = PERFORMANCE_BAND_SUMMARIES.get(
        performance_band, "Your Pronunciation Needs More Practice."
    )

    if not weak_phonemes:
        return default_summary

    weakest = weak_phonemes[0]

    return (
        f"{default_summary} "
        f"The /{weakest['phoneme']}/ sound in "
        f"'{weakest['word']}' Needs The Most Attention."
    )


def build_action_items(weak_phonemes: list[WeakPhonemeFeedback]) -> list[str]:

    action_items: list[str] = []

    for result in weak_phonemes:
        phoneme = result["phoneme"]

        action_item = (
            f"Practice The /{phoneme}/ Sound In "
            f"'{result['word']}'. "
            f"{result['articulation_hint']}"
        )

        if action_item in action_items:
            continue

        action_items.append(action_item)

        if len(action_items) >= MAX_FEEDBACK_ACTION_ITEMS:
            break

    while len(action_items) < MAX_FEEDBACK_ACTION_ITEMS:
        action_items.append(
            "Repeat The Sentence Slowly And Focus On Clear Articulation."
        )

    return action_items


def build_encouragement(performance_band: str) -> str:

    encouragements = ENCOURAGEMENT_MESSAGES.get(
        performance_band,
        [
            "Keep Practicing And Stay Consistent.",
        ],
    )

    return random.choice(encouragements)


def build_fallback_feedback(*, scoring_payload: ScoringPayload) -> FeedbackPayload:
    performance_band = scoring_payload["performance_band"]
    weak_phonemes = extract_weak_phonemes(scoring_payload)

    return {
        "summary": build_summary(
            performance_band,
            weak_phonemes,
        ),
        "action_items": build_action_items(weak_phonemes),
        "encouragement": build_encouragement(performance_band),
        "feedback_provider": "fallback",
        "feedback_model": "rule-based",
    }


def build_feedback_context(
    *, target_text: str, scoring_payload: ScoringPayload
) -> dict:
    weak_phonemes = extract_weak_phonemes(scoring_payload)
    weak_words = extract_weak_words(scoring_payload)
    prioritized_phonemes = derive_prioritized_phonemes(weak_phonemes)

    return {
        "target_text": target_text,
        "overall_score": round(
            scoring_payload["overall_score"],
            4,
        ),
        "performance_band": scoring_payload["performance_band"],
        "prioritized_phonemes": prioritized_phonemes,
        "weak_phonemes": weak_phonemes,
        "weak_words": weak_words,
    }


def build_user_prompt(*, target_text: str, scoring_payload: ScoringPayload) -> str:
    feedback_context = build_feedback_context(
        target_text=target_text, scoring_payload=scoring_payload
    )
    serialized_context = json.dumps(
        feedback_context, separators=(",", ":"), ensure_ascii=True
    )

    return (
        "Use The Pronunciation Assessment JSON Below "
        "to Coach The Learner. Ground All Feedback "
        "in The Provided Phoneme And Word Scores. "
        "Only Mention Real Pronunciation Issues "
        "Supported By The Data. Return Valid JSON Only.\n"
        f"{serialized_context}"
    )


def _call_groq(*, target_text: str, scoring_payload: ScoringPayload) -> FeedbackPayload:

    response = get_groq_client().chat.completions.create(
        model=settings.app.groq_model,
        temperature=0.15,
        max_completion_tokens=220,
        messages=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT,
            },
            {
                "role": "user",
                "content": build_user_prompt(
                    target_text=target_text,
                    scoring_payload=scoring_payload,
                ),
            },
        ],
    )

    content = response.choices[0].message.content

    if not content:
        raise FeedbackGenerationError("Groq Has Returned An Empty Response.")

    parsed = json.loads(content)
    summary = str(parsed["summary"]).strip()

    action_items = [str(item).strip() for item in parsed["action_items"]][
        :MAX_FEEDBACK_ACTION_ITEMS
    ]
    encouragement = str(parsed["encouragement"]).strip()

    if len(action_items) < MAX_FEEDBACK_ACTION_ITEMS:
        raise FeedbackGenerationError("Groq Has Returned Too Few Action Items.")

    return {
        "summary": summary,
        "action_items": action_items,
        "encouragement": encouragement,
        "feedback_provider": "groq",
        "feedback_model": settings.app.groq_model,
    }


async def generate_feedback(
    *, target_text: str, scoring_payload: ScoringPayload
) -> FeedbackPayload:
    if not settings.app.use_groq or not settings.app.groq_api_key:
        return build_fallback_feedback(scoring_payload=scoring_payload)

    try:
        return await asyncio.to_thread(
            _call_groq,
            target_text=target_text,
            scoring_payload=scoring_payload,
        )

    except Exception:
        logger.exception("Groq API call failed, falling back to rule-based feedback")
        return build_fallback_feedback(scoring_payload=scoring_payload)
