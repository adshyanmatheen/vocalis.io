import logging
from math import inf

import numpy as np

from app.domain.alignment.exceptions import ViterbiAlignmentError

logger = logging.getLogger(__name__)


def build_extended_alignment_sequence(
    target_token_ids: list[int],
    blank_token_id: int,
) -> list[int]:

    extended_sequence = [blank_token_id]

    for token_id in target_token_ids:
        extended_sequence.append(token_id)
        extended_sequence.append(blank_token_id)

    return extended_sequence


def compute_viterbi_alignment_path(
    log_probabilities: np.ndarray, extended_sequence: list[int], blank_token_id: int
) -> list[tuple[int, int]]:

    try:
        num_frames = log_probabilities.shape[0]
        num_states = len(extended_sequence)

        trellis = np.full((num_frames, num_states), -inf, dtype=np.float32)

        backpointers = np.full((num_frames, num_states), -1, dtype=np.int32)

        trellis[0, 0] = log_probabilities[0, blank_token_id]

        if num_states > 1:
            trellis[0, 1] = log_probabilities[0, extended_sequence[1]]

        for frame_index in range(1, num_frames):
            for state_index, token_id in enumerate(extended_sequence):
                candidate_states: list[tuple[float, int]] = [
                    (trellis[frame_index - 1, state_index], state_index)
                ]

                if state_index - 1 >= 0:
                    candidate_states.append(
                        (
                            trellis[frame_index - 1, state_index - 1],
                            state_index - 1,
                        )
                    )

                if (
                    state_index - 2 >= 0
                    and token_id != blank_token_id
                    and token_id != extended_sequence[state_index - 2]
                ):
                    candidate_states.append(
                        (trellis[frame_index - 1, state_index - 2], state_index - 2)
                    )

                (best_score, best_previous_state) = max(
                    candidate_states, key=lambda candidate: candidate[0]
                )

                trellis[frame_index, state_index] = (
                    best_score + log_probabilities[frame_index, token_id]
                )

                backpointers[frame_index, state_index] = best_previous_state

        last_state = num_states - 1

        if (
            num_states > 1
            and trellis[
                num_frames - 1,
                num_states - 2,
            ]
            > trellis[
                num_frames - 1,
                last_state,
            ]
        ):
            last_state = num_states - 2

        alignment_path: list[tuple[int, int]] = []

        current_state = last_state

        for frame_index in range(num_frames - 1, -1, -1):
            alignment_path.append((frame_index, current_state))

            previous_state = backpointers[
                frame_index,
                current_state,
            ]

            if previous_state < 0:
                break

            current_state = int(previous_state)

        alignment_path.reverse()

        return alignment_path

    except Exception as error:
        logger.exception("Viterbi alignment decoding failed")
        raise ViterbiAlignmentError("The Viterbi Alignment Decoding Failed.") from error
