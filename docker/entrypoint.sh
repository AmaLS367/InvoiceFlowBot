#!/usr/bin/env sh
set -e

# Run Alembic migrations
python -m alembic upgrade head

# Start the bot
python bot.py
