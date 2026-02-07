from __future__ import annotations

import sqlite3
from logging.config import fileConfig
from pathlib import Path

from alembic import context
from sqlalchemy import create_engine, engine_from_config, pool

from backend.storage.db import DB_PATH

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = None


def get_url() -> str:
    """
    Database URL for migrations. Uses DB_PATH from app config so we migrate the same DB the app uses.
    Tests can override with config.set_main_option("sqlalchemy.url", "sqlite:///:memory:").
    """
    url_from_config = config.get_main_option("sqlalchemy.url")
    if url_from_config and ":memory:" in url_from_config:
        return url_from_config
    db_path = Path(DB_PATH).resolve()
    return f"sqlite:///{db_path.as_posix()}"


def run_migrations_offline() -> None:
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    url_from_config = config.get_main_option("sqlalchemy.url")
    # Prefer app DB_PATH so we migrate the same DB the app uses (alembic.ini may have a different path)
    use_app_path = True
    if url_from_config and ":memory:" in url_from_config:
        use_app_path = False  # tests override with in-memory DB
    if use_app_path:
        db_path = Path(DB_PATH).resolve()
        db_path.parent.mkdir(parents=True, exist_ok=True)
        path_str = str(db_path)

        def _sqlite_creator():
            return sqlite3.connect(path_str)

        connectable = create_engine(
            "sqlite://",
            creator=_sqlite_creator,
            poolclass=pool.NullPool,
        )
    else:
        configuration = config.get_section(config.config_ini_section) or {}
        configuration["sqlalchemy.url"] = url_from_config
        connectable = engine_from_config(
            configuration,
            prefix="sqlalchemy.",
            poolclass=pool.NullPool,
        )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
