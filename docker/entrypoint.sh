#!/usr/bin/env sh
set -e

# Run Alembic migrations
python -m alembic -c backend/alembic.ini upgrade head

# Start the bot
python bot.py
