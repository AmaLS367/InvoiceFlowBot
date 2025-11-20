# Troubleshooting

## sqlite3.OperationalError: unable to open database file
- **Problem:** the container cannot open `data.sqlite`.
- **Cause:** Docker mounted a directory instead of a file because `data.sqlite` was missing.
- **Fix:** stop the container, delete the directory, create an empty file with `New-Item .\data.sqlite -ItemType File | Out-Null`, then run `docker-compose up --build -d`.

## Bot does not respond in Telegram
- **Problem:** commands stay unanswered or Telegram reports token errors.
- **Cause:** wrong `BOT_TOKEN`, network restrictions, or Telegram is blocked.
- **Fix:** verify the token inside `.env`, ensure the host can reach `api.telegram.org`, and restart the bot. Inspect `logs/errors.log` for stack traces.

## Mindee API errors
- **Problem:** OCR fails with Mindee-related messages.
- **Cause:** invalid `MINDEE_API_KEY`, incorrect `Model_id_mindee`, or transient network issues.
- **Fix:** update credentials in `.env`, confirm that the Mindee account is active, and retry once connectivity is restored.

## Docker container exits immediately
- **Problem:** `docker ps` shows the service stopping right after launch.
- **Cause:** missing mandatory environment variables or missing write access to logs/database.
- **Fix:** review `docker logs <container>`, provide `BOT_TOKEN`, `MINDEE_API_KEY`, `Model_id_mindee`, and make sure `logs/` plus `data.sqlite` are writable.

## Logs are empty
- **Problem:** no log files appear, even under load.
- **Cause:** `LOG_DIR` points to a non-existent path or log level is too strict.
- **Fix:** create the directory or remove `LOG_DIR` to fall back to `logs/`. Set `LOG_LEVEL=INFO` to verify the pipeline.

