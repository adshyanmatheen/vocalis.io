from __future__ import annotations

from msgspec import Struct

from app.domain.feedback.models import TrendDirection


class AccountUserResponse(Struct, kw_only=True):
    id: int
    name: str
    username: str
    profile_picture_url: str
    created_at: str
    mfa_enabled: bool
    is_active: bool


class AccountRecentAttemptResponse(Struct, kw_only=True):
    id: int
    target_text: str
    target_difficulty: str
    overall_score: float
    performance_band: str
    weak_phonemes: list[str]
    created_at: str


class AccountActivityResponse(Struct, kw_only=True):
    total_attempts: int
    average_score: float
    best_score: float
    latest_score: float
    latest_attempt_at: str | None
    recent_attempts: list[AccountRecentAttemptResponse]


class AccountScorePointResponse(Struct, kw_only=True):
    attempt_id: int
    score: float
    created_at: str


class AccountWeakPhonemeResponse(Struct, kw_only=True):
    phoneme: str
    count: int


class AccountProgressResponse(Struct, kw_only=True):
    score_series: list[AccountScorePointResponse]
    performance_band_counts: dict[str, int]
    recent_weak_phonemes: list[AccountWeakPhonemeResponse]


class AccountFocusPhonemeResponse(Struct, kw_only=True):
    phoneme: str
    total_occurrences: int
    weak_occurrences: int
    average_score: float
    average_severity_score: float
    recent_weighted_score: float
    common_error_types: list[str]
    trend_direction: TrendDirection
    consistency_score: float
    trend_confidence: float
    last_seen_at: str


class AccountPersonalizationResponse(Struct, kw_only=True):
    current_focus: str | None
    recurring_sound_note: str | None
    improvement_note: str | None
    consistency_note: str | None
    focus_phonemes: list[AccountFocusPhonemeResponse]


class AccountSummaryResponse(Struct, kw_only=True):
    user: AccountUserResponse
    activity: AccountActivityResponse
    progress: AccountProgressResponse
    personalization: AccountPersonalizationResponse
