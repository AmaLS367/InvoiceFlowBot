# Database

InvoiceFlowBot relies on SQLite, a lightweight file-based database. By default data is stored in `data.sqlite` at the project root (or inside the container). Override the path with `INVOICE_DB_PATH` if needed.

## Schema

`storage/db.py:init_db()` runs on startup and ensures these tables exist:

- `invoices` — invoice headers: Telegram user, supplier, client, document number, date fields, total amount, raw text, and source path.
- `invoice_items` — line items: row index, code, name, quantity, price, total per line.
- `comments` — user comments linked to invoices.

The database enables WAL mode for safer concurrent writes.

## Best practices

- Keep `data.sqlite` out of version control and store it in backups.
- Make regular copies before upgrades. Copying the file is enough:
```powershell
Copy-Item .\data.sqlite .\backup\data-$(Get-Date -Format yyyyMMddHHmmss).sqlite
```
- In Docker, verify that `./data.sqlite:/app/data.sqlite` mounts a real file; otherwise data will stay inside the container.

## Restore and migrate

To move InvoiceFlowBot to another host, stop the bot, copy `data.sqlite`, place it on the new server, and start the bot again. `init_db()` will create any missing tables automatically.
