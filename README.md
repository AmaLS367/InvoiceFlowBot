# InvoiceFlowBot
[![CI](https://github.com/AmaLS367/InvoiceFlowBot/actions/workflows/ci.yml/badge.svg)](https://github.com/AmaLS367/InvoiceFlowBot/actions/workflows/ci.yml)

For Russian documentation see [README.ru.md](README.ru.md) and [docs/ru/index.md](docs/ru/index.md).

A Telegram bot for automated invoice processing using OCR technology. The bot extracts structured data from PDF invoices and photos, allowing users to review, edit, and save invoice information to a database.

## Features

- **OCR Processing**: Automatic extraction of invoice data using Mindee API. The OCR layer is built on a provider abstraction, allowing for easy integration of additional OCR providers in the future.
- **Multiple Format Support**: Handles PDF files and images (JPEG, PNG, HEIC, HEIF, WebP)
- **Interactive Editing**: Edit invoice header fields and line items via Telegram interface
- **Data Storage**: Save processed invoices to SQLite database
- **Period Queries**: Query invoices by date range and supplier
- **Comment System**: Add comments to invoices
- **CSV Export**: Export invoice items as CSV for large invoices

## Requirements

- Python 3.11+
- Telegram Bot Token
- Mindee API Key

## Quick Start with Docker

1. Clone the repository and copy the example env: `Copy-Item .env.example .env`
2. Start the stack: `docker-compose up --build -d`
3. Stop the stack: `docker-compose down`

## Installation

1. Clone the repository:
```powershell
git clone https://github.com/AmaLS367/InvoiceFlowBot.git
cd InvoiceFlowBot
```

2. Create a virtual environment:
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

3. Install dependencies:
```powershell
pip install -e .
```

4. Create a `.env` file in the project root:
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

### Configuration

The bot is configured via environment variables managed by pydantic settings in `config.py`.

For local development you can create a `.env` file in the project root:

```env
BOT_TOKEN=123456:ABCDEF_your_bot_token
MINDEE_API_KEY=your-mindee-api-key
MINDEE_MODEL_ID=mindee/invoices/v4
DB_FILENAME=data.sqlite
```

On startup the application reads these values into the `Settings` model.

5. Run the bot:
```powershell
python bot.py
```

## Tests

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

## Usage

### Basic Commands

- `/start` - Start the bot and see main menu
- `/help` - Show help message
- `/show` - Display current draft invoice
- `/save` - Save current draft to database

### Editing Commands

- `/edit supplier=... client=... date=YYYY-MM-DD doc=... total=123.45` - Edit header fields
- `/edititem <index> name=... qty=... price=... total=...` - Edit specific line item
- `/comment <text>` - Add a comment to the invoice

### Query Commands

- `/invoices YYYY-MM-DD YYYY-MM-DD [supplier=text]` - Query invoices by date range and optional supplier filter

### Interactive Buttons

The bot provides inline keyboard buttons for:
- Upload invoice
- Edit invoice fields
- Add comments
- Save invoice
- Query invoices by period
- View help

## Project Structure

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

## Configuration

The bot uses environment variables for configuration. See `.env.example` for available options.

### Required Variables

- `BOT_TOKEN`: Telegram bot token from @BotFather
- `MINDEE_API_KEY`: API key from Mindee platform
- `MINDEE_MODEL_ID`: Mindee model ID for invoice processing

### Optional Variables

- `LOG_LEVEL`: Logging level (DEBUG, INFO, WARNING, ERROR)
- `LOG_ROTATE_MB`: Maximum log file size in MB before rotation
- `LOG_BACKUPS`: Number of backup log files to keep
- `LOG_CONSOLE`: Enable console logging (0 or 1)
- `LOG_DIR`: Custom log directory path

## Database

The bot uses SQLite database to store invoices. The database schema is managed by Alembic.

### Database setup

Before running the bot or tests make sure the schema is up to date:

```powershell
python -m alembic upgrade head
```

The application entrypoints call `storage.db.init_db()`, which will also upgrade the database to the latest migration.

The database tables include:
- Invoices (header information)
- Items (line items for each invoice)
- Comments (comments associated with invoices)
- Invoice drafts (temporary drafts for editing)

## Logging

Logs are written to the `logs/` directory by default:
- `ocr_engine.log` - General application logs
- `errors.log` - Error and warning logs
- `router.log` - OCR routing logs
- `extract.log` - Invoice extraction logs

## Documentation

- [docs/ru/index.md](docs/ru/index.md)
- [docs/en/index.md](docs/en/index.md)

## Screenshots

- [Screenshots (RU)](docs/ru/screenshots.md)
- [Bot screenshots (EN)](docs/en/screenshots.md)

## License

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

## Development

### Code Quality

The project uses the following tools for code quality:

- **ruff** - Fast Python linter
- **mypy** - Static type checking

### Local Development Setup

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

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

For issues and questions, please open an issue on the repository.
