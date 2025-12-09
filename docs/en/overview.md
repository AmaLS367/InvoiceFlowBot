# 📖 System Overview

InvoiceFlowBot runs as a Telegram bot that receives documents from users and processes them through an OCR pipeline:

- Users upload invoices as PDFs or images directly in the chat.
- `handlers/file.py` validates the payload and stores a temporary copy.
- `services/invoice_service.py` orchestrates OCR calls via `ocr/engine/router.py` and converts results to domain entities (`domain/invoices.py`).
- The OCR layer is implemented through a provider abstraction: the `OcrProvider` interface and the `MindeeOcrProvider` implementation. The `ocr.engine.router` module depends only on the interface and calls the current provider for invoice recognition. The rest of the system uses only the `extract_invoice` function from `ocr.engine.router`.
- Draft data lives in user state (`handlers/state.py`) until the operator confirms it.
- Confirmed invoices are persisted to SQLite via `storage/db.py`, and the Telegram UI (`handlers/commands.py`, `handlers/callbacks.py`, `handlers/utils.py`) lets users edit or query records.

## Data flow

1. A PDF or photo arrives from the user.
2. `handlers/file.py` receives the file and calls `services/invoice_service.process_invoice_file()`.
3. The service layer triggers `ocr/engine/router.py`, which uses the OCR provider (currently `MindeeOcrProvider`) to obtain raw OCR data from Mindee API.
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
- `ocr/` — OCR layer with provider abstraction:
  - `providers/` — provider abstraction layer:
    - `base.py` — `OcrProvider` interface defining the contract for OCR providers
    - `mindee_provider.py` — `MindeeOcrProvider` implementation that delegates to Mindee API
  - `engine/router.py` — uses the provider abstraction to call OCR services; the rest of the system only depends on `router.extract_invoice`
  - `mindee_client.py` — direct Mindee API integration (used by `MindeeOcrProvider`)
  - Shared utilities and logging helpers
- `storage/db.py` — database initialization, inserts, lookups, and comment management.
- `tests/` — pytest suites covering domain entities, OCR parsing, service layer, and storage behaviours.
