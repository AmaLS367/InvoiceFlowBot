# System Overview

InvoiceFlowBot runs as a Telegram bot that receives documents from users and processes them through an OCR pipeline:

- Users upload invoices as PDFs or images directly in the chat.
- `handlers/file.py` validates the payload and stores a temporary copy.
- `ocr/extract.py` calls Mindee via `ocr/mindee_client.py`, while `ocr/engine` converts results to internal types.
- Draft data lives in user state (`handlers/state.py`) until the operator confirms it.
- Confirmed invoices are persisted to SQLite via `storage/db.py`, and the Telegram UI (`handlers/commands.py`, `handlers/utils.py`) lets users edit or query records.

## Data flow

1. A PDF or photo arrives from the user.
2. The bot triggers `ocr.extract` and the Mindee client to obtain raw OCR data.
3. `ocr/engine/router.py` plus `ocr/engine/types.py` normalize the payload and augment it with logging metadata.
4. The draft stays in memory, where the user can edit values through commands or buttons.
5. `/save` calls `storage.db.save_invoice`, writing headers, items, and comments into `data.sqlite`.
6. `/invoices` and helper functions query `storage/db.py` for historical data by period and supplier.

## Key directories

- `bot.py` — entry point configuring the Telegram bot and handlers.
- `config.py` — loads `.env`, handles tokens, Mindee credentials, and logging knobs.
- `handlers/` — command handling, file ingestion, and per-user state tracking.
- `ocr/` — Mindee integration, routing logic, shared utilities, and logging helpers.
- `storage/db.py` — database initialization, inserts, lookups, and comment management.
- `tests/` — pytest suites covering OCR parsing and storage behaviours.

