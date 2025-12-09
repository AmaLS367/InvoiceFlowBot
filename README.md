<img src="https://capsule-render.vercel.app/api?type=waving&color=gradient&customColorList=12,16,20&height=200&section=header&text=InvoiceFlowBot&fontSize=60&animation=fadeIn&fontAlignY=35&desc=Automated%20Invoice%20Processing%20with%20OCR&descAlignY=55&descSize=20"/>

<div align="center">

<p align="center">
  <img src="https://readme-typing-svg.demolab.com?font=Fira+Code&size=22&duration=3000&pause=1000&center=true&vCenter=true&width=600&lines=Automated+Invoice+Processing;OCR+%7C+Telegram+Bot+%7C+SQLite;Extract+%7C+Edit+%7C+Save+%7C+Query;Mindee+API+%2B+Python+3.11%2B" alt="Typing SVG" />
</p>

[![CI](https://img.shields.io/github/actions/workflow/status/AmaLS367/InvoiceFlowBot/ci.yml?style=for-the-badge&logo=github&label=CI&color=success)](https://github.com/AmaLS367/InvoiceFlowBot/actions/workflows/ci.yml)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/downloads/)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg?style=for-the-badge)](https://opensource.org/licenses/Apache-2.0)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg?style=for-the-badge)](https://github.com/astral-sh/ruff)
[![Telegram](https://img.shields.io/badge/Telegram-Bot-blue?style=for-the-badge&logo=telegram)](https://telegram.org/)

<p align="center">
  <img src="https://img.shields.io/badge/OCR-Mindee-4A90E2?style=for-the-badge&logo=data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjQiIGhlaWdodD0iMjQiIHZpZXdCb3g9IjAgMCAyNCAyNCIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHBhdGggZD0iTTEyIDJMMiA3TDEyIDEyTDIyIDdMMTIgMloiIGZpbGw9IndoaXRlIi8+CjxwYXRoIGQ9Ik0yIDEzTDEyIDE4TDIyIDEzIiBzdHJva2U9IndoaXRlIiBzdHJva2Utd2lkdGg9IjIiLz4KPC9zdmc+" alt="OCR" />
  <img src="https://img.shields.io/badge/Database-SQLite-003B57?style=for-the-badge&logo=sqlite&logoColor=white" alt="SQLite" />
  <img src="https://img.shields.io/badge/Framework-Aiogram_3-2CA5E0?style=for-the-badge&logo=telegram&logoColor=white" alt="Aiogram" />
</p>

---

> 🇷🇺 **Русская документация:** [README.ru.md](README.ru.md) • [docs/ru/index.md](docs/ru/index.md)

</div>

<br/>

A Telegram bot for automated invoice processing using OCR technology. The bot extracts structured data from PDF invoices and photos, allowing users to review, edit, and save invoice information to a database.


## ✨ Features

<div align="center">

```mermaid
graph LR
    A[📱 Upload] -->|PDF/Image| B[🔍 OCR Extract]
    B -->|Parse Data| C[✏️ Edit Draft]
    C -->|Confirm| D[💾 SQLite]
    D -->|Query| E[📊 Reports]

    style A fill:#4A90E2,stroke:#2c3e50,stroke-width:2px,color:#fff
    style B fill:#FF6B6B,stroke:#2c3e50,stroke-width:2px,color:#fff
    style C fill:#FFD93D,stroke:#2c3e50,stroke-width:2px,color:#333
    style D fill:#50C878,stroke:#2c3e50,stroke-width:2px,color:#fff
    style E fill:#B19CD9,stroke:#2c3e50,stroke-width:2px,color:#fff
```

</div>

| Feature | Description | Status |
|---------|-------------|--------|
| 🤖 **OCR Processing** | Automatic extraction via Mindee API with provider abstraction | ![](https://img.shields.io/badge/-Ready-success?style=flat-square) |
| 📎 **Multiple Formats** | PDF, JPEG, PNG, HEIC, HEIF, WebP | ![](https://img.shields.io/badge/-Ready-success?style=flat-square) |
| ✏️ **Interactive Editing** | Edit headers and line items via Telegram | ![](https://img.shields.io/badge/-Ready-success?style=flat-square) |
| 💾 **Data Storage** | SQLite with Alembic migrations | ![](https://img.shields.io/badge/-Ready-success?style=flat-square) |
| 📅 **Period Queries** | Filter by date range and supplier | ![](https://img.shields.io/badge/-Ready-success?style=flat-square) |
| 💬 **Comment System** | Add notes to invoices | ![](https://img.shields.io/badge/-Ready-success?style=flat-square) |
| 📊 **CSV Export** | Export line items for analysis | ![](https://img.shields.io/badge/-Ready-success?style=flat-square) |

## 📋 Requirements

- 🐍 Python 3.11+
- 🤖 Telegram Bot Token
- 🔑 Mindee API Key

## 🚀 Quick Start with Docker

> [!TIP]
> The fastest way to get started! Docker handles all dependencies automatically.

```powershell
# 1. Clone and setup environment
git clone https://github.com/AmaLS367/InvoiceFlowBot.git
cd InvoiceFlowBot
Copy-Item .env.example .env

# 2. Edit .env with your tokens
notepad .env

# 3. Start the bot
docker-compose up --build -d

# 4. Check logs
docker-compose logs -f

# 5. Stop when done
docker-compose down
```

## 💻 Installation

> [!NOTE]
> Requires Python 3.11+ and Git installed on your system.

<details>
<summary><b>📦 Step-by-step installation guide</b></summary>

### 1. Clone the repository
```powershell
git clone https://github.com/AmaLS367/InvoiceFlowBot.git
cd InvoiceFlowBot
```

### 2. Create a virtual environment
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3. Install dependencies
```powershell
pip install -e .
```

### 4. Create a `.env` file in the project root
```env
BOT_TOKEN=your_telegram_bot_token
MINDEE_API_KEY=your_mindee_api_key
MINDEE_MODEL_ID=your_mindee_model_id

# Optional logging configuration
LOG_LEVEL=INFO
LOG_ROTATE_MB=10
LOG_BACKUPS=5
LOG_CONSOLE=0
LOG_DIR=logs
```

### ⚙️ Configuration

The bot is configured via environment variables managed by pydantic settings in `config.py`.

For local development you can create a `.env` file in the project root:

```env
BOT_TOKEN=123456:ABCDEF_your_bot_token
MINDEE_API_KEY=your-mindee-api-key
MINDEE_MODEL_ID=mindee/invoices/v4
DB_FILENAME=data.sqlite
```

On startup the application reads these values into the `Settings` model.

### 5. Run the bot
```powershell
python bot.py
```

> [!TIP]
> Check `logs/` directory for detailed application logs if you encounter any issues.

</details>

## 🧪 Tests

Run unit tests with `pytest`. On Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e .[dev]
pytest
```

You can also run a specific test file:

```powershell
python -m pytest tests/test_invoice_service.py
```

## 📖 Usage

> [!TIP]
> New to the bot? Start with `/start` to see the interactive menu!

<details>
<summary><b>🎯 Basic Commands</b></summary>

| Command | Description |
|---------|-------------|
| `/start` | Start the bot and see main menu |
| `/help` | Show help message |
| `/show` | Display current draft invoice |
| `/save` | Save current draft to database |

</details>

<details>
<summary><b>✏️ Editing Commands</b></summary>

| Command | Description | Example |
|---------|-------------|---------|
| `/edit` | Edit header fields | `/edit supplier=ACME client=Corp date=2024-01-15` |
| `/edititem` | Edit specific line item | `/edititem 0 name=Widget qty=5 price=10.50` |
| `/comment` | Add a comment | `/comment Approved by manager` |

</details>

<details>
<summary><b>🔍 Query Commands</b></summary>

```
/invoices YYYY-MM-DD YYYY-MM-DD [supplier=text]
```

**Example:**
```
/invoices 2024-01-01 2024-01-31 supplier=ACME
```

</details>

<details>
<summary><b>🔘 Interactive Buttons</b></summary>

The bot provides inline keyboard buttons for:
- 📤 Upload invoice
- ✏️ Edit invoice fields
- 💬 Add comments
- 💾 Save invoice
- 📅 Query invoices by period
- ❓ View help

</details>

<div align="center">

## 📊 Project Stats

<p align="center">
  <img src="https://img.shields.io/github/languages/top/AmaLS367/InvoiceFlowBot?style=for-the-badge&color=blue" alt="Top Language"/>
  <img src="https://img.shields.io/github/languages/code-size/AmaLS367/InvoiceFlowBot?style=for-the-badge&color=green" alt="Code Size"/>
  <img src="https://img.shields.io/github/last-commit/AmaLS367/InvoiceFlowBot?style=for-the-badge&color=orange" alt="Last Commit"/>
</p>

<img src="https://github-readme-activity-graph.vercel.app/graph?username=AmaLS367&repo=InvoiceFlowBot&theme=react-dark&hide_border=true&area=true" width="100%"/>

</div>

## 📁 Project Structure

```
InvoiceFlowBot/
├── bot.py                 # Main bot entry point
├── config.py              # Configuration management
├── domain/
│   └── invoices.py        # Domain entities (Invoice, InvoiceHeader, InvoiceItem, etc.)
├── services/
│   └── invoice_service.py # Service layer (OCR orchestration, domain conversion)
├── handlers/
│   ├── commands.py        # Text command handlers (/show, /edit, /invoices, etc.)
│   ├── callbacks.py       # Callback query handlers (inline button actions)
│   ├── file.py            # File upload handlers
│   ├── state.py           # Global state management
│   └── utils.py           # Utility functions and keyboards
├── ocr/
│   ├── extract.py         # Invoice extraction entry point
│   ├── mindee_client.py   # Mindee API integration
│   ├── providers/         # OCR provider abstraction layer
│   │   ├── base.py        # OcrProvider interface
│   │   └── mindee_provider.py  # Mindee provider implementation
│   └── engine/
│       ├── router.py      # OCR routing logic (uses providers)
│       ├── types.py       # Data type definitions
│       └── util.py        # OCR utilities and logging
└── storage/
    └── db.py              # Database operations
```

## ⚙️ Configuration

The bot uses environment variables for configuration. See `.env.example` for available options.

<details>
<summary><b>📋 Environment Variables Reference</b></summary>

### 🔑 Required Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `BOT_TOKEN` | Telegram bot token from @BotFather | `123456:ABCDEF...` |
| `MINDEE_API_KEY` | API key from Mindee platform | `your-api-key` |
| `MINDEE_MODEL_ID` | Mindee model ID for invoice processing | `mindee/invoices/v4` |

> [!WARNING]
> The bot will not start without these required variables!

### 🔧 Optional Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `LOG_LEVEL` | Logging level | `INFO` |
| `LOG_ROTATE_MB` | Max log file size in MB | `10` |
| `LOG_BACKUPS` | Number of backup log files | `5` |
| `LOG_CONSOLE` | Enable console logging | `0` |
| `LOG_DIR` | Custom log directory | `logs` |

</details>

## 🗄️ Database

The bot uses SQLite database to store invoices. The database schema is managed by Alembic.

<details>
<summary><b>🔨 Database Setup & Structure</b></summary>

### Initial Setup

```powershell
python -m alembic upgrade head
```

> [!NOTE]
> The application automatically runs migrations on startup via `storage.db.init_db()`.

### Database Tables

| Table | Description |
|-------|-------------|
| `invoices` | Header information (supplier, client, dates, totals) |
| `invoice_items` | Line items for each invoice |
| `comments` | User comments associated with invoices |
| `invoice_drafts` | Temporary drafts for editing |

### Backup & Restore

```powershell
# Backup
Copy-Item .\data.sqlite .\backup\data-$(Get-Date -Format yyyyMMddHHmmss).sqlite

# Restore
Copy-Item .\backup\data-20240115.sqlite .\data.sqlite
```

> [!WARNING]
> Always backup `data.sqlite` before major updates!

</details>

## 📝 Logging

Logs are written to the `logs/` directory by default:
- `ocr_engine.log` - General application logs
- `errors.log` - Error and warning logs
- `router.log` - OCR routing logs
- `extract.log` - Invoice extraction logs

## 📚 Documentation

- [docs/ru/index.md](docs/ru/index.md)
- [docs/en/index.md](docs/en/index.md)

## 📸 Screenshots

- [Screenshots (RU)](docs/ru/screenshots.md)
- [Bot screenshots (EN)](docs/en/screenshots.md)

## 📄 License

Copyright 2025 Ama

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

## 👨‍💻 Development

### 🔍 Code Quality

The project uses the following tools for code quality:

- **ruff** - Fast Python linter
- **mypy** - Static type checking

### 🛠️ Local Development Setup

```powershell
# Install dependencies
pip install -e .
pip install -e .[dev]

# Run linter
python -m ruff check .

# Run type checker
python -m mypy domain services ocr storage

# Run tests
python -m pytest
```

The CI pipeline automatically runs `ruff`, `mypy`, and `pytest` on every push and pull request.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 💬 Support

For issues and questions, please open an issue on the repository.

---

<div align="center">

### 🌟 Star History

[![Star History Chart](https://api.star-history.com/svg?repos=AmaLS367/InvoiceFlowBot&type=Date)](https://star-history.com/#AmaLS367/InvoiceFlowBot&Date)

<img src="https://capsule-render.vercel.app/api?type=waving&color=gradient&height=100&section=footer"/>

**Made with ❤️ by [Ama](https://github.com/AmaLS367)**

</div>
