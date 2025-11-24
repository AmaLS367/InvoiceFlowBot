# Architecture

This document describes the high level architecture of InvoiceFlowBot.

## Layers

The project is split into several layers:

- **domain** - pure domain model for invoices and drafts.

- **services** - business logic that orchestrates domain, OCR and storage.

- **ocr** - OCR engine and providers (Mindee), responsible for turning files into structured data.

- **storage** - async storage layer on top of SQLite and Alembic migrations.

- **handlers** - Telegram entrypoint implemented with aiogram 3.

- **core** - configuration and dependency injection container.

## High level component diagram

```mermaid
flowchart LR
    TgUser[Telegram user] -->|files, commands| Handlers

    subgraph Bot
        Handlers[handlers/*]
        Services[services/*]
        Domain[domain/*]
        OCR[ocr/*]
        Storage[storage/*]
        Config[config.py / core/*]
    end

    Handlers --> Services
    Services --> Domain
    Services --> OCR
    Services --> Storage
    OCR --> MindeeAPI[(Mindee API)]
    Storage --> SQLite[(SQLite database)]
    Config --> Handlers
    Config --> Services
    Config --> Storage
```

## Invoice processing flow

```mermaid
sequenceDiagram
    participant User as Telegram user
    participant TG as Telegram Bot API
    participant H as handlers/file.py
    participant S as InvoiceService
    participant O as OcrProvider (Mindee)
    participant ST as AsyncInvoiceStorage

    User->>TG: send PDF or image
    TG->>H: update with file
    H->>S: process_invoice_file(pdf_path, fast, max_pages)
    S->>O: extract(pdf_bytes)
    O->>MindeeAPI: HTTP request
    MindeeAPI-->>O: OCR JSON
    O-->>S: ExtractionResult
    S->>S: map to Invoice domain model
    S->>ST: save_invoice_domain_async(invoice)
    ST-->>S: invoice id
    S-->>H: Invoice with id
    H-->>User: message with invoice header and items
```
