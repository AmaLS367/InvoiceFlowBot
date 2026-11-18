<h1 align="center">InvoiceFlowBot</h1>

<p align="center">
  <strong>Automated Telegram bot for extracting, editing, and storing invoices with local OCR</strong>
</p>

<p align="center">
  <a href="https://github.com/AmaLS367/InvoiceFlowBot/actions/workflows/ci.yml"><img src="https://img.shields.io/github/actions/workflow/status/AmaLS367/InvoiceFlowBot/ci.yml?style=flat-square&logo=github&label=CI" alt="CI" /></a>
  <a href="https://www.python.org/downloads/"><img src="https://img.shields.io/badge/Python-3.11%2B-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python 3.11+" /></a>
  <a href="https://telegram.org/"><img src="https://img.shields.io/badge/Aiogram-3.x-2CA5E0?style=flat-square&logo=telegram&logoColor=white" alt="Aiogram 3" /></a>
  <a href="docs/en/setup-local.md"><img src="https://img.shields.io/badge/OCR-Docling%20%2B%20Tesseract-4A90E2?style=flat-square" alt="OCR" /></a>
  <a href="docs/en/database.md"><img src="https://img.shields.io/badge/Database-SQLite-003B57?style=flat-square&logo=sqlite&logoColor=white" alt="SQLite" /></a>
  <a href="#-interface-languages"><img src="https://img.shields.io/badge/Languages-7-2EA043?style=flat-square" alt="Languages" /></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-Apache%202.0-blue?style=flat-square" alt="License: Apache 2.0" /></a>
</p>

<p align="center">
  <strong>English</strong> ·
  <a href="README.ru.md">Русский</a> ·
  <a href="docs/en/index.md">Documentation</a> ·
  <a href="docs/en/screenshots.md">Screenshots</a>
</p>

<p align="center">
  <a href="docs/assets/screenshots/InvoiceFlowBot_Contra_1600x1200_web.mp4">
    <img src="docs/assets/screenshots/demo.webp" alt="InvoiceFlowBot demo" width="820" />
  </a>
</p>

<p align="center">
  <sub>
    <a href="docs/assets/screenshots/InvoiceFlowBot_Contra_1600x1200_web.mp4">Watch full HD video with sound (MP4)</a>
    ·
    <a href="docs/en/screenshots.md">Browse screenshots</a>
  </sub>
</p>

---

InvoiceFlowBot accepts PDF invoices and photos in Telegram, extracts structured headers and line items locally with Docling and Tesseract (or Mindee as an optional backend), lets users review and edit drafts inline, and saves verified invoices to SQLite for period-based reporting and CSV export.

## ✨ Features

```mermaid
graph LR
    A[Upload PDF / Photo] --> B[Local OCR]
    B --> C[Review & Edit Draft]
    C --> D[Save to SQLite]
    D --> E[Period Reports & CSV]
```

| Feature | Description |
|---------|-------------|
| **Local OCR by Default** | Runs Docling + Tesseract on your own server with no per-document API fees (optional Mindee provider included). |
| **Multiple Input Formats** | Supports PDF, JPEG, PNG, HEIC, HEIF, and WebP. |
| **Multilingual Interface (7 Languages)** | Auto-detects the user's Telegram language, persists choices in SQLite, and localizes Telegram command menus. |
| **Interactive Draft Review** | Edit supplier, customer, date, invoice number, totals, and individual line items via inline buttons or commands. |
| **Automatic Sanity Checks** | Highlights line-item sum mismatches and auto-computed or decimal-corrected values before saving. |
| **SQLite + Alembic Migrations** | Stores invoices, line items, comments, drafts, and user language preferences with versioned schema migrations. |
| **Period Queries & CSV Export** | Filter saved invoices by date range and supplier; long item tables are exported as UTF-8 CSV files. |

## 🌐 Interface Languages

The bot interface, inline keyboards, and per-user Telegram command menu support **7 languages** out of the box:

