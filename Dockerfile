FROM python:3.11-slim-buster

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN set -eux; \
    sed -i 's/deb.debian.org/archive.debian.org/g' /etc/apt/sources.list; \
    sed -i 's|security.debian.org|archive.debian.org|g' /etc/apt/sources.list; \
    printf "Acquire::Check-Valid-Until \"false\";\n" > /etc/apt/apt.conf.d/99no-check-valid; \
    apt-get update; \
    apt-get install -y --no-install-recommends gcc libc-dev; \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN mkdir -p logs

COPY . .

CMD ["python", "bot.py"]

