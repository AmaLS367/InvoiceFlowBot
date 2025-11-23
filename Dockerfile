# Builder stage: install dependencies
FROM python:3.11-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install system dependencies needed for building Python packages
RUN set -eux; \
    apt-get update; \
    apt-get install -y --no-install-recommends gcc libc-dev; \
    rm -rf /var/lib/apt/lists/*

# Copy dependency files first (for better layer caching)
COPY pyproject.toml ./
COPY README.md ./

# Upgrade pip
RUN python -m pip install --upgrade pip

# Copy application code needed for installation
COPY core/ ./core/
COPY domain/ ./domain/
COPY services/ ./services/
COPY ocr/ ./ocr/
COPY storage/ ./storage/
COPY handlers/ ./handlers/
COPY alembic/ ./alembic/
COPY alembic.ini ./
COPY config.py ./
COPY bot.py ./

# Install dependencies and application
RUN python -m pip install --no-cache-dir -e .

# Runtime stage: minimal runtime image
FROM python:3.11-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Create non-root user
RUN useradd -m botuser

WORKDIR /app

# Copy installed Python packages from builder
COPY --from=builder /usr/local/lib/python3.11 /usr/local/lib/python3.11
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code (only what's needed, .dockerignore excludes tests/docs)
COPY . /app

# Create data directory for SQLite database
RUN mkdir -p /app/data

# Copy entrypoint script
COPY docker/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Change ownership of /app to botuser
RUN chown -R botuser:botuser /app

# Switch to non-root user
USER botuser

# Set default database filename
ENV DB_FILENAME=data.sqlite

# Healthcheck: verify environment is healthy
HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
    CMD python healthcheck.py || exit 1

# Entrypoint runs migrations and starts the bot
ENTRYPOINT ["/entrypoint.sh"]
