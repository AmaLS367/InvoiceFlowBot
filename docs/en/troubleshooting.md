<img src="https://capsule-render.vercel.app/api?type=waving&color=gradient&customColorList=6,11,20&height=120&section=header&text=Troubleshooting&fontSize=35&animation=fadeIn"/>

<div align="center">

<p align="center">
  <img src="https://readme-typing-svg.demolab.com?font=Fira+Code&size=18&duration=3000&pause=1000&center=true&vCenter=true&width=500&lines=Common+Issues;Quick+Solutions;Check+Logs" alt="Typing SVG" />
</p>

[![Solutions](https://img.shields.io/badge/Solutions-6+-blue?style=for-the-badge)](troubleshooting.md)
[![Quick Fix](https://img.shields.io/badge/Fix-Fast-green?style=for-the-badge)](#sqlite3operationalerror-unable-to-open-database-file)
[![Logs](https://img.shields.io/badge/Check-Logs-orange?style=for-the-badge)](#logs-are-empty)

</div>

## 📋 About This Guide

> [!TIP]
> Most problems can be solved by checking environment variables and logs in `logs/`

## ❌ sqlite3.OperationalError: unable to open database file
- **Problem:** the container cannot open `data.sqlite`.
- **Cause:** Docker mounted a directory instead of a file because `data.sqlite` was missing.
- **Fix:** stop the container, delete the directory, create an empty file with `New-Item .\data.sqlite -ItemType File | Out-Null`, then run `docker-compose up --build -d`.

## Bot does not respond in Telegram
- **Problem:** commands stay unanswered or Telegram reports token errors.
- **Cause:** wrong `BOT_TOKEN`, network restrictions, or Telegram is blocked.
- **Fix:** verify the token inside `.env`, ensure the host can reach `api.telegram.org`, and restart the bot. Inspect `logs/errors.log` for stack traces.

## Mindee API errors
- **Problem:** OCR fails with Mindee-related messages.
- **Cause:** invalid `MINDEE_API_KEY`, incorrect `MINDEE_MODEL_ID`, or transient network issues.
- **Fix:** update credentials in `.env`, confirm that the Mindee account is active, and retry once connectivity is restored.

## File processing errors
- **Problem:** bot reports "Не удалось обработать файл" (Failed to process file) or similar error messages.
- **Cause:** corrupted PDF, unsupported image format, or file conversion failure (e.g., HEIC/HEIF to JPEG).
- **Behavior:** the bot sends a user-friendly error message in Telegram and logs detailed error information (including file path and exception traceback) to `logs/errors.log` for debugging.
- **Fix:** ensure the file is a valid PDF or supported image format (JPEG, PNG). For HEIC/HEIF files, the bot attempts automatic conversion; if it fails, try converting manually before uploading.

## OCR service errors
- **Problem:** bot responds with "Сервис распознавания сейчас недоступен" (OCR service temporarily unavailable).
- **Cause:** network timeout, Mindee API 4xx/5xx response, or service outage.
- **Behavior:** the bot sends a user-friendly message to the user and logs the full error details (including request path, response status, and exception) to `logs/errors.log` for investigation.
- **Fix:** check network connectivity, verify Mindee API status, and retry after a short delay. Review `logs/errors.log` for specific error codes or messages.

## Docker container exits immediately
- **Problem:** `docker ps` shows the service stopping right after launch.
- **Cause:** missing mandatory environment variables or missing write access to logs/database.
- **Fix:** review `docker logs <container>`, provide `BOT_TOKEN`, `MINDEE_API_KEY`, `MINDEE_MODEL_ID`, and make sure `logs/` plus `data.sqlite` are writable.

## Logs are empty
- **Problem:** no log files appear, even under load.
- **Cause:** `LOG_DIR` points to a non-existent path or log level is too strict.
- **Fix:** create the directory or remove `LOG_DIR` to fall back to `logs/`. Set `LOG_LEVEL=INFO` to verify the pipeline.
