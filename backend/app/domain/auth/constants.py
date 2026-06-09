from __future__ import annotations

import re

MIN_NAME_LENGTH = 2
MAX_NAME_LENGTH = 32

MIN_PASSWORD_LENGTH = 8
PASSWORD_REQUIRE_UPPERCASE = True
PASSWORD_REQUIRE_LOWERCASE = True
PASSWORD_REQUIRE_DIGIT = True

ACCESS_TOKEN_DURATION_MINUTES = 15
REFRESH_TOKEN_DURATION_DAYS = 7

ACCESS_TOKEN_COOKIE_NAME = "access_token"
REFRESH_TOKEN_COOKIE_NAME = "refresh_token"

AUTH_RATE_LIMIT_ATTEMPTS = 5
AUTH_RATE_LIMIT_WINDOW_SECONDS = 300

MFA_ISSUER_NAME = "Vocalis.io"
MFA_CODE_VALID_WINDOW = 0
MFA_CHALLENGE_DURATION_MINUTES = 5
MFA_RATE_LIMIT_ATTEMPTS = 5
MFA_RATE_LIMIT_WINDOW_SECONDS = 300

NAME_PATTERN = re.compile(r"^[A-Za-z\s]{2,32}$")

PASSWORD_UPPERCASE_PATTERN = re.compile(r"[A-Z]")
PASSWORD_LOWERCASE_PATTERN = re.compile(r"[a-z]")
PASSWORD_DIGIT_PATTERN = re.compile(r"\d")

INVALID_NAME_MESSAGE = (
    "Your Name Must Be 2 To 32 Characters And Contain Only Letters and Spaces."
)
PASSWORD_LENGTH_MESSAGE = "Your Password Must Be At Least 8 Characters Long."
PASSWORD_UPPERCASE_MESSAGE = "Your Password Must Include At Least One Uppercase Letter."
PASSWORD_LOWERCASE_MESSAGE = "Your Password Must Include At Least One Lowercase Letter."
PASSWORD_DIGIT_MESSAGE = "Your Password Must Include At Least One Number."
RATE_LIMIT_MESSAGE = "There Were Too Many Sign-In Attempts. Please Try Again After Waiting A Few Minutes."

USERNAME_ADJECTIVES = [
    "ancient",
    "arcane",
    "astral",
    "atomic",
    "aurora",
    "autumn",
    "blazing",
    "bold",
    "brisk",
    "celestial",
    "chaotic",
    "chromatic",
    "cinder",
    "cosmic",
    "crimson",
    "crystal",
    "cyber",
    "dancing",
    "dark",
    "dawn",
    "desert",
    "divine",
    "dreamy",
    "drifting",
    "echo",
    "electric",
    "ember",
    "emerald",
    "epic",
    "eternal",
    "fabled",
    "fierce",
    "flaming",
    "flickering",
    "floating",
    "frozen",
    "galactic",
    "gentle",
    "ghost",
    "glacial",
    "glowing",
    "golden",
    "hidden",
    "hollow",
    "icy",
    "infinite",
    "iron",
    "jade",
    "jolly",
    "lively",
    "lunar",
    "magic",
    "midnight",
    "misty",
    "mystic",
    "neon",
    "night",
    "nova",
    "obsidian",
    "ocean",
    "phantom",
    "plasma",
    "polar",
    "quantum",
    "quiet",
    "radiant",
    "rapid",
    "rising",
    "royal",
    "sacred",
    "scarlet",
    "shadow",
    "shimmering",
    "silent",
    "silver",
    "sky",
    "solar",
    "spectral",
    "spiral",
    "stellar",
    "storm",
    "sunset",
    "swift",
    "thunder",
    "titan",
    "twilight",
    "velvet",
    "vibrant",
    "violet",
    "virtual",
    "wandering",
    "whispering",
    "wild",
    "winter",
    "woodland",
    "zen",
]

USERNAME_ANIMALS = [
    "badger",
    "bear",
    "buffalo",
    "cobra",
    "cougar",
    "crane",
    "crow",
    "dolphin",
    "dragon",
    "eagle",
    "falcon",
    "ferret",
    "fox",
    "gecko",
    "griffin",
    "hawk",
    "heron",
    "husky",
    "hyena",
    "jaguar",
    "koala",
    "kraken",
    "leopard",
    "lion",
    "lynx",
    "mamba",
    "mongoose",
    "narwhal",
    "octopus",
    "orca",
    "otter",
    "owl",
    "panther",
    "parrot",
    "peacock",
    "phoenix",
    "puma",
    "rabbit",
    "raccoon",
    "raven",
    "rhino",
    "scorpion",
    "serpent",
    "shark",
    "sparrow",
    "spider",
    "stag",
    "tiger",
    "viper",
    "whale",
    "wolf",
    "wolverine",
    "yak",
]

DICEBEAR_BASE_URL = "https://api.dicebear.com/9.x/glass/svg"

DEFAULT_AVATAR_STYLE = "glass"
DEFAULT_AVATAR_BACKGROUND_TYPE = "gradientLinear"
DEFAULT_AVATAR_RADIUS = 50
DEFAULT_AVATAR_SIZE = 128
