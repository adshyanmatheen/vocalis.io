from __future__ import annotations

MAX_FEEDBACK_ACTION_ITEMS = 2

DEFAULT_WEAK_PHONEME_LIMIT = 6
DEFAULT_WEAK_WORD_LIMIT = 4

IMPROVEMENT_DELTA_THRESHOLD = 0.08
DECLINE_DELTA_THRESHOLD = -0.08

HIGH_CONSISTENCY_THRESHOLD = 0.82
LOW_CONSISTENCY_THRESHOLD = 0.58

HIGH_TREND_CONFIDENCE_THRESHOLD = 0.8
MEDIUM_TREND_CONFIDENCE_THRESHOLD = 0.55

RECENT_PHONEME_TREND_LIMIT = 16

PHONEME_MEMORY_DECAY_FACTOR = 0.72

WEAK_PHONEME_SCORE_THRESHOLD = 0.75

MODERATE_SEVERITY_THRESHOLD = 0.55

HIGH_PRIORITY_FEEDBACK_PHONEMES = {
    "R",
    "L",
    "TH",
    "DH",
    "SH",
    "CH",
    "V",
    "W",
}

PHONEME_ARTICULATION_HINTS: dict[str, str] = {
    "R": "Curl your tongue slightly without touching the roof of your mouth.",
    "L": "Let the tip of your tongue briefly touch behind your upper teeth.",
    "TH": "Place your tongue gently between your teeth and push air forward.",
    "DH": "Voice the TH sound while keeping your tongue lightly between your teeth.",
    "SH": "Round your lips slightly and push air smoothly forward.",
    "CH": "Start with a stop sound and release into SH smoothly.",
    "V": "Touch your lower lip lightly against your upper teeth and vibrate your voice.",
    "W": "Round your lips tightly before releasing the sound.",
}

PERFORMANCE_BAND_SUMMARIES: dict[str, str] = {
    "Excellent": "Your pronunciation was very clear and consistent.",
    "Strong": "Your pronunciation was strong overall with only minor issues.",
    "On Track": "Your pronunciation is improving, but some sounds still need refinement.",
    "Needs More Practice": "Several sounds need more careful pronunciation practice.",
    "Needs Careful Practice": "You should slow down and focus carefully on difficult sounds.",
}

TREND_DIRECTION_LABELS: dict[str, str] = {
    "improving": "improving",
    "stable": "stable",
    "declining": "declining",
}

CONSISTENCY_DIRECTION_LABELS: dict[str, str] = {
    "improving": "becoming more consistent",
    "stable": "remaining relatively stable",
    "declining": "still inconsistent",
}

ENCOURAGEMENT_MESSAGES: dict[str, list[str]] = {
    "Excellent": [
        "You are speaking very confidently now.",
        "Your pronunciation control is becoming very strong.",
    ],
    "Strong": [
        "You are making strong pronunciation progress.",
        "Your articulation is becoming clearer and more natural.",
    ],
    "On Track": [
        "You are steadily improving with practice.",
        "Your pronunciation is moving in the right direction.",
    ],
    "Needs More Practice": [
        "Keep practicing slowly and carefully.",
        "Repetition and slower pacing will help you improve.",
    ],
    "Needs Careful Practice": [
        "Focus on one sound at a time and avoid rushing.",
        "Careful repetition will help strengthen your pronunciation.",
    ],
}
