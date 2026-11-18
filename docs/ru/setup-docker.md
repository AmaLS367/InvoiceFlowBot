<img src="https://capsule-render.vercel.app/api?type=waving&color=gradient&customColorList=6,11,20&height=120&section=header&text=Docker+Setup&fontSize=40&animation=fadeIn"/>

<div align="center">

[![Docker](https://img.shields.io/badge/Docker-Compose-blue?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com/)
[![Container](https://img.shields.io/badge/Container-Ready-green?style=for-the-badge)](https://hub.docker.com/)
[![Quick Start](https://img.shields.io/badge/Setup-5%20Minutes-orange?style=for-the-badge)](#запуск-контейнера)

</div>

## 📋 О Docker

Docker позволяет развернуть InvoiceFlowBot без локальной установки Python и зависимостей. Compose сохраняет базу, логи и кэш моделей OCR при пересоздании контейнера.

> [!TIP]
> Docker - самый быстрый способ запуска! Все зависимости уже включены в образ.

## ⚙️ Подготовка

Выполняйте команды из корня проекта. Файл базы и каталог `logs/` должны быть доступны пользователю контейнера (`botuser`) на запись. В Linux, если после подготовки путей по инструкции ниже нужно настроить владельца, выполните `docker compose build bot`, затем `docker compose run --rm --no-deps --entrypoint id bot`, чтобы узнать UID и GID для настройки прав.

Если предыдущий запуск создал каталог `data.sqlite`, выполните `docker compose down`, проверьте содержимое каталога и переименуйте его перед продолжением. Существующий файл SQLite сохраните.

<a name="запуск-контейнера"></a>

## 🚀 Запуск контейнера

PowerShell:

```powershell
if (-not (Test-Path -LiteralPath .env)) { Copy-Item .env.example .env }
notepad .env
# Укажите BOT_TOKEN в .env перед продолжением.
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
# Укажите BOT_TOKEN в .env перед продолжением.
if [ ! -e ./data.sqlite ]; then touch ./data.sqlite; fi
test -f ./data.sqlite && mkdir -p ./logs && docker compose up --build -d
```

При запуске контейнер применяет миграции Alembic, затем бот подключается к Telegram через polling. Вывод запуска доступен по команде `docker compose logs -f bot`.

## 🔄 Остановка и обновление

Остановить сервис:
```powershell
docker compose down
```

Получить свежую версию и пересобрать:
```powershell
git pull
docker compose up --build -d
```

## Томы и данные

Файл `docker-compose.yml` монтирует ресурсы:
- `./data.sqlite:/app/data.sqlite` — база счетов. Держите ее в бэкапах.
- `./logs:/app/logs` — логи OCR и ошибок доступны на хосте.

- `ocr-models:/app/data/huggingface` — именованный том кэша Hugging Face, путь задан через `HF_HOME`.

Вложения Telegram скачиваются в `/app/temp/` внутри контейнера. При смене пути к базе обновите `INVOICE_DB_PATH` и монтирование в Compose. Перед обновлением сделайте [резервную копию базы](database.md#резервная-копия-и-восстановление).
