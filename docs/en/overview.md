# System Overview

InvoiceFlowBot runs as a Telegram bot that receives documents from users and processes them through an OCR pipeline:

- Users upload invoices as PDFs or images directly in the chat.
- `handlers/file.py` validates the payload and stores a temporary copy.
- `services/invoice_service.py` orchestrates OCR calls via `ocr/engine/router.py` and converts results to domain entities (`domain/invoices.py`).
- Draft data lives in user state (`handlers/state.py`) until the operator confirms it.
- Confirmed invoices are persisted to SQLite via `storage/db.py`, and the Telegram UI (`handlers/commands.py`, `handlers/callbacks.py`, `handlers/utils.py`) lets users edit or query records.

## Data flow

1. A PDF or photo arrives from the user.
2. `handlers/file.py` receives the file and calls `services/invoice_service.process_invoice_file()`.
3. The service layer triggers `ocr/engine/router.py` and the Mindee client to obtain raw OCR data.
4. `services/invoice_service.py` converts the OCR result (`ExtractionResult`) into a domain `Invoice` entity.
5. The draft `Invoice` stays in memory (`handlers/state.py`), where the user can edit values through commands (`handlers/commands.py`) or callback buttons (`handlers/callbacks.py`).
6. `/save` or the save callback calls `services/invoice_service.save_invoice()`, which persists the domain entity via `storage/db.py` into `data.sqlite`.
7. `/invoices` and helper functions query `services/invoice_service.list_invoices()`, which fetches domain entities from `storage/db.py` filtered by period and supplier.

## Key directories

- `bot.py` — entry point configuring the Telegram bot and handlers.
- `config.py` — loads `.env`, handles tokens, Mindee credentials, and logging knobs.
- `domain/` — core business entities (Invoice, InvoiceHeader, InvoiceItem, etc.) independent of infrastructure.
- `services/` — service layer coordinating domain logic, OCR pipeline, and persistence.
- `handlers/` — Telegram bot handlers:
  - `file.py` — file upload and initial OCR processing
  - `commands.py` — text command handlers (/show, /edit, /invoices, etc.)
  - `callbacks.py` — callback query handlers for inline buttons (edit, save, comment, etc.)
  - `utils.py` — formatting utilities and keyboard builders
  - `state.py` — global state management for user sessions
- `ocr/` — Mindee integration, routing logic, shared utilities, and logging helpers.
- `storage/db.py` — database initialization, inserts, lookups, and comment management.
- `tests/` — pytest suites covering domain entities, OCR parsing, and storage behaviours.

