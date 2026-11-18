<img src="https://capsule-render.vercel.app/api?type=waving&color=gradient&customColorList=6,11,20&height=120&section=header&text=Architecture&fontSize=40&animation=fadeIn"/>

<div align="center">

<p align="center">
  <img src="https://readme-typing-svg.demolab.com?font=Fira+Code&size=18&duration=3000&pause=1000&center=true&vCenter=true&width=500&lines=Clean+Architecture;Layered+Design;Modular+System" alt="Typing SVG" />
</p>

[![Architecture](https://img.shields.io/badge/Pattern-Clean%20Architecture-blue?style=for-the-badge)](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
[![Layers](https://img.shields.io/badge/Layers-6-green?style=for-the-badge)](#-layers)
[![Mermaid](https://img.shields.io/badge/Diagrams-Mermaid-orange?style=for-the-badge)](#high-level-component-diagram)

</div>

## 📋 About

This document describes the high level architecture of InvoiceFlowBot.

## 📦 Layers

The project is split into several layers:

- **backend.domain** - pure domain model for invoices and drafts.

- **backend.services** - business logic that orchestrates domain, OCR and storage.

- **backend.ocr** - OCR engine and providers (Docling, Tesseract, Mindee), responsible for turning files into structured data.

- **backend.storage** - async storage layer on top of SQLite and Alembic migrations.

- **backend.handlers** - Telegram entrypoint implemented with aiogram 3.

- **backend.core** - configuration and dependency injection container.

## High level component diagram

```mermaid
flowchart LR
    TgUser[Telegram user] -->|files, commands| Handlers

    subgraph Bot
        Handlers[backend.handlers/*]
        Services[backend.services/*]
        Domain[backend.domain/*]
        OCR[backend.ocr/*]
        Storage[backend.storage/*]
        Config[backend.config.py / backend.core/*]
    end

    Handlers --> Services
    Services --> Domain
    Services --> OCR
    Services --> Storage
    OCR --> Local[Docling + Tesseract]
    OCR -.-> MindeeAPI[(Mindee API)]
    Storage --> SQLite[(SQLite database)]
    Config --> Handlers
    Config --> Services
    Config --> Storage
```

## Invoice processing flow

```mermaid
sequenceDiagram
    participant User as Telegram user
    participant H as Telegram handlers
    participant I as InvoiceService
    participant O as Configured OCR provider
    participant D as DraftService
    participant DB as SQLite

    User->>H: Upload PDF or image
    H->>I: process_invoice_file()
    I->>O: extract_invoice() in a worker thread
    O-->>I: ExtractionResult
    I-->>H: Invoice
    H->>D: set_current_draft()
    D->>DB: Write invoice_drafts for this user
    H-->>User: Display draft and review notes
    User->>H: Edit or add comments
    H->>D: Update current draft
    User->>H: Confirm with /save or Save button
    H->>I: save_invoice()
    I->>DB: Write confirmed invoice, items, and comments
    H->>D: clear_current_draft()
    H-->>User: Confirm saved invoice ID
```

SQLite keeps one active draft per Telegram user. Aiogram FSM keeps the conversation state for operations such as editing a field or entering period dates.
