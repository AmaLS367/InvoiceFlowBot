<img src="https://capsule-render.vercel.app/api?type=waving&color=gradient&customColorList=12,16,20&height=120&section=header&text=System+Overview&fontSize=40&animation=fadeIn"/>

<div align="center">

[![System](https://img.shields.io/badge/System-Architecture-blue?style=for-the-badge)](architecture.md)
[![Components](https://img.shields.io/badge/Components-Modular-green?style=for-the-badge)](architecture.md)
[![Flow](https://img.shields.io/badge/Data-Flow-orange?style=for-the-badge)](#data-flow)

</div>

## 📋 Description

InvoiceFlowBot runs as a Telegram bot that receives documents from users and processes them through an OCR pipeline:

- Users upload invoices as PDFs or images directly in the chat.
- `backend.handlers.file` validates the payload and stores a temporary copy.
- `backend.services.invoice_service` orchestrates OCR calls via `backend.ocr.engine.router` and converts results to domain entities (`backend.domain.invoices`).
- The OCR layer is implemented through a provider abstraction: the `OcrProvider` interface and the `MindeeOcrProvider` implementation. The `backend.ocr.engine.router` module depends only on the interface and calls the current provider for invoice recognition. The rest of the system uses only the `extract_invoice` function from `backend.ocr.engine.router`.
- Draft data lives in user state (`backend.handlers.fsm`) until the operator confirms it.
- Confirmed invoices are persisted to SQLite via `backend.storage.db`, and the Telegram UI (`backend.handlers.commands`, `backend.handlers.callbacks`, `backend.handlers.utils`) lets users edit or query records.

## Data flow

1. A PDF or photo arrives from the user.
2. `backend.handlers.file` receives the file and calls `backend.services.invoice_service.process_invoice_file()`.
3. The service layer triggers `backend.ocr.engine.router`, which uses the OCR provider (currently `MindeeOcrProvider`) to obtain raw OCR data from Mindee API.
4. `backend.services.invoice_service` converts the OCR result (`ExtractionResult`) into a domain `Invoice` entity.
5. The draft `Invoice` stays in memory (`backend.handlers.fsm`), where the user can edit values through commands (`backend.handlers.commands`) or callback buttons (`backend.handlers.callbacks`).
6. `/save` or the save callback calls `backend.services.invoice_service.save_invoice()`, which persists the domain entity via `backend.storage.db` into `data.sqlite`.
7. `/invoices` and helper functions query `backend.services.invoice_service.list_invoices()`, which fetches domain entities from `backend.storage.db` filtered by period and supplier.

## Key directories

- `bot.py` — entry point configuring the Telegram bot and handlers.
- `backend.config` — loads `.env`, handles tokens, Mindee credentials, and logging knobs.
- `backend.domain/` — core business entities (Invoice, InvoiceHeader, InvoiceItem, etc.) independent of infrastructure.
- `backend.services/` — service layer coordinating domain logic, OCR pipeline, and persistence.
- `backend.handlers/` — Telegram bot handlers:
  - `file.py` — file upload and initial OCR processing
  - `commands.py` — text command handlers (/show, /edit, /invoices, etc.)
  - `callbacks.py` — callback query handlers for inline buttons (edit, save, comment, etc.)
  - `utils.py` — formatting utilities and keyboard builders
  - `fsm.py` — global state management for user sessions
- `backend.ocr/` — OCR layer with provider abstraction:
  - `providers/` — provider abstraction layer:
    - `base.py` — `OcrProvider` interface defining the contract for OCR providers
    - `mindee_provider.py` — `MindeeOcrProvider` implementation that delegates to Mindee API
  - `engine/router.py` — uses the provider abstraction to call OCR services; the rest of the system only depends on `router.extract_invoice`
  - `mindee_client.py` — direct Mindee API integration (used by `MindeeOcrProvider`)
  - Shared utilities and logging helpers
- `backend.storage/db.py` — database initialization, inserts, lookups, and comment management.
- `tests/` — pytest suites covering domain entities, OCR parsing, service layer, and storage behaviours.
