# 📄 InvoiceFlowBot

[![CI](https://github.com/AmaLS367/InvoiceFlowBot/actions/workflows/ci.yml/badge.svg)](https://github.com/AmaLS367/InvoiceFlowBot/actions/workflows/ci.yml)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)

> 🇬🇧 For English documentation see [README.md](README.md)

Русская документация по проекту InvoiceFlowBot.

## 📋 Описание

InvoiceFlowBot это Telegram бот для обработки инвойсов с помощью OCR.
Бот принимает PDF или изображение, отправляет его в Mindee, извлекает реквизиты счета и сохраняет их в SQLite.
Через интерфейс Telegram можно просматривать счета, редактировать шапку и позиции, добавлять комментарии и выгружать товары в CSV.

## 🚀 Быстрый старт с Docker

> [!TIP]
> Самый быстрый способ запуска! Docker автоматически настроит все зависимости.

```powershell
# 1. Клонируйте и настройте окружение
git clone https://github.com/AmaLS367/InvoiceFlowBot.git
cd InvoiceFlowBot
Copy-Item .env.example .env

# 2. Отредактируйте .env с вашими токенами
notepad .env

# 3. Запустите бота
docker-compose up --build -d

# 4. Просмотр логов
docker-compose logs -f

# 5. Остановка
docker-compose down
```

## 🔧 Требования

- 🐍 Python 3.11+
- 🤖 Токен Telegram бота
- 🔑 Mindee API Key и Model ID
- 💾 Доступ к SQLite (идет в комплекте с Python)

## 💻 Установка и запуск локально

> [!NOTE]
> Требуется Python 3.11+ и Git

<details>
<summary><b>📦 Пошаговая инструкция по установке</b></summary>

### 1. Клонируйте репозиторий

```powershell
git clone https://github.com/AmaLS367/InvoiceFlowBot.git
cd InvoiceFlowBot
```

### 2. Создайте виртуальное окружение

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3. Установите зависимости

```powershell
pip install -e .
```

### 4. Настройте переменные окружения

```powershell
Copy-Item .env.example .env
notepad .env
```

**Пример `.env`:**
```env
BOT_TOKEN=123456:ABCDEF_your_bot_token
MINDEE_API_KEY=your-mindee-api-key
MINDEE_MODEL_ID=mindee/invoices/v4
DB_FILENAME=data.sqlite
```

> [!WARNING]
> Не забудьте заменить значения на свои реальные токены!

### 5. Запустите бота

```powershell
python bot.py
```

> [!TIP]
> Логи по умолчанию пишутся в каталог `logs/` - проверьте их при возникновении проблем.

</details>

## 📚 Документация

<details>
<summary><b>📖 Полное руководство (docs/ru/)</b></summary>

| Раздел | Описание |
|--------|----------|
| 📖 [Обзор](docs/ru/overview.md) | Архитектура и компоненты системы |
| 💻 [Настройка локально](docs/ru/setup-local.md) | Установка без Docker |
| 🐳 [Запуск в Docker](docs/ru/setup-docker.md) | Контейнеризация и развертывание |
| ⚙️ [Конфигурация](docs/ru/config.md) | Переменные окружения |
| 🗄️ [База данных](docs/ru/database.md) | Структура SQLite и миграции |
| 🧪 [Тесты](docs/ru/tests.md) | Запуск тестов и проверки качества |
| 🔧 [Устранение неполадок](docs/ru/troubleshooting.md) | Решение типовых проблем |
| 📸 [Скриншоты](docs/ru/screenshots.md) | Визуальные примеры |

> [!NOTE]
> 🇬🇧 Английская версия документации: [README.md](README.md)

</details>
