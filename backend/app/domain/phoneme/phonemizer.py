from __future__ import annotations

import logging
from functools import lru_cache

from g2p_en import G2p

from app.domain.phoneme.constants import PHONEME_MODEL_WARMUP_TEXT
from app.domain.phoneme.exceptions import PhonemizationError

logger = logging.getLogger(__name__)


def resource_exists(nltk_module, resource_paths: tuple[str, ...]) -> bool:

    for resource_path in resource_paths:
        try:
            nltk_module.data.find(resource_path)

        except LookupError:
            continue

        else:
            return True

    return False


def ensure_nltk_resource(
    nltk_module, *, resource_paths: tuple[str, ...], download_names: tuple[str, ...]
) -> None:

    if resource_exists(nltk_module, resource_paths):
        return

    for download_name in download_names:
        nltk_module.download(download_name, quiet=True)

        if resource_exists(nltk_module, resource_paths):
            return

    raise PhonemizationError("The Required NLTK Resources Could Not Be Loaded.")


@lru_cache(maxsize=1)
def ensure_nltk_resources() -> None:

    import nltk

    ensure_nltk_resource(
        nltk,
        resource_paths=("corpora/cmudict", "corpora/cmudict/"),
        download_names=("cmudict",),
    )

    ensure_nltk_resource(
        nltk,
        resource_paths=("taggers/averaged_perceptron_tagger_eng/",),
        download_names=("averaged_perceptron_tagger_eng",),
    )


@lru_cache(maxsize=1)
def get_g2p() -> G2p:
    try:
        ensure_nltk_resources()
        g2p = G2p()

        g2p(PHONEME_MODEL_WARMUP_TEXT)
        return g2p

    except Exception as error:
        logger.exception("Failed to initialize G2P engine")
        raise PhonemizationError(
            "Failed To Initialize The Grapheme-To-Phoneme Engine."
        ) from error


def normalize_phoneme(phoneme: str) -> str:
    return "".join(character for character in phoneme if not character.isdigit())


@lru_cache(maxsize=512)
def phonemize_text(text: str) -> list[list[str]]:

    try:
        g2p = get_g2p()
        words = [word for word in text.strip().split() if word]
        phoneme_words: list[list[str]] = []

        for word in words:
            phonemes = [token for token in g2p(word) if token and token != " "]
            normalized_phonemes = [normalize_phoneme(phoneme) for phoneme in phonemes]

            cleaned_phonemes = [phoneme for phoneme in normalized_phonemes if phoneme]

            phoneme_words.append(cleaned_phonemes)

        return phoneme_words

    except Exception as error:
        logger.exception("Failed to convert text into phoneme sequences")
        raise PhonemizationError(
            "Failed To Convert Text Into Phoneme Sequences."
        ) from error
