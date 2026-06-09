import numpy as np

from app.domain.alignment.decoder import perform_forced_alignment
from app.domain.alignment.models import AlignmentResult


class AlignmentService:
    @staticmethod
    def align_target_text(
        processed_audio: np.ndarray, target_text: str
    ) -> AlignmentResult:

        return perform_forced_alignment(
            processed_audio=processed_audio, target_text=target_text
        )
