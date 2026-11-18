from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Literal, Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_DIR = Path(__file__).resolve().parent


def resolve_db_path(db_path_value: str) -> Path:
    """
    Resolve the SQLite path from INVOICE_DB_PATH.

    Relative paths are interpreted relative to the backend directory so the default
    "../data.sqlite" points to the project/app root in both local and Docker runs.
    """
    raw_path = Path(db_path_value)
    if raw_path.is_absolute():
        return raw_path
    return (BACKEND_DIR / raw_path).resolve()


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    BOT_TOKEN: str
    OCR_PROVIDER: Literal["local", "mindee"] = "local"
    OCR_LANGUAGES: str = "eng+rus"
    MINDEE_API_KEY: str = ""
    MINDEE_MODEL_ID: str = ""

    UPLOAD_FOLDER: str = "data/uploads"
    ARTIFACTS_DIR: str = "data/artifacts"

    LOG_LEVEL: str = "INFO"
    LOG_ROTATE_MB: int = 10
    LOG_BACKUPS: int = 5
    LOG_CONSOLE: str = "0"
    LOG_DIR: Optional[str] = None

    INVOICE_DB_PATH: str = Field("../data.sqlite", alias="INVOICE_DB_PATH")


@lru_cache()
def get_settings() -> Settings:
    return Settings()  # type: ignore[call-arg]


settings = get_settings()

# Validate required settings
if not settings.BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN not found or empty. Check your .env file.")

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
DB_PATH: str = str(resolve_db_path(settings.INVOICE_DB_PATH))
