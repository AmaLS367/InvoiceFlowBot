<img src="https://capsule-render.vercel.app/api?type=waving&color=gradient&customColorList=6,11,20&height=120&section=header&text=Database&fontSize=40&animation=fadeIn"/>

<div align="center">

[![SQLite](https://img.shields.io/badge/Database-SQLite-blue?style=for-the-badge&logo=sqlite&logoColor=white)](https://www.sqlite.org/)
[![Alembic](https://img.shields.io/badge/Migrations-Alembic-green?style=for-the-badge)](https://alembic.sqlalchemy.org/)
[![WAL](https://img.shields.io/badge/Mode-WAL-orange?style=for-the-badge)](#schema)

</div>

## 📋 About Database

InvoiceFlowBot relies on SQLite, a lightweight file-based database. By default data is stored in `data.sqlite` at the project root (or inside the container). Override the path with `INVOICE_DB_PATH` if needed.

> [!NOTE]
> SQLite requires no separate database server - everything in one file!

## 📊 Schema

`backend.storage.db:init_db()` runs on startup and ensures these tables exist:

- `invoices` — invoice headers: Telegram user, supplier, client, document number, date fields, total amount, raw text, and source path.
- `invoice_items` — line items: row index, code, name, quantity, price, total per line.
- `comments` — user comments linked to invoices.

The database enables WAL mode for safer concurrent writes.

## 🔄 Migrations

Schema changes are managed by [Alembic](https://alembic.sqlalchemy.org/). Migrations create and update tables (including `invoice_drafts` for draft invoices).

### When to run migrations

- **First-time setup** — before first run, so all tables exist.
- **After pulling changes** — if new migrations were added to the repo.
- **After cloning** — so the local database matches the current schema.

The bot also runs migrations on startup via `backend.storage.db.init_db()`, but running them manually once from the project root is recommended so the same database file is used (see below).

### How to run migrations

**Always run from the project root** (the `InvoiceFlowBot` directory) so the app config and `.env` are loaded and migrations apply to the same database the bot uses (by default `backend/data.sqlite`).

```powershell
# From project root (Windows)
python -m alembic -c backend/alembic.ini upgrade head
```

Or use the script:

```powershell
python scripts/python/migrate.py
```

Linux/macOS:

```bash
./scripts/linux/migrate.sh
```

Other commands (from project root):

```powershell
# Roll back one migration
python scripts/python/migrate.py downgrade -1

# Create a new migration (developers)
python -m alembic -c backend/alembic.ini revision -m "describe_change"
```

> [!TIP]
> If you see `no such table: invoice_drafts` or `unable to open database file`, run migrations from the project root as above. The path to the database is taken from the app config (`INVOICE_DB_PATH` / `backend/data.sqlite`), not from `alembic.ini`.

## ⚠️ Best practices

> [!WARNING]
> Make regular backups of `data.sqlite`!

- ❌ Keep `data.sqlite` out of version control
- 💾 Backup command:
```powershell
Copy-Item .\data.sqlite .\backup\data-$(Get-Date -Format yyyyMMddHHmmss).sqlite
```
- 🐳 In Docker, verify volume mapping is correct

## Restore and migrate

To move InvoiceFlowBot to another host, stop the bot, copy `data.sqlite`, place it on the new server, and start the bot again. `init_db()` will create any missing tables automatically.
