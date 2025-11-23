# Local Setup

## Prerequisites

- Python 3.8 or newer
- Git installed
- Telegram bot token and Mindee API credentials

## Steps

1. **Clone the repository and enter the project directory:**
```powershell
git clone https://github.com/AmaLS367/InvoiceFlowBot.git
cd InvoiceFlowBot
```

2. **Create and activate a Windows virtual environment:**
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

3. **Install runtime dependencies:**
```powershell
pip install -e .
```

4. **Create `.env` from the template and set required variables:**
```powershell
Copy-Item .env.example .env
notepad .env
```

Required values:
- `BOT_TOKEN` — token from @BotFather.
- `MINDEE_API_KEY` — Mindee API key.
- `Model_id_mindee` — Mindee model identifier for invoices.

5. **Run the bot:**
```powershell
python bot.py
```

## Notes

- A successful launch prints log lines about Aiogram startup. If something fails, check the console or log files for stack traces.
- When the bot does not connect to Telegram, double-check `BOT_TOKEN`, confirm internet access, and restart the process after fixing the `.env`.
