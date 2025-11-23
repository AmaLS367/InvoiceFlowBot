# Development Guide

## Database migrations

The project uses Alembic to manage the SQLite schema.

### How the schema is applied

At runtime the database schema is created or upgraded by calling `storage.db.init_db()`.
This function is a thin wrapper around:

```powershell
python -m alembic upgrade head
```

Every entrypoint that needs a database should call `init_db()` once before using the storage layer.

### Running migrations locally

To make sure your local database is up to date, run:

```powershell
python -m alembic upgrade head
```

This upgrades the database pointed to by `storage.db.DB_PATH` to the latest migration.

### Creating a new migration

When you change the database schema, you must add a new Alembic migration.

The recommended workflow is:

1. Edit the schema in code only after the migration is created and applied.

2. Create a new migration file:

   ```powershell
   python -m alembic revision -m "describe_change"
   ```

3. Edit the generated revision file in `alembic/versions/` and write the `upgrade` and `downgrade` functions using raw SQL for SQLite.

4. Apply the migration:

   ```powershell
   python -m alembic upgrade head
   ```

SQLite support is limited for automatic schema diffs, so migrations are written by hand.

### Migrations and tests

Tests that rely on the database use the same migrations:

* `storage.db.DB_PATH` can be patched to point to a temporary file.

* `storage.db.init_db()` is called to apply all migrations to that temporary database.

This keeps the test schema and the runtime schema consistent.

### Docker and migrations

When running the bot inside Docker, migrations must be applied before starting the application process.

A typical pattern is to run:

```powershell
python -m alembic upgrade head
python bot.py
```

from an entrypoint script.

### CI pipeline

The GitHub Actions workflow runs the following steps:

1. Installs development dependencies and the package itself in editable mode:

   ```powershell
   python -m pip install -e .[dev]
   ```

2. Applies Alembic migrations:

   ```powershell
   python -m alembic upgrade head
   ```

3. Runs static checks and tests:

   ```powershell
   python -m ruff check .
   python -m mypy domain services ocr storage
   python -m pytest
   ```
