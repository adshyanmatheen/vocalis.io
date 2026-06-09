from pathlib import Path
from typing import Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
        frozen=True,
        validate_default=True,
    )

    app_name: str = Field(
        default="vocalis.io",
    )

    environment: Literal["development", "production", "testing"] = Field(
        default="development",
    )

    debug: bool = Field(default=False)

    host: str = Field(default="0.0.0.0")

    port: int = Field(default=8000, ge=1, le=65535)

    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(  # pyrefly: ignore
        default="INFO"
    )

    cors_allowed_origins: list[str] = Field(
        default=[
            "http://localhost:5173",
            "http://127.0.0.1:5173",
            "http://localhost:3000",
            "http://127.0.0.1:3000",
            "http://localhost:3010",
            "http://127.0.0.1:3010",
        ],
    )

    database_url: str = Field()

    jwt_secret_key: str = Field()

    huggingface_model_id: str = Field(default=("matheetharanadshyan/wav2vec2-svarah"))

    huggingface_cache_dir: str = Field(default=".cache/huggingface")

    huggingface_token: str | None = Field(default=None)

    use_groq: bool = Field(default=False)

    groq_api_key: str | None = Field(default=None)

    groq_model: str = Field(default="llama-3.1-8b-instant")

    device: Literal[
        "cpu",
        "cuda",
        "mps",
    ] = Field(default="cpu")

    alignment_quantization_backend: Literal[
        "none",
        "torchao",
    ] = Field(default="none")

    sample_rate: int = Field(default=16000, ge=8000, le=48000)

    min_audio_duration_seconds: float = Field(default=0.5, gt=0)

    max_audio_duration_seconds: float = Field(default=30.0, gt=0)

    max_websocket_buffer_mb: int = Field(default=10, ge=1, le=100)

    realtime_inference_timeout_seconds: float = Field(default=20.0, gt=0)

    max_concurrent_realtime_inferences: int = Field(default=4, ge=1, le=32)

    backup_enabled: bool = Field(default=True)

    backup_directory: str = Field(default="backups")

    backup_retention_days: int = Field(default=30, ge=1)

    @field_validator("database_url", mode="before")
    @classmethod
    def normalize_sqlite_database_url(cls, value: str) -> str:
        if not isinstance(value, str):
            return value
        sqlite_prefix = "sqlite+aiosqlite:///./"
        if not value.startswith(sqlite_prefix):
            return value
        backend_root = Path(__file__).resolve().parents[3]
        relative_path = value.removeprefix(sqlite_prefix)
        database_path = (backend_root / relative_path).resolve()
        return f"sqlite+aiosqlite:///{database_path.as_posix()}"
