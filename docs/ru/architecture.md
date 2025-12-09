<img src="https://capsule-render.vercel.app/api?type=waving&color=gradient&customColorList=6,11,20&height=120&section=header&text=Архитектура&fontSize=40&animation=fadeIn"/>

<div align="center">

<p align="center">
  <img src="https://readme-typing-svg.demolab.com?font=Fira+Code&size=18&duration=3000&pause=1000&center=true&vCenter=true&width=500&lines=%D0%A7%D0%B8%D1%81%D1%82%D0%B0%D1%8F+%D0%B0%D1%80%D1%85%D0%B8%D1%82%D0%B5%D0%BA%D1%82%D1%83%D1%80%D0%B0;%D0%A0%D0%B0%D0%B7%D0%B4%D0%B5%D0%BB%D0%B5%D0%BD%D0%B8%D0%B5+%D0%BD%D0%B0+%D1%81%D0%BB%D0%BE%D0%B8;%D0%9C%D0%BE%D0%B4%D1%83%D0%BB%D1%8C%D0%BD%D1%8B%D0%B9+%D0%B4%D0%B8%D0%B7%D0%B0%D0%B9%D0%BD" alt="Typing SVG" />
</p>

[![Architecture](https://img.shields.io/badge/Pattern-Clean%20Architecture-blue?style=for-the-badge)](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
[![Layers](https://img.shields.io/badge/Layers-6-green?style=for-the-badge)](#слои-проекта)
[![Mermaid](https://img.shields.io/badge/Diagrams-Mermaid-orange?style=for-the-badge)](#общая-схема-компонентов)

</div>

## 📋 О документе

Этот документ описывает высокоуровневую архитектуру InvoiceFlowBot.

> [!NOTE]
> Проект использует чистую архитектуру с разделением на слои

## 📦 Слои проекта

Проект разделен на несколько слоев:

- **domain** - чистая доменная модель счетов и черновиков.

- **services** - бизнес логика, которая связывает домен, OCR и хранилище.

- **ocr** - движок OCR и провайдеры (Mindee), отвечают за преобразование файлов в структурированные данные.

- **storage** - асинхронный слой поверх SQLite с миграциями Alembic.

- **handlers** - входной слой Telegram на базе aiogram 3.

- **core** - конфигурация и контейнер зависимостей.

## Общая схема компонентов

```mermaid
flowchart LR
    TgUser[Пользователь Telegram] -->|файлы, команды| Handlers

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
    Storage --> SQLite[(SQLite база данных)]
    Config --> Handlers
    Config --> Services
    Config --> Storage
```

## Поток обработки инвойса

```mermaid
sequenceDiagram
    participant User as Пользователь
    participant TG as Telegram Bot API
    participant H as handlers/file.py
    participant S as InvoiceService
    participant O as OcrProvider (Mindee)
    participant ST as AsyncInvoiceStorage

    User->>TG: отправка PDF или изображения
    TG->>H: апдейт с файлом
    H->>S: process_invoice_file(pdf_path, fast, max_pages)
    S->>O: extract(pdf_bytes)
    O->>MindeeAPI: HTTP запрос
    MindeeAPI-->>O: OCR JSON
    O-->>S: ExtractionResult
    S->>S: маппинг в доменную модель Invoice
    S->>ST: save_invoice_domain_async(invoice)
    ST-->>S: id счета
    S-->>H: Invoice с id
    H-->>User: сообщение с шапкой и позициями
```
