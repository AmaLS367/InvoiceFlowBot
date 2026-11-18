<img src="https://capsule-render.vercel.app/api?type=waving&color=gradient&customColorList=12,16,20&height=120&section=header&text=Configuration&fontSize=40&animation=fadeIn"/>

<div align="center">

[![dotenv](https://img.shields.io/badge/.env-Configuration-blue?style=for-the-badge)](https://github.com/theskumar/python-dotenv)
[![pydantic](https://img.shields.io/badge/Pydantic-Settings-green?style=for-the-badge&logo=pydantic)](https://docs.pydantic.dev/)
[![Variables](https://img.shields.io/badge/Env%20Vars-11-orange?style=for-the-badge)](#-required-variables)

</div>

## 📋 About Configuration

Pydantic Settings reads environment variables and the `.env` file from the current working directory. Environment variables take precedence. Run local commands from the project root.

> [!IMPORTANT]
> The bot will not start without required variables!

## 🔑 Required variables

These variables are mandatory. If they are not set, the application will terminate at startup with a clear error message.

| Variable | Purpose | Accepted values | Default |
| --- | --- | --- | --- |
| `BOT_TOKEN` | Telegram bot token used by Aiogram | Token from @BotFather | none (startup fails without it) |

## 🔧 Optional variables

| Variable | Purpose | Accepted values | Default |
| --- | --- | --- | --- |
| `OCR_PROVIDER` | OCR backend | `local`, `mindee` | `local` |
| `OCR_LANGUAGES` | Installed Tesseract language codes joined with `+` | e.g. `eng+rus` | `eng+rus` |
| `MINDEE_API_KEY` | API key when `OCR_PROVIDER=mindee` | Mindee API key | empty |
| `MINDEE_MODEL_ID` | Model ID when `OCR_PROVIDER=mindee` | e.g. `mindee/invoices/v4` or a UUID | empty |
| `INVOICE_DB_PATH` | Path to the SQLite file | Absolute path or path relative to `backend/` | `../data.sqlite` |
| `LOG_LEVEL` | Base logging level | `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL` | `INFO` |
| `LOG_ROTATE_MB` | Size threshold before rotating log files | Integer megabytes | `10` |
| `LOG_BACKUPS` | Number of rotated log backups to keep | Integer | `5` |
| `LOG_CONSOLE` | Mirror application logs to stderr | Enable with `1`, `true`, or `True` | `0` |
| `LOG_DIR` | Custom directory for log files | Absolute or relative path | `logs` inside the repo |

`ARTIFACTS_DIR` defaults to `data/artifacts` for the synchronous OCR helper. The Telegram upload handler always writes to `temp/` relative to the working directory. `UPLOAD_FOLDER` is declared in settings without a consumer.

For local OCR in Compose, `HF_HOME` points to the model-cache volume at `/app/data/huggingface`. Set `HF_HUB_OFFLINE=1` in the process environment or the Compose `.env` after the models are cached.

`LOG_DIR` affects where `ocr_engine.log`, `errors.log`, `router.log`, and `extract.log` appear. If it is unset, the application creates `logs/` automatically.

## Working with `.env`

- Do not commit `.env`; use `.env.example` as the shared template.
- Restart the local bot or run `docker compose up -d --force-recreate bot` after editing the Compose `.env` file.
- Keep separate `.env` files for each environment (development, staging, production) with their own tokens and database paths.
