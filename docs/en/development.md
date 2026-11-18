<img src="https://capsule-render.vercel.app/api?type=waving&color=gradient&customColorList=12,16,20&height=120&section=header&text=Development+Guide&fontSize=40&animation=fadeIn"/>

<div align="center">

[![Alembic](https://img.shields.io/badge/Migrations-Alembic-orange?style=for-the-badge)](https://alembic.sqlalchemy.org/)
[![SQLite](https://img.shields.io/badge/Database-SQLite-blue?style=for-the-badge&logo=sqlite)](https://www.sqlite.org/)
[![CI/CD](https://img.shields.io/badge/Pipeline-GitHub%20Actions-green?style=for-the-badge&logo=github)](https://github.com/features/actions)

</div>

## Interface translations

To add a language, copy [the English catalog](../../backend/handlers/locales/en.json) to a file named for the new two-letter ISO 639-1 code, such as `nl.json`. Translate the values and preserve the keys and format placeholders. Then register the code and its native name in `LANGUAGES` in [`texts.py`](../../backend/handlers/texts.py). The picker and Telegram command menu use that registry.

## 🗄️ Database migrations

The project uses Alembic to manage the SQLite schema.

### How the schema is applied

At runtime the database schema is created or upgraded by calling `backend.storage.db.init_db()`.
It uses the Alembic Python API to upgrade to `head`. The equivalent CLI command is:

```powershell
python -m alembic -c backend/alembic.ini upgrade head
```

Every entrypoint that needs a database should call `init_db()` once before using the storage layer.

### Running migrations locally

From the project root, set `BOT_TOKEN` in `.env` or in the environment, then run:

```powershell
python -m alembic -c backend/alembic.ini upgrade head
```

This upgrades the database pointed to by `backend.storage.db.DB_PATH` to the latest migration.

### Creating a new migration

When you change the database schema, you must add a new Alembic migration.

The recommended workflow is:

1. Edit the schema in code only after the migration is created and applied.

2. Create a new migration file:

   ```powershell
   python -m alembic -c backend/alembic.ini revision -m "describe_change"
   ```

3. Edit the generated revision file in `backend/alembic/versions/` and write the `upgrade` and `downgrade` functions using raw SQL for SQLite.

4. Apply the migration:

   ```powershell
   python -m alembic -c backend/alembic.ini upgrade head
   ```

SQLite support is limited for automatic schema diffs, so migrations are written by hand.

### Migrations and tests

Tests that rely on the database use the same migrations:

* `backend.storage.db.DB_PATH` can be patched to point to a temporary file.

* `backend.storage.db.init_db()` is called to apply all migrations to that temporary database.

Storage integration tests use the Alembic revisions against temporary SQLite databases.

### Docker and migrations

The Docker entrypoint applies the migrations before starting the bot:

```powershell
python -m alembic -c backend/alembic.ini upgrade head
python bot.py
```

## CI pipeline

On pushes to `main` or `master` and pull requests targeting either branch, [CI](../../.github/workflows/ci.yml) uses Python 3.11, installs `.[dev]`, applies migrations with a test token, and runs pre-commit and mypy. It then runs two test groups:

```bash
pytest --import-mode=importlib -m "not storage_db"
pytest --import-mode=importlib -m "storage_db" --no-cov
```

[Coverage](../../.github/workflows/coverage.yml) enforces a minimum of 80%. [Docker Build](../../.github/workflows/docker.yml) and [Compose](../../.github/workflows/docker-compose.yml) check image and container setup. The Docker healthcheck verifies Python imports. [Docs](../../.github/workflows/docs.yml) checks links when documentation changes. [Security](../../.github/workflows/security.yml) runs Bandit, pip-audit, and Trivy on the same branches and weekly.

[Release](../../.github/workflows/release.yml) publishes the Docker image to GHCR for `v*` tags using `GITHUB_TOKEN`. It creates a GitHub Release only for tags matching `vX.0.0`.
