from functools import lru_cache

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """All configuration comes from environment variables or a .env file."""

    model_config = SettingsConfigDict(
        env_file=("../.env", ".env"), env_file_encoding="utf-8", extra="ignore"
    )

    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "gemma4:e4b"
    ollama_timeout_seconds: float = 120.0

    # Speech-to-text (faster-whisper). Models download into whisper_model_dir on first use.
    whisper_model: str = "small"
    whisper_model_dir: str = ".models"

    database_url: str = "sqlite:///./paperwork.db"

    # Shared family access code. The web app sends it on every request.
    access_code: SecretStr = SecretStr("")

    max_image_bytes: int = 10 * 1024 * 1024
    max_audio_bytes: int = 10 * 1024 * 1024

    cors_origins: list[str] = ["http://localhost:3000"]


@lru_cache
def get_settings() -> Settings:
    return Settings()
