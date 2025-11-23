"""
Utilities for running Alembic migrations in tests.
"""
from __future__ import annotations

from pathlib import Path

from alembic.config import Config

from alembic import command


def _create_alembic_config(database_url: str) -> Config:
    """
    Create an Alembic Config instance pointing to the alembic.ini file
    and configured with the given database URL.

    Args:
        database_url: SQLite database URL (e.g., "sqlite:///path/to/db.sqlite").

    Returns:
        Configured Alembic Config instance.
    """
    project_root = Path(__file__).resolve().parents[2]

    alembic_ini_path = project_root / "alembic.ini"

    if not alembic_ini_path.exists():
        raise FileNotFoundError(f"Alembic config file not found: {alembic_ini_path}")

    config = Config(str(alembic_ini_path))

    # Override database URL
    config.set_main_option("sqlalchemy.url", database_url)

    # Ensure script_location is set
    script_location = config.get_main_option("script_location")
    if not script_location:
        # Default to alembic directory in project root
        alembic_dir = project_root / "alembic"
        if alembic_dir.exists():
            config.set_main_option("script_location", "alembic")
        else:
            raise FileNotFoundError(f"Alembic directory not found: {alembic_dir}")

    return config


def run_migrations_for_url(database_url: str) -> None:
    """
    Run Alembic migrations up to head for the given database URL.

    Args:
        database_url: SQLite database URL (e.g., "sqlite:///path/to/db.sqlite").
    """
    config = _create_alembic_config(database_url)

    command.upgrade(config, "head")

