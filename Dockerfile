FROM python:3.11-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN set -eux; \
    apt-get update; \
    apt-get install -y --no-install-recommends gcc libc-dev; \
    rm -rf /var/lib/apt/lists/*

COPY pyproject.toml ./
COPY README.md ./

RUN python -m pip install --no-cache-dir --upgrade pip "setuptools>=84.1.0" "wheel>=0.46.2"

COPY backend/core/ ./backend/core/
COPY backend/domain/ ./backend/domain/
COPY backend/services/ ./backend/services/
COPY backend/ocr/ ./backend/ocr/
COPY backend/storage/ ./backend/storage/
COPY backend/handlers/ ./backend/handlers/
COPY backend/alembic/ ./backend/alembic/
COPY backend/alembic.ini ./backend/
COPY backend/config.py ./backend/
COPY bot.py ./

RUN python -m pip install --no-cache-dir --upgrade -e .

# Runtime stage: minimal runtime image
FROM python:3.11-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Apply OS security updates and remove base site-packages/ensurepip to avoid stale dist-info metadata
RUN set -eux; \
    apt-get update; \
    apt-get upgrade -y; \
    rm -rf /var/lib/apt/lists/*; \
    rm -rf /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/ensurepip

# Create non-root user
RUN useradd -m botuser

WORKDIR /app

# Copy installed Python packages from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

COPY . /app

# Create data directory for SQLite database
RUN mkdir -p /app/data

COPY docker/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

RUN chown -R botuser:botuser /app

USER botuser

ENV INVOICE_DB_PATH=../data.sqlite

HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
    CMD python backend/healthcheck.py || exit 1

ENTRYPOINT ["/entrypoint.sh"]
