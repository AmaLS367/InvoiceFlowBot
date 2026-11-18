<img src="https://capsule-render.vercel.app/api?type=waving&color=gradient&customColorList=6,11,20&height=120&section=header&text=Docker+Setup&fontSize=40&animation=fadeIn"/>

<div align="center">

[![Docker](https://img.shields.io/badge/Docker-Compose-blue?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com/)
[![Container](https://img.shields.io/badge/Container-Ready-green?style=for-the-badge)](https://hub.docker.com/)
[![Quick Start](https://img.shields.io/badge/Setup-5%20Minutes-orange?style=for-the-badge)](#start-the-stack)

</div>

## 📋 About Docker

The container provides Python, Tesseract and the application dependencies. Compose keeps the database, logs and OCR model cache across container replacements.

> [!TIP]
> Docker is the fastest way to get started! All dependencies included.

## ⚙️ Preparation

Run these commands from the project root. The database file and `logs/` must be writable by the container user (`botuser`). On Linux, if you need to adjust ownership after preparing the host paths below, run `docker compose build bot` followed by `docker compose run --rm --no-deps --entrypoint id bot` to find the UID and GID that need write access.

If a previous launch created a directory named `data.sqlite`, run `docker compose down`, check its contents, and rename the directory before continuing. Keep any existing SQLite file.

<a name="start-the-stack"></a>

## 🚀 Start the stack

PowerShell:

```powershell
if (-not (Test-Path -LiteralPath .env)) { Copy-Item .env.example .env }
notepad .env
# Set BOT_TOKEN in .env before continuing.
if (-not (Test-Path -LiteralPath ./data.sqlite)) {
    New-Item -Path ./data.sqlite -ItemType File | Out-Null
}
if (-not (Test-Path -LiteralPath ./data.sqlite -PathType Leaf)) {
    throw 'data.sqlite must be a file'
}
New-Item -Path ./logs -ItemType Directory -Force | Out-Null
docker compose up --build -d
```

Bash:

```bash
if [ ! -e .env ]; then cp .env.example .env; fi
# Set BOT_TOKEN in .env before continuing.
if [ ! -e ./data.sqlite ]; then touch ./data.sqlite; fi
test -f ./data.sqlite && mkdir -p ./logs && docker compose up --build -d
```

The entrypoint applies Alembic migrations before starting Telegram polling. Follow startup with `docker compose logs -f bot`.

## 🔄 Stop and upgrade

Stop the bot:
```powershell
docker compose down
```

Pull the latest code and rebuild:
```powershell
git pull
docker compose up --build -d
```

## Volumes

`docker-compose.yml` mounts:
- `./data.sqlite:/app/data.sqlite` — SQLite database persisted on the host.
- `./logs:/app/logs` — OCR and error logs accessible outside the container.

- `ocr-models:/app/data/huggingface` — named volume for the Hugging Face cache configured by `HF_HOME`.

Telegram attachments are downloaded to `/app/temp/`, inside the container. To change the database location, update both `INVOICE_DB_PATH` and the Compose mount. See the [database backup procedure](database.md#backup-and-restore) before upgrading.
