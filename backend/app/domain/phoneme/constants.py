PHONEME_MODEL_NAME = "vitouphy/wav2vec2-xls-r-300m-timit-phoneme"

PHONEME_MODEL_SAMPLE_RATE = 16_000

PHONEME_MODEL_WARMUP_TEXT = "warmup"

PHONEME_CONFIDENCE_PRECISION = 4

PHONEME_TIMESTAMP_PRECISION = 4

MINIMUM_PHONEME_CONFIDENCE = 0.0

MAXIMUM_PHONEME_CONFIDENCE = 1.0

DEFAULT_PHONEME_SOURCE = "wav2vec2_phoneme_inference"

EXPECTED_PHONEME_SOURCE = "expected_phoneme_estimation"

PREDICTED_PHONEME_SOURCE = "predicted_phoneme_decoding"

SUPPORTED_ESPEAK_LIBRARY_PATHS = (
    "/opt/homebrew/lib/libespeak-ng.dylib",
    "/usr/local/lib/libespeak-ng.dylib",
    "/usr/lib/x86_64-linux-gnu/libespeak-ng.so.1",
    "/usr/lib/aarch64-linux-gnu/libespeak-ng.so.1",
)

PHONEME_CONFUSIONS: dict[str, list[str]] = {
    "P": ["B", "F"],
    "B": ["P", "V"],
    "F": ["P", "V"],
    "V": ["B", "F", "W"],
    "TH": ["S", "T", "D"],
    "DH": ["D", "Z", "TH"],
    "S": ["SH", "TH"],
    "Z": ["S", "DH"],
    "SH": ["S", "CH"],
    "CH": ["SH", "JH"],
    "R": ["L", "W"],
    "L": ["R"],
    "T": ["D", "TH"],
    "D": ["T", "DH"],
    "K": ["G"],
    "G": ["K"],
    "W": ["V", "B"],
}

IGNORED_PHONEME_TOKENS = {
    "[PAD]",
    "[UNK]",
    "|",
}

PHONEME_VOWELS = {
    "AA",
    "AE",
    "AH",
    "AO",
    "AW",
    "AY",
    "EH",
    "ER",
    "EY",
    "IH",
    "IY",
    "OW",
    "OY",
    "UH",
    "UW",
}

PHONEME_CONSONANTS = {
    "B",
    "CH",
    "D",
    "DH",
    "F",
    "G",
    "HH",
    "JH",
    "K",
    "L",
    "M",
    "N",
    "NG",
    "P",
    "R",
    "S",
    "SH",
    "T",
    "TH",
    "V",
    "W",
    "Y",
    "Z",
    "ZH",
}

HIGH_IMPORTANCE_PHONEMES = {
    "R",
    "L",
    "TH",
    "DH",
    "V",
    "W",
    "SH",
    "ZH",
    "CH",
    "JH",
}

MAXIMUM_PHONEME_SEQUENCE_LENGTH = 512

MINIMUM_WORD_DURATION_SECONDS = 0.05

MINIMUM_PHONEME_DURATION_SECONDS = 0.02

DEFAULT_PHONEME_CONFIDENCE = 0.0

DEFAULT_PHONEME_SEVERITY = "severe"

DEFAULT_MATCH_OVERLAP_THRESHOLD = 0.35

DISTORTION_CONFIDENCE_THRESHOLD = 0.70

PHONEME_ERROR_WEIGHTS = {
    "none": 0.0,
    "distortion": 0.20,
    "substitution": 0.35,
    "deletion": 0.55,
    "insertion": 0.35,
}

PHONEME_SEVERITY_WEIGHT = 0.75

EXCELLENT_SCORE_THRESHOLD = 0.90

STRONG_SCORE_THRESHOLD = 0.75

ON_TRACK_THRESHOLD = 0.60

NEEDS_MORE_PRACTICE_THRESHOLD = 0.40

MILD_SEVERITY_THRESHOLD = 0.25

MODERATE_SEVERITY_THRESHOLD = 0.50

SEVERE_SEVERITY_THRESHOLD = 0.75
