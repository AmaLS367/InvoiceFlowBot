# Configuration

All settings live in environment variables. `config.py` loads `.env` with `os.getenv`, so updating the file and restarting the process is enough to apply changes.

## Required variables

| Variable | Purpose | Accepted values | Default |
| --- | --- | --- | --- |
| `BOT_TOKEN` | Telegram bot token used by Aiogram | Token from @BotFather | none (startup fails without it) |
| `MINDEE_API_KEY` | Mindee API key for invoice extraction | API key from the Mindee console (https://platform.mindee.com/) | none (startup fails without it) |
| `MINDEE_MODEL_ID` | Mindee model identifier for invoice processing | Model ID from Mindee platform (e.g., `mindee/invoices/v4` or custom model UUID) | none (startup fails without it) |

## Optional variables

| Variable | Purpose | Accepted values | Default |
| --- | --- | --- | --- |
| `INVOICE_DB_PATH` | Path to the SQLite file | Any valid file path | `data.sqlite` |
| `LOG_LEVEL` | Base logging level | `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL` | `INFO` |
| `LOG_ROTATE_MB` | Size threshold before rotating log files | Integer megabytes | `10` |
| `LOG_BACKUPS` | Number of rotated log backups to keep | Integer | `5` |
| `LOG_CONSOLE` | Mirror logs to stdout/stderr | `0`/`1`, `true`/`false` | `0` |
| `LOG_DIR` | Custom directory for log files | Absolute or relative path | `logs` inside the repo |

`LOG_DIR` affects where `ocr_engine.log`, `errors.log`, `router.log`, and `extract.log` appear. If it is unset, the application creates `logs/` automatically.

## Working with `.env`

- Do not commit `.env`; use `.env.example` as the shared template.
- Restart the bot or recreate the Docker container after updating variables.
- Keep separate `.env` files for each environment (development, staging, production) with their own tokens and database paths.

