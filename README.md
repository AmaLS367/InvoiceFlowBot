# Invoice Bot

A Telegram bot for automated invoice processing using OCR technology. The bot extracts structured data from PDF invoices and photos, allowing users to review, edit, and save invoice information to a database.

## Features

- **OCR Processing**: Automatic extraction of invoice data using Mindee API
- **Multiple Format Support**: Handles PDF files and images (JPEG, PNG, HEIC, HEIF, WebP)
- **Interactive Editing**: Edit invoice header fields and line items via Telegram interface
- **Data Storage**: Save processed invoices to SQLite database
- **Period Queries**: Query invoices by date range and supplier
- **Comment System**: Add comments to invoices
- **CSV Export**: Export invoice items as CSV for large invoices

## Requirements

- Python 3.8+
- Telegram Bot Token
- Mindee API Key

## Installation

1. Clone the repository:
```bash
git clone https://github.com/AmaLS367/Invoice_bot
cd invoice_bot
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the project root:
```env
BOT_TOKEN=your_telegram_bot_token
MINDEE_API_KEY=your_mindee_api_key
Model_id_mindee=your_mindee_model_id

# Optional logging configuration
LOG_LEVEL=INFO
LOG_ROTATE_MB=10
LOG_BACKUPS=5
LOG_CONSOLE=0
LOG_DIR=logs
```

5. Run the bot:
```bash
python bot.py
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
invoice_bot/
├── bot.py                 # Main bot entry point
├── config.py              # Configuration management
├── handlers/
│   ├── commands.py        # Command handlers
│   ├── file.py            # File upload handlers
│   ├── state.py           # Global state management
│   └── utils.py           # Utility functions and keyboards
├── ocr/
│   ├── extract.py         # Invoice extraction entry point
│   ├── mindee_client.py   # Mindee API integration
│   └── engine/
│       ├── router.py      # OCR routing logic
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
- `Model_id_mindee`: Mindee model ID for invoice processing

### Optional Variables

- `LOG_LEVEL`: Logging level (DEBUG, INFO, WARNING, ERROR)
- `LOG_ROTATE_MB`: Maximum log file size in MB before rotation
- `LOG_BACKUPS`: Number of backup log files to keep
- `LOG_CONSOLE`: Enable console logging (0 or 1)
- `LOG_DIR`: Custom log directory path

## Database

The bot uses SQLite database to store invoices. The database is automatically initialized on first run. Tables include:
- Invoices (header information)
- Items (line items for each invoice)
- Comments (comments associated with invoices)

## Logging

Logs are written to the `logs/` directory by default:
- `ocr_engine.log` - General application logs
- `errors.log` - Error and warning logs
- `router.log` - OCR routing logs
- `extract.log` - Invoice extraction logs

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

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

For issues and questions, please open an issue on the repository.

