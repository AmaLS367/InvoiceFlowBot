<img src="https://capsule-render.vercel.app/api?type=waving&color=gradient&customColorList=6,11,20&height=120&section=header&text=Database&fontSize=40&animation=fadeIn"/>

<div align="center">

[![SQLite](https://img.shields.io/badge/Database-SQLite-blue?style=for-the-badge&logo=sqlite&logoColor=white)](https://www.sqlite.org/)
[![Alembic](https://img.shields.io/badge/Migrations-Alembic-green?style=for-the-badge)](https://alembic.sqlalchemy.org/)

</div>


## About SQLite

`INVOICE_DB_PATH` defaults to `../data.sqlite`. The bot resolves relative paths from `backend/`, so the default file is `data.sqlite` in the project root locally and `/app/data.sqlite` in Docker. A fresh database uses SQLite's default rollback journal mode (`delete`).

## Schema

- `invoices` stores confirmed invoices, including supplier, customer, number, date, total and source path.
- `invoice_items` stores individual items linked to invoices.
- `comments` stores user comments and automatic sum checks linked to invoices.
- `invoice_drafts` stores one active draft per Telegram user.
- `user_languages` stores the selected interface language for each Telegram user.

## Migrations

The bot applies Alembic migrations on startup. To apply them manually, set `BOT_TOKEN` in `.env` or the process environment and run from the project root:

```bash
python -m alembic -c backend/alembic.ini upgrade head
```

You can also use `python scripts/python/migrate.py` or `bash scripts/linux/migrate.sh`. To roll back one revision, stop the bot, back up the database, and use `python scripts/python/migrate.py downgrade -1`. On the next start, the bot applies any pending upgrades. Alembic uses the application's database path. For new revisions, see the [development guide](development.md#creating-a-new-migration).

## Backup and restore

Stop the bot before copying the SQLite file. In Docker, run `docker compose down` and copy the database from the host. The following PowerShell example backs up the default local or Compose database:

```powershell
New-Item -ItemType Directory -Force ./backup | Out-Null
Copy-Item ./data.sqlite "./backup/data-$(Get-Date -Format yyyyMMddHHmmss).sqlite"
```

If you configured a custom path, copy that database instead. To restore or move it, keep the bot stopped, retain a copy of any destination database, and place the backup at the configured path. On startup the bot applies any pending migrations.
