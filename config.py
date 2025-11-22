from __future__ import annotations

from functools import lru_cache
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application configuration loaded from environment variables and optional .env file.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    BOT_TOKEN: str
    MINDEE_API_KEY: str
    MINDEE_MODEL_ID: str

    UPLOAD_FOLDER: str = "data/uploads"
    ARTIFACTS_DIR: str = "data/artifacts"

    LOG_LEVEL: str = "INFO"
    LOG_ROTATE_MB: int = 10
    LOG_BACKUPS: int = 5
    LOG_CONSOLE: str = "0"
    LOG_DIR: Optional[str] = None


@lru_cache()
def get_settings() -> Settings:
    """
    Return a cached Settings instance so configuration is loaded only once.
    """
    return Settings()  # type: ignore[call-arg]


settings = get_settings()

# Validate required settings
if not settings.BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN not found or empty. Check your .env file.")

if not settings.MINDEE_API_KEY or not settings.MINDEE_API_KEY.strip():
    raise RuntimeError("MINDEE_API_KEY is not set. Please configure it in environment or .env file.")

if not settings.MINDEE_MODEL_ID or not settings.MINDEE_MODEL_ID.strip():
    raise RuntimeError("MINDEE_MODEL_ID is not set. Please configure it in environment or .env file.")

# Module-level constants for backward compatibility
BOT_TOKEN: str = settings.BOT_TOKEN
MINDEE_API_KEY: str = settings.MINDEE_API_KEY
MINDEE_MODEL_ID: str = settings.MINDEE_MODEL_ID

UPLOAD_FOLDER: str = settings.UPLOAD_FOLDER
ARTIFACTS_DIR: str = settings.ARTIFACTS_DIR

LOG_LEVEL: str = settings.LOG_LEVEL.upper()
LOG_ROTATE_MB: int = settings.LOG_ROTATE_MB
LOG_BACKUPS: int = settings.LOG_BACKUPS
LOG_CONSOLE: bool = settings.LOG_CONSOLE in ("1", "true", "True")
LOG_DIR: Optional[str] = settings.LOG_DIR
