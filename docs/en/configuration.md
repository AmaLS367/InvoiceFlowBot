# Configuration

The application configuration is managed through a pydantic `Settings` model in `config.py`.

All configuration values are loaded from environment variables and an optional `.env` file in the project root.

## Settings model

The `config.Settings` model reads the following keys:

- `BOT_TOKEN`  
  Telegram bot token. Required.

- `MINDEE_API_KEY`  
  Mindee API key used by the OCR client. Required.

- `MINDEE_MODEL_ID`  
  Mindee model identifier. Required.

- `DB_FILENAME` (or `INVOICE_DB_PATH`)  
  Name of the SQLite database file. Defaults to `data.sqlite` if not set.

- `DB_DIR`  
  Directory where the database file is stored. By default this is the project directory where `config.py` is located.

- `UPLOAD_FOLDER`  
  Directory for uploaded files. Defaults to `data/uploads`.

- `ARTIFACTS_DIR`  
  Directory for OCR artifacts. Defaults to `data/artifacts`.

- `LOG_LEVEL`  
  Logging level (DEBUG, INFO, WARNING, ERROR). Defaults to `INFO`.

- `LOG_ROTATE_MB`  
  Maximum log file size in MB before rotation. Defaults to `10`.

- `LOG_BACKUPS`  
  Number of backup log files to keep. Defaults to `5`.

- `LOG_CONSOLE`  
  Enable console logging (0 or 1). Defaults to `0`.

- `LOG_DIR`  
  Custom log directory path. Optional.

The settings instance is created once via `get_settings()` with an `lru_cache`, and the module exposes convenience constants such as `BOT_TOKEN`, `MINDEE_API_KEY`, and `DB_PATH`.

## Environment variables and .env file

By default `config.Settings` is configured with:

```python
model_config = SettingsConfigDict(
    env_file=".env",
    env_file_encoding="utf-8",
    extra="ignore",
)
```

This means:

* Values can be provided as real environment variables.
* In local development you can keep them in a `.env` file in the project root.

Example `.env` file:

```env
BOT_TOKEN=123456:ABCDEF_your_bot_token
MINDEE_API_KEY=your-mindee-api-key
MINDEE_MODEL_ID=mindee/invoices/v4

# Optional database configuration
INVOICE_DB_PATH=data.sqlite
# DB_DIR=D:\invoiceflowbot\data

# Optional logging configuration
LOG_LEVEL=INFO
LOG_ROTATE_MB=10
LOG_BACKUPS=5
LOG_CONSOLE=0
LOG_DIR=logs
```

## How the config is used in the code

Typical usage patterns:

* Telegram bot entrypoint:

  ```python
  from config import BOT_TOKEN

  bot = Bot(token=BOT_TOKEN)
  ```

* Mindee OCR client:

  ```python
  import config

  MINDEE_API_KEY = config.MINDEE_API_KEY
  ```

* Database path:

  ```python
  import config

  DB_PATH = config.DB_PATH
  ```

All modules should rely on the `config` module instead of calling `os.getenv` directly. This keeps configuration in one place and makes tests easier to control via monkeypatching.

