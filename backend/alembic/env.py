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
    Tests can override with config.set_main_option("sqlalchemy.url", "sqlite:///path" or "sqlite:///:memory:").
    """
    url_from_config = config.get_main_option("sqlalchemy.url")
    if url_from_config:
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
    # Use url_from_config when set (tests or explicit override); otherwise use app DB_PATH
    if url_from_config:
        url_str: str = url_from_config
        if ":memory:" in url_str:
            configuration = config.get_section(config.config_ini_section) or {}
            configuration["sqlalchemy.url"] = url_str
            connectable = engine_from_config(
                configuration,
                prefix="sqlalchemy.",
                poolclass=pool.NullPool,
            )
        else:
            # File path: extract path and use creator so SQLite creates the file
            path_str = url_str.replace("sqlite:///", "").replace("sqlite://", "")
            path_obj = Path(path_str)
            if not path_obj.is_absolute():
                # Resolve relative to the directory containing alembic.ini so
                # "data.sqlite" in backend/alembic.ini -> backend/data.sqlite
                config_dir = Path(config.config_file_name or "").resolve().parent
                path_obj = (config_dir / path_str).resolve()
            path_obj.parent.mkdir(parents=True, exist_ok=True)

            def _sqlite_creator():
                return sqlite3.connect(str(path_obj))

            connectable = create_engine(
                "sqlite://",
                creator=_sqlite_creator,
                poolclass=pool.NullPool,
            )
    else:
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
