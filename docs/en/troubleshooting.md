<img src="https://capsule-render.vercel.app/api?type=waving&color=gradient&customColorList=6,11,20&height=120&section=header&text=Troubleshooting&fontSize=35&animation=fadeIn"/>

<div align="center">

<p align="center">
  <img src="https://readme-typing-svg.demolab.com?font=Fira+Code&size=18&duration=3000&pause=1000&center=true&vCenter=true&width=500&lines=Common+Issues;Quick+Solutions;Check+Logs" alt="Typing SVG" />
</p>

[![Solutions](https://img.shields.io/badge/Solutions-6+-blue?style=for-the-badge)](#-about-this-guide)
[![Quick Fix](https://img.shields.io/badge/Fix-Fast-green?style=for-the-badge)](#-sqlite3operationalerror-unable-to-open-database-file)
[![Logs](https://img.shields.io/badge/Check-Logs-orange?style=for-the-badge)](#logs-are-empty)

</div>

## 📋 About This Guide

Check the failing command's output first. In Docker, use `docker compose logs bot`. Application warnings and exceptions go to `logs/errors.log` by default.

## ❌ sqlite3.OperationalError: unable to open database file

Check that `./data.sqlite` on the host is a regular file that the container can write. If Docker created a directory at that path, stop the service with `docker compose down`, check the directory's contents and rename it. Then follow the [Docker setup](setup-docker.md#start-the-stack) to create the missing file. Preserve any existing database file.

## Bot does not respond in Telegram

Check `BOT_TOKEN` and the host's connection to `api.telegram.org`. Restart the local process after an environment change. For Compose, run `docker compose up -d --force-recreate bot` after editing `.env`.

## Local OCR errors

Check that `tesseract --list-langs` includes the languages configured in `OCR_LANGUAGES` (default `eng+rus`). The first OCR request needs access to Hugging Face unless the Docling models are already cached.

## Mindee API errors

If `OCR_PROVIDER=mindee`, verify `MINDEE_API_KEY`, `MINDEE_MODEL_ID`, and network access to Mindee. Check `logs/errors.log` for provider warnings and any logged exception details.

## File processing errors

Try a valid PDF, JPEG, PNG, or WebP. Convert HEIC/HEIF to JPEG or PNG before uploading. If image normalization fails, look for the exception in `logs/errors.log`.

## OCR service errors

The bot can report that recognition is unavailable for either provider. Check `OCR_PROVIDER` and follow the relevant checks above. Review `logs/errors.log` for the failure that the provider or upload handler recorded.

## Docker container exits immediately

Run `docker compose logs bot`, check `BOT_TOKEN`, and verify that the container user can write to the database and log paths. During startup, Alembic and configuration errors can appear in the container output.

## Logs are empty

Check the configured log level and the active log directory. The app creates the directory if it has permission. With a relative `LOG_DIR`, check the path from the working directory. To mirror application messages to stderr, set `LOG_CONSOLE=1` and restart or recreate the process.
