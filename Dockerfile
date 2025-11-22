FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install system dependencies if needed
RUN set -eux; \
    apt-get update; \
    apt-get install -y --no-install-recommends gcc libc-dev; \
    rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy application code
COPY . /app

# Install application in editable mode
RUN pip install --no-cache-dir -e .

# Create data directory for SQLite database
RUN mkdir -p /app/data

# Create non-root user
RUN useradd -m botuser

# Change ownership of /app to botuser
RUN chown -R botuser:botuser /app

# Copy entrypoint script
COPY docker/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Switch to non-root user
USER botuser

# Set default database filename
ENV DB_FILENAME=data.sqlite

ENTRYPOINT ["/entrypoint.sh"]
