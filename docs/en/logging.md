<img src="https://capsule-render.vercel.app/api?type=waving&color=gradient&customColorList=12,16,20&height=120&section=header&text=Logging&fontSize=40&animation=fadeIn"/>

<div align="center">

[![Rotating](https://img.shields.io/badge/Handler-Rotating-blue?style=for-the-badge)](https://docs.python.org/3/library/logging.handlers.html)
[![Files](https://img.shields.io/badge/Log%20Files-4-green?style=for-the-badge)](#-log-files)
[![Levels](https://img.shields.io/badge/Levels-Configurable-orange?style=for-the-badge)](#configuration-knobs)

</div>

## 📋 About Logging

`backend.ocr.engine.util` configures rotating log handlers the first time `get_logger` runs. By default logs live in `logs/` next to the source code or inside the directory specified via `LOG_DIR`.

> [!TIP]
> For startup errors, check the process output or `docker compose logs bot`. For application errors, start with `errors.log`.

## 📁 Log files

- `ocr_engine.log` — general application events, OCR steps, and file processing.
- `errors.log` — warnings and errors (level `WARNING` and above).
- `router.log` — messages from the `ocr.router` logger when using the synchronous OCR helper.
- `extract.log` — messages from the synchronous OCR wrapper in `backend.ocr.extract`.

The asynchronous Telegram upload path records its application messages in `ocr_engine.log` and its warnings and errors in `errors.log`.

## Configuration knobs

| Variable | Effect |
| --- | --- |
| `LOG_LEVEL` | Base logging level (`DEBUG` for verbose tracing, `INFO` for production). |
| `LOG_ROTATE_MB` | Maximum size before rotating each log file. |
| `LOG_BACKUPS` | Number of rotated log archives to keep. |
| `LOG_CONSOLE` | Mirror application logs to stderr. |
| `LOG_DIR` | Custom log directory. The app creates it if permissions allow. |

Handlers use `RotatingFileHandler`, so once a file reaches the limit it is renamed to `.1`, `.2`, etc.

## Recommendations

- Enable `LOG_LEVEL=DEBUG` when investigating issues that require more detail.
- For containers, set `LOG_CONSOLE=1` and watch `docker compose logs -f bot` while debugging.
- Ensure the log directory is writable so the bot can start.
