from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

BACKEND_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_ROOT))

from app.domain.alignment.engine import load_alignment_model_bundle  # noqa: E402
from app.domain.phoneme.engine import load_phoneme_model_bundle  # noqa: E402
from app.domain.realtime.service import RealtimeAssessmentService  # noqa: E402


def build_synthetic_waveform() -> np.ndarray:
    sample_rate = 16_000
    duration_seconds = 1.0
    time_axis = np.linspace(
        0,
        duration_seconds,
        int(sample_rate * duration_seconds),
        endpoint=False,
    )

    return (0.2 * np.sin(2 * np.pi * 220 * time_axis)).astype(np.float32)


def main() -> None:
    alignment_bundle = load_alignment_model_bundle()
    phoneme_bundle = load_phoneme_model_bundle()
    service = RealtimeAssessmentService()

    scoring_payload = service.process_audio_window(
        waveform=build_synthetic_waveform(),
        target_text="The quick brown fox",
        sample_rate=16_000,
    )

    print(
        json.dumps(
            {
                "alignment_device": alignment_bundle.inference_device,
                "phoneme_device": str(phoneme_bundle.device),
                "overall_score": scoring_payload["overall_score"],
                "performance_band": scoring_payload["performance_band"],
                "phoneme_result_count": len(scoring_payload["phoneme_results"]),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
