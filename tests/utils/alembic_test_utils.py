from __future__ import annotations

from pathlib import Path

from alembic import command
from alembic.config import Config


def _create_alembic_config(database_url: str) -> Config:
    project_root = Path(__file__).resolve().parents[2]

    alembic_ini_path = project_root / "backend" / "alembic.ini"

    if not alembic_ini_path.exists():
        raise FileNotFoundError(f"Alembic config file not found: {alembic_ini_path}")

    config = Config(str(alembic_ini_path))

    config.set_main_option("sqlalchemy.url", database_url)

    script_location = config.get_main_option("script_location")
    if not script_location:
        alembic_dir = project_root / "backend" / "alembic"
        if alembic_dir.exists():
            config.set_main_option("script_location", "backend/alembic")
        else:
            raise FileNotFoundError(f"Alembic directory not found: {alembic_dir}")

    return config


def run_migrations_for_url(database_url: str) -> None:
    config = _create_alembic_config(database_url)

    command.upgrade(config, "head")
