<img src="https://capsule-render.vercel.app/api?type=waving&color=gradient&customColorList=12,16,20&height=120&section=header&text=Обзор+системы&fontSize=40&animation=fadeIn"/>

<div align="center">

[![System](https://img.shields.io/badge/System-Architecture-blue?style=for-the-badge)](architecture.md)
[![Components](https://img.shields.io/badge/Components-Modular-green?style=for-the-badge)](architecture.md)
[![Flow](https://img.shields.io/badge/Data-Flow-orange?style=for-the-badge)](#-движение-данных)

</div>

## 📋 Описание

InvoiceFlowBot работает как Telegram бот, принимающий документы от пользователя и обрабатывающий их через слой OCR:

- Пользователь отправляет боту PDF или фото счета, загружая файл прямо в чат.
- `backend.handlers.file` принимает вложение, скачивает его в `temp/` и подготавливает изображения для OCR.
- `backend.services.invoice_service` запускает OCR через `backend.ocr.async_client` и конвертирует результаты в доменные сущности (`backend.domain.invoices`).
- Интерфейс `OcrProvider` задаёт контракт распознавания. По умолчанию роутер выбирает `LocalOcrProvider` (Docling и Tesseract). Mindee можно включить в настройках.
- Черновик хранится в таблице SQLite `invoice_drafts` по пользователю. Подтверждённые данные записывает `backend.storage.db_async`. FSM хранит состояние диалога.
- Телеграм интерфейс (`backend.handlers.commands`, `backend.handlers.callbacks`, `backend.handlers.utils`) позволяет поправить поля, добавить комментарии и запросить историю.

## 🔄 Движение данных

<div align="center">

```mermaid
sequenceDiagram
    participant U as 👤 Пользователь
    participant T as 📱 Telegram
    participant H as 🎯 Handlers
    participant S as ⚙️ Services
    participant O as 🔍 OCR Provider
    participant D as 💾 Database

    U->>T: Отправка PDF/Фото
    T->>H: file.py получает файл
    H->>S: process_invoice_file()
    S->>O: extract_invoice()
    O-->>S: ExtractionResult
    S->>S: Конвертация в Invoice
    S-->>H: Invoice (черновик)
    H->>D: Сохранение черновика в invoice_drafts
    H->>U: Показ черновика
    U->>H: Редактирование
    H->>D: Обновление черновика
    U->>H: Подтверждение через /save или кнопку
    H->>S: save_invoice()
    S->>D: Сохранение
    D-->>S: Success
    H->>D: Удаление черновика
    H-->>U: Подтверждение с ID счёта
```

</div>

### 📝 Детальные шаги

<table>
<tr>
<td width="5%" align="center">1️⃣</td>
<td>Пользователь отправляет PDF или изображение в бот</td>
</tr>
<tr>
<td width="5%" align="center">2️⃣</td>
<td><code>backend.handlers.file</code> получает файл и вызывает <code>backend.services.invoice_service.process_invoice_file()</code></td>
</tr>
<tr>
<td width="5%" align="center">3️⃣</td>
<td>Сервис запускает выбранный провайдер OCR в отдельном потоке</td>
</tr>
<tr>
<td width="5%" align="center">4️⃣</td>
<td><code>backend.services.invoice_service</code> конвертирует <code>ExtractionResult</code> в доменную <code>Invoice</code></td>
</tr>
<tr>
<td width="5%" align="center">5️⃣</td>
<td>Черновик сохраняется в SQLite, пользователь редактирует его через команды или кнопки</td>
</tr>
<tr>
<td width="5%" align="center">6️⃣</td>
<td>Команда <code>/save</code> → <code>save_invoice()</code> → <code>backend.storage.db_async</code> → SQLite</td>
</tr>
<tr>
<td width="5%" align="center">7️⃣</td>
<td>Команда <code>/invoices</code> → <code>list_invoices()</code> с фильтрацией</td>
</tr>
</table>

## 📁 Основные директории

<div align="center">

```mermaid
graph TD
    A[bot.py] -->|инициализирует| B[backend.handlers]
    B -->|использует| C[backend.services]
    C -->|использует| D[backend.domain]
    C -->|использует| E[backend.ocr]
    C -->|использует| F[backend.storage]
    G[backend.config] -.настраивает.-> A
    G -.настраивает.-> B
    G -.настраивает.-> C

    style A fill:#4A90E2,stroke:#2c3e50,stroke-width:2px,color:#fff
    style B fill:#50C878,stroke:#2c3e50,stroke-width:2px,color:#fff
    style C fill:#FFD93D,stroke:#2c3e50,stroke-width:2px,color:#333
    style D fill:#FF6B6B,stroke:#2c3e50,stroke-width:2px,color:#fff
    style E fill:#B19CD9,stroke:#2c3e50,stroke-width:2px,color:#fff
    style F fill:#A8E6CF,stroke:#2c3e50,stroke-width:2px,color:#333
    style G fill:#FFA07A,stroke:#2c3e50,stroke-width:2px,color:#fff
```

</div>

### 🗂️ Структура модулей

| Модуль | Назначение | Ключевые файлы |
|--------|-----------|----------------|
| 🎯 **bot.py** | Точка входа | Регистрация хендлеров |
| ⚙️ **backend.config** | Конфигурация | `.env`, токены, Mindee |
| 🎨 **backend.domain/** | Доменная модель | Invoice, Header, Item |
| ⚡ **backend.services/** | Бизнес-логика | invoice_service.py |
| 🤖 **backend.handlers/** | Telegram обработка | file, commands, callbacks |
| 🔍 **backend.ocr/** | OCR провайдеры | engine, providers, mindee |
| 💾 **backend.storage/** | База данных | db.py, db_async.py, drafts_async.py, user_languages.py |
| 🧪 **tests/** | Тестирование | Unit & integration |

<details>
<summary><b>📦 Подробная структура backend.handlers/</b></summary>

- `file.py` — загрузка файлов и начальная обработка OCR
- `commands.py` — текстовые команды (/show, /edit, /invoices)
- `callbacks.py` — callback-запросы для inline-кнопок
- `utils.py` — утилиты форматирования и клавиатуры
- `fsm.py` — состояния диалога для редактирования и ввода фильтров периода

</details>

<details>
<summary><b>🔍 Подробная структура backend.ocr/</b></summary>

**providers/** — абстракция провайдеров:
- `base.py` — интерфейс `OcrProvider`
- `local_provider.py` — локальное распознавание PDF, сканов и фотографий
- `mindee_provider.py` — реализация для Mindee

**engine/** — движок OCR:
- `router.py` — маршрутизация к провайдерам
- `types.py` — типы данных
- `util.py` — утилиты

**Mindee интеграция:**
- `mindee_client.py` — прямая работа с Mindee API

</details>