| Code | Language | Catalog |
|------|----------|---------|
| `ru` | Русский (default fallback) | [`ru.json`](backend/handlers/locales/ru.json) |
| `en` | English | [`en.json`](backend/handlers/locales/en.json) |
| `de` | Deutsch | [`de.json`](backend/handlers/locales/de.json) |
| `es` | Español | [`es.json`](backend/handlers/locales/es.json) |
| `fr` | Français | [`fr.json`](backend/handlers/locales/fr.json) |
| `it` | Italiano | [`it.json`](backend/handlers/locales/it.json) |
| `pt` | Português | [`pt.json`](backend/handlers/locales/pt.json) |

Users can switch languages anytime via `/language` or the **🌐 Language** button. Adding another language only requires a new ISO 639-1 JSON file in `backend/handlers/locales/` and registering it in `LANGUAGES` in [`backend/handlers/texts.py`](backend/handlers/texts.py) — see the [development guide](docs/en/development.md).

## 🚀 Quick Start with Docker

> [!TIP]
> Docker includes Python, Tesseract language packs, and all runtime dependencies out of the box.

```bash
# 1. Clone the repository and prepare .env
git clone https://github.com/AmaLS367/InvoiceFlowBot.git
cd InvoiceFlowBot
cp .env.example .env

# 2. Set BOT_TOKEN in .env, then build and start
docker compose up --build -d

# 3. Follow logs
docker compose logs -f

# 4. Stop
docker compose down
```

## 💻 Local Installation

Requires **Python 3.11+**, **Git**, and **Tesseract** (with language data matching `OCR_LANGUAGES`, e.g., `eng+rus`).

<details>
<summary><b>Step-by-step local setup</b></summary>

1. Clone and create a virtual environment:

   ```bash
   git clone https://github.com/AmaLS367/InvoiceFlowBot.git
   cd InvoiceFlowBot
   python -m venv .venv
   # Linux/macOS:
   source .venv/bin/activate
   # Windows PowerShell:
   # .\.venv\Scripts\Activate.ps1
   ```

2. Install dependencies:

   ```bash
   pip install -e .
   ```

3. Create `.env` from `.env.example`:

   ```env
   BOT_TOKEN=123456:ABCDEF_your_bot_token
   OCR_PROVIDER=local
   OCR_LANGUAGES=eng+rus
   ```

   With `OCR_PROVIDER=local`, documents are processed locally without external OCR credentials; the first run downloads Docling models. To use Mindee instead, set `OCR_PROVIDER=mindee`, `MINDEE_API_KEY`, and `MINDEE_MODEL_ID`. See the [local setup guide](docs/en/setup-local.md).

4. Apply migrations and run the bot:

   ```bash
   python -m alembic -c backend/alembic.ini upgrade head
   python bot.py
   ```

</details>

## 📖 Usage

Start with `/start` to pick a language and open the interactive menu.

| Command | Description | Example |
|---------|-------------|---------|
| `/start` | Initialize session, choose language, open menu | `/start` |
| `/help` | Show quick help and available commands | `/help` |
| `/language` | Switch interface language and command menu | `/language` |
| `/show` | Display the current invoice draft | `/show` |
| `/save` | Save the current draft to SQLite | `/save` |
| `/edit` | Batch-edit header fields | `/edit supplier=ACME client=Corp date=2025-01-15` |
| `/edititem` | Edit a specific line item (1-based index) | `/edititem 1 name=Widget qty=5 price=10.50` |
| `/comment` | Append a comment to the active draft | `/comment Approved by manager` |
| `/invoices` | Query saved invoices by date and supplier | `/invoices 2025-01-01 2025-01-31 supplier=ACME` |

Inline buttons mirror the main workflow: upload invoice, edit header or line items, add comments, save draft, query by period, view help, and switch language.

## ⚙️ Configuration

<details>
<summary><b>Environment variables reference</b></summary>

