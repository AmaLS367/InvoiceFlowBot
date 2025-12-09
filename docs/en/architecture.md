<img src="https://capsule-render.vercel.app/api?type=waving&color=gradient&customColorList=6,11,20&height=120&section=header&text=Architecture&fontSize=40&animation=fadeIn"/>

<div align="center">

<p align="center">
  <img src="https://readme-typing-svg.demolab.com?font=Fira+Code&size=18&duration=3000&pause=1000&center=true&vCenter=true&width=500&lines=Clean+Architecture;Layered+Design;Modular+System" alt="Typing SVG" />
</p>

[![Architecture](https://img.shields.io/badge/Pattern-Clean%20Architecture-blue?style=for-the-badge)](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
[![Layers](https://img.shields.io/badge/Layers-6-green?style=for-the-badge)](#layers)
[![Mermaid](https://img.shields.io/badge/Diagrams-Mermaid-orange?style=for-the-badge)](#overall-component-diagram)

</div>

## 📋 About

This document describes the high level architecture of InvoiceFlowBot.

## 📦 Layers

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
