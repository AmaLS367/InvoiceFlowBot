from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
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

    DB_FILENAME: str = Field("data.sqlite", alias="INVOICE_DB_PATH")
    DB_DIR: Path = Field(
        default_factory=lambda: Path(__file__).resolve().parent,
        alias="DB_DIR",
    )


@lru_cache()
def get_settings() -> Settings:
    return Settings()  # type: ignore[call-arg]


settings = get_settings()

# Validate required settings
if not settings.BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN not found or empty. Check your .env file.")

if not settings.MINDEE_API_KEY or not settings.MINDEE_API_KEY.strip():
    raise RuntimeError(
        "MINDEE_API_KEY is not set. Please configure it in environment or .env file."
    )

if not settings.MINDEE_MODEL_ID or not settings.MINDEE_MODEL_ID.strip():
    raise RuntimeError(
        "MINDEE_MODEL_ID is not set. Please configure it in environment or .env file."
    )

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

# Database configuration
BASE_DIR: Path = settings.DB_DIR
DB_PATH: str = str(BASE_DIR / settings.DB_FILENAME)
