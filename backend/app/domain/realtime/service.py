from __future__ import annotations

from collections import Counter
from typing import Any

import msgspec
import numpy as np

from app.domain.alignment.service import AlignmentService
from app.domain.feedback.constants import (
    MAX_FEEDBACK_ACTION_ITEMS,
    PHONEME_ARTICULATION_HINTS,
)
from app.domain.phoneme.models import ScoringPayload
from app.domain.phoneme.scoring import performance_band_from_score
from app.domain.phoneme.service import PhonemeService
from app.domain.phoneme.utils import extract_weak_phonemes


def _normalize_word_score_keys(word_scores: list[dict[str, Any]]) -> None:
    for ws in word_scores:
        if not isinstance(ws, dict):
            continue
        if "weighted_score" not in ws and "score" in ws:
            ws["weighted_score"] = ws["score"]
        if "score" not in ws and "weighted_score" in ws:
            ws["score"] = ws["weighted_score"]


class RealtimeAssessmentService:
    def __init__(self, phoneme_service: PhonemeService | None = None) -> None:
        self.phoneme = phoneme_service or PhonemeService()

    def build_word_segments(
        self, *, waveform: np.ndarray, target_text: str
    ) -> list[dict[str, Any]]:
        alignment_result = AlignmentService.align_target_text(
            processed_audio=waveform,
            target_text=target_text,
        )

        return [
            {
                "text": word_segment.text,
                "word": word_segment.text,
                "start_time": word_segment.start_time,
                "end_time": word_segment.end_time,
                "confidence": word_segment.confidence,
            }
            for word_segment in alignment_result.word_segments
        ]

    def process_audio_window(
        self,
        *,
        waveform: np.ndarray,
        target_text: str,
        sample_rate: int,
    ) -> ScoringPayload:
        word_segments = self.build_word_segments(
            waveform=waveform,
            target_text=target_text,
        )

        return self.phoneme.analyze_pronunciation(
            target_text=target_text,
            word_segments=word_segments,
            audio_waveform=waveform,
            sample_rate=sample_rate,
        )

    def build_partial_feedback(
        self, *, scoring_payload: dict[str, Any]
    ) -> dict[str, Any]:
        return {
            "overall_score": scoring_payload["overall_score"],
            "weak_phonemes": extract_weak_phonemes(
                phoneme_results=scoring_payload["phoneme_results"]
            ),
            "word_scores": msgspec.to_builtins(scoring_payload["word_scores"]),
            "performance_band": scoring_payload["performance_band"],
        }

    def build_encouragement(
        self, *, performance_band: str, weak_phoneme_count: int
    ) -> str:
        if performance_band == "Excellent":
            return "Excellent precision. Keep this pace and challenge yourself with longer phrases."

        if performance_band == "Strong":
            return "Strong performance. A few focused repetitions will push this to excellent."

        if performance_band == "On Track":
            return "Good momentum. Keep practicing consistently to improve clarity and stability."

        if performance_band == "Needs More Practice":
            if weak_phoneme_count > 0:
                return "Progress is building. Focus on the suggested phonemes and repeat short drills."
            return "Progress is building. Keep steady practice to strengthen pronunciation confidence."

        if weak_phoneme_count > 0:
            return "Keep going. Slow, deliberate repetition on the focus phonemes will help quickly."

        return "Keep going. Consistent short sessions will improve control and pronunciation accuracy."

    def build_word_diagnostics(
        self, *, word_scores: list[dict[str, Any]]
    ) -> dict[str, Any]:
        sorted_words = sorted(
            word_scores,
            key=lambda item: float(item.get("weighted_score", item.get("score", 0.0))),
        )
        ndigits = 4
        weakest_words = [
            {
                "word": str(item.get("word", "")),
                "score": round(
                    float(item.get("weighted_score", item.get("score", 0.0))),
                    ndigits,
                ),
                "phoneme_count": int(item.get("phoneme_count", 0)),
            }
            for item in sorted_words[:3]
        ]
        strongest_words = [
            {
                "word": str(item.get("word", "")),
                "score": round(
                    float(item.get("weighted_score", item.get("score", 0.0))),
                    ndigits,
                ),
                "phoneme_count": int(item.get("phoneme_count", 0)),
            }
            for item in list(reversed(sorted_words[-3:]))
        ]
        return {
            "weakest_words": weakest_words,
            "strongest_words": strongest_words,
        }

    def build_error_breakdown(
        self, *, phoneme_results: list[dict[str, Any]]
    ) -> dict[str, Any]:
        error_type_counts = Counter(
            str(result.get("error_type", "unknown")) for result in phoneme_results
        )
        severity_counts = Counter(
            str(result.get("severity", "unknown")) for result in phoneme_results
        )
        total_errors = len(phoneme_results)

        return {
            "total_scored_phonemes": total_errors,
            "error_types": dict(error_type_counts),
            "severity_distribution": dict(severity_counts),
        }

    def build_coaching_plan(self, *, weak_phonemes: list[str]) -> list[str]:
        if not weak_phonemes:
            return [
                "Keep pace steady and record a longer sentence to validate consistency.",
                "Repeat one challenge phrase 3 times and keep articulation crisp.",
            ]

        drills = [
            f"Practice isolated repetitions of /{phoneme}/ for 30-45 seconds."
            for phoneme in weak_phonemes[:2]
        ]
        drills.append(
            "Read the full target sentence slowly, then at natural pace, while preserving phoneme clarity."
        )
        return drills

    def build_action_items(
        self,
        *,
        phoneme_results: list[dict[str, Any]],
        weak_phonemes: list[str],
    ) -> list[str]:
        weakest_results = sorted(
            (
                result
                for result in phoneme_results
                if str(result.get("expected_phoneme", "")) in weak_phonemes
            ),
            key=lambda result: float(result.get("phoneme_score", 0.0)),
        )
        action_items: list[str] = []
        covered_phonemes: set[str] = set()

        for result in weakest_results:
            phoneme = str(result.get("expected_phoneme", "")).strip()
            if not phoneme or phoneme in covered_phonemes:
                continue

            word = str(result.get("word", "")).strip()
            score = float(result.get("phoneme_score", 0.0))
            hint = PHONEME_ARTICULATION_HINTS.get(
                phoneme, "Slow down and repeat the sound carefully."
            )
            if word:
                action_item = (
                    f"Train /{phoneme}/ in '{word}' (score {score:.2f}). {hint}"
                )
            else:
                action_item = f"Train /{phoneme}/ (score {score:.2f}). {hint}"

            action_items.append(action_item)
            covered_phonemes.add(phoneme)

            if len(action_items) >= MAX_FEEDBACK_ACTION_ITEMS:
                break

        while len(action_items) < MAX_FEEDBACK_ACTION_ITEMS:
            if weak_phonemes:
                focus = weak_phonemes[len(action_items) % len(weak_phonemes)]
                action_items.append(
                    f"Repeat short minimal pairs with /{focus}/ and keep articulation deliberate."
                )
            else:
                action_items.append(
                    "Repeat the full sentence slowly, then once at natural pace with clear enunciation."
                )

        return action_items

    def build_summary(
        self,
        *,
        overall_score: float,
        performance_band: str,
        weak_phonemes: list[str],
        word_scores: list[dict[str, Any]],
    ) -> str:
        score_pct = round(overall_score * 100)
        weakest_words = [
            str(item.get("word", "")).strip()
            for item in self.build_word_diagnostics(word_scores=word_scores)[
                "weakest_words"
            ]
            if str(item.get("word", "")).strip()
        ]
        focus_sounds = ", ".join(f"/{phoneme}/" for phoneme in weak_phonemes[:3])

        if weakest_words:
            if len(weakest_words) == 1:
                word_clause = f' "{weakest_words[0]}" struggled most'
            elif len(weakest_words) == 2:
                word_clause = (
                    f' "{weakest_words[0]}" and "{weakest_words[1]}" struggled most'
                )
            else:
                word_clause = (
                    f' "{weakest_words[0]}", "{weakest_words[1]}", '
                    f'and "{weakest_words[2]}" struggled most'
                )
        else:
            word_clause = ""

        if not weak_phonemes:
            if score_pct >= 80:
                return (
                    f"At {score_pct}%, you held {performance_band.lower()} clarity with no "
                    "flagged sound gaps. Keep this articulation and add a little speed next round."
                )
            return (
                f"You scored {score_pct}% ({performance_band}) without a dominant weak sound—"
                "clarity may be pacing or vowel shape. Slow the line slightly and stress each "
                "syllable on the way out."
            )

        if word_clause:
            word_clause = f";{word_clause}."

        if score_pct >= 75:
            return f"Strong {score_pct}% run. Polish {focus_sounds}{word_clause}"

        if score_pct >= 50:
            return (
                f"{score_pct}% puts you in {performance_band} territory. Lead with "
                f"{focus_sounds}{word_clause or '; drill each sound in isolation, then read the full line at half speed.'}"
            )

        return (
            f"{score_pct}%—articulation is being pulled down by {focus_sounds}"
            f"{word_clause or '.'} Work the top sound slowly, then replay the full passage once."
        )

    def build_completion_feedback(
        self, *, scoring_payload: dict[str, Any], duration_seconds: float
    ) -> dict[str, Any]:
        weak_phonemes = extract_weak_phonemes(
            phoneme_results=scoring_payload["phoneme_results"]
        )
        phoneme_results = msgspec.to_builtins(scoring_payload["phoneme_results"])
        overall_score = float(scoring_payload["overall_score"])
        performance_band = str(scoring_payload["performance_band"])
        word_scores = msgspec.to_builtins(scoring_payload["word_scores"])
        weak_phoneme_count = len(weak_phonemes)
        practiced_word_count = len(word_scores)
        pronunciation_accuracy = round(overall_score * 100, 1)
        average_word_confidence = (
            sum(float(item.get("average_confidence", 0.0)) for item in word_scores)
            / practiced_word_count
            if practiced_word_count
            else 0.0
        )

        summary = self.build_summary(
            overall_score=overall_score,
            performance_band=performance_band,
            weak_phonemes=weak_phonemes,
            word_scores=word_scores,
        )

        return {
            "summary": summary,
            "action_items": self.build_action_items(
                phoneme_results=phoneme_results,
                weak_phonemes=weak_phonemes,
            ),
            "encouragement": self.build_encouragement(
                performance_band=performance_band,
                weak_phoneme_count=weak_phoneme_count,
            ),
            "feedback_provider": "vocalis-realtime",
            "feedback_model": "wav2vec2-phoneme",
            "metrics": {
                "overall_score": round(overall_score, 4),
                "accuracy_percent": pronunciation_accuracy,
                "performance_band": performance_band,
                "weak_phoneme_count": weak_phoneme_count,
                "practiced_word_count": practiced_word_count,
                "average_word_confidence": round(average_word_confidence, 4),
                "speech_pace_wpm": round(
                    (practiced_word_count / duration_seconds) * 60, 2
                )
                if duration_seconds > 0
                else 0.0,
            },
            "highlights": {
                "top_weak_phonemes": weak_phonemes[:5],
                "next_focus": weak_phonemes[:3],
                "has_weak_phonemes": weak_phoneme_count > 0,
            },
            "word_diagnostics": self.build_word_diagnostics(word_scores=word_scores),
            "error_breakdown": self.build_error_breakdown(
                phoneme_results=phoneme_results
            ),
            "coaching_plan": self.build_coaching_plan(weak_phonemes=weak_phonemes),
            "realtime": {
                "duration_seconds": round(duration_seconds, 4),
                "source": "websocket_pcm16",
            },
        }

    def aggregate_scoring_windows(
        self, *, scoring_windows: list[dict[str, Any]]
    ) -> dict[str, Any]:
        if not scoring_windows:
            return {
                "phoneme_results": [],
                "word_scores": [],
                "overall_score": 0.0,
                "performance_band": "Needs Careful Practice",
            }

        phoneme_results: list[dict[str, Any]] = []
        word_scores: list[dict[str, Any]] = []

        for scoring_window in scoring_windows:
            phoneme_results.extend(scoring_window.get("phoneme_results", []))
            word_scores.extend(scoring_window.get("word_scores", []))

        _normalize_word_score_keys(word_scores)

        overall_score = sum(
            float(window.get("overall_score", 0.0)) for window in scoring_windows
        ) / len(scoring_windows)

        return {
            "phoneme_results": phoneme_results,
            "word_scores": word_scores,
            "overall_score": round(overall_score, 4),
            "performance_band": str(performance_band_from_score(overall_score)),
        }


realtime_assessment_service = RealtimeAssessmentService()
