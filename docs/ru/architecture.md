# Архитектура

Этот документ описывает высокоуровневую архитектуру InvoiceFlowBot.

## Слои проекта

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