### Required

| Variable | Description | Example |
|----------|-------------|---------|
| `BOT_TOKEN` | Telegram bot token from `@BotFather` | `123456:ABCDEF...` |

### Optional

| Variable | Description | Default |
|----------|-------------|---------|
| `OCR_PROVIDER` | OCR backend (`local` or `mindee`) | `local` |
| `OCR_LANGUAGES` | Tesseract language codes joined by `+` | `eng+rus` |
| `MINDEE_API_KEY` | Mindee API key (when `OCR_PROVIDER=mindee`) | empty |
| `MINDEE_MODEL_ID` | Mindee model ID (when `OCR_PROVIDER=mindee`) | empty |
| `LOG_LEVEL` | Logging level | `INFO` |
| `LOG_ROTATE_MB` | Max log file size in MB | `10` |
| `LOG_BACKUPS` | Number of rotated log backups | `5` |
| `LOG_CONSOLE` | Enable console logging (`0` or `1`) | `0` |
| `LOG_DIR` | Directory for log files | `logs` |

</details>

## 🗄️ Database

SQLite schema is managed with Alembic (`backend/alembic/versions/`).

<details>
<summary><b>Tables & migrations</b></summary>

| Table | Description |
|-------|-------------|
| `invoices` | Saved invoice headers (supplier, customer, date, number, totals) |
| `invoice_items` | Line items linked to each invoice |
| `comments` | User and automatic review comments |
| `invoice_drafts` | Active per-user drafts prior to saving |
| `user_languages` | Saved per-user interface language preference |

Run migrations from the project root:

```bash
python -m alembic -c backend/alembic.ini upgrade head
```

See [Database Guide](docs/en/database.md) for backup, restore, and schema details.

</details>

## 📁 Project Structure

```text
InvoiceFlowBot/
├── bot.py                          # Application entry point
├── scripts/                        # Cross-platform dev/ops scripts (python, linux, windows)
├── backend/
│   ├── config.py                   # Pydantic environment settings
│   ├── core/container.py           # Dependency injection container
│   ├── domain/                     # Domain models (invoices, drafts)
│   ├── handlers/
│   │   ├── commands*.py            # Command handlers (/start, /show, /edit, /invoices, ...)
│   │   ├── callbacks*.py           # Inline keyboard handlers
│   │   ├── file.py                 # PDF & image upload handlers
│   │   ├── language.py             # Language picker & Telegram menu localization
│   │   ├── locale_middleware.py    # Per-update locale resolution
│   │   ├── texts.py                # Locale registry & text formatting helpers
│   │   └── locales/                # JSON translation catalogs (de, en, es, fr, it, pt, ru)
│   ├── ocr/
│   │   ├── extract.py              # Extraction entry point
│   │   ├── engine/                 # OCR router, types, and utilities
│   │   └── providers/              # Local (Docling + Tesseract) and Mindee providers
│   ├── services/                   # Invoice & draft application services
│   ├── storage/                    # Async SQLite repositories & user language storage
│   └── alembic/                    # Alembic schema migrations
└── docs/                           # English & Russian documentation and screenshots
```

## 🛠️ Development & Testing

```bash
pip install -e .[dev]
python -m ruff check .
python -m mypy backend/
python -m pytest
```

Helper wrappers for setup, migrations, linting, formatting, and tests are also available in `scripts/python/`, `scripts/linux/`, and `scripts/windows/` (see [Scripts Guide](docs/en/scripts.md)).

## 📚 Documentation

- **English:** [docs/en/index.md](docs/en/index.md) · [Screenshots](docs/en/screenshots.md) · [Development](docs/en/development.md)
- **Русский:** [README.ru.md](README.ru.md) · [docs/ru/index.md](docs/ru/index.md) · [Скриншоты](docs/ru/screenshots.md)

## 📄 License

Licensed under the [Apache License 2.0](LICENSE). Copyright 2025 Ama.
