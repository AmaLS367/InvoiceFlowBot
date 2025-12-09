<img src="https://capsule-render.vercel.app/api?type=waving&color=gradient&customColorList=12,16,20&height=200&section=header&text=InvoiceFlowBot&fontSize=60&animation=fadeIn&fontAlignY=35&desc=Автоматическая%20обработка%20счетов%20через%20OCR&descAlignY=55&descSize=20"/>

<div align="center">

<p align="center">
  <img src="https://readme-typing-svg.demolab.com?font=Fira+Code&size=22&duration=3000&pause=1000&center=true&vCenter=true&width=600&lines=Автоматическая+обработка+счетов;OCR+%7C+Telegram+бот+%7C+SQLite;Загрузка+%7C+Редактирование+%7C+Сохранение;Mindee+API+%2B+Python+3.11%2B" alt="Typing SVG" />
</p>

[![CI](https://img.shields.io/github/actions/workflow/status/AmaLS367/InvoiceFlowBot/ci.yml?style=for-the-badge&logo=github&label=CI&color=success)](https://github.com/AmaLS367/InvoiceFlowBot/actions/workflows/ci.yml)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/downloads/)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg?style=for-the-badge)](https://opensource.org/licenses/Apache-2.0)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg?style=for-the-badge)](https://github.com/astral-sh/ruff)
[![Telegram](https://img.shields.io/badge/Telegram-Бот-blue?style=for-the-badge&logo=telegram)](https://telegram.org/)

<p align="center">
  <img src="https://img.shields.io/badge/OCR-Mindee-4A90E2?style=for-the-badge&logo=data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjQiIGhlaWdodD0iMjQiIHZpZXdCb3g9IjAgMCAyNCAyNCIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHBhdGggZD0iTTEyIDJMMiA3TDEyIDEyTDIyIDdMMTIgMloiIGZpbGw9IndoaXRlIi8+CjxwYXRoIGQ9Ik0yIDEzTDEyIDE4TDIyIDEzIiBzdHJva2U9IndoaXRlIiBzdHJva2Utd2lkdGg9IjIiLz4KPC9zdmc+" alt="OCR" />
  <img src="https://img.shields.io/badge/БД-SQLite-003B57?style=for-the-badge&logo=sqlite&logoColor=white" alt="SQLite" />
  <img src="https://img.shields.io/badge/Фреймворк-Aiogram_3-2CA5E0?style=for-the-badge&logo=telegram&logoColor=white" alt="Aiogram" />
</p>

---

> 🇬🇧 **English documentation:** [README.md](README.md)

</div>

<br/>

Русская документация по проекту InvoiceFlowBot.

## 📋 Описание

InvoiceFlowBot это Telegram бот для обработки инвойсов с помощью OCR.
Бот принимает PDF или изображение, отправляет его в Mindee, извлекает реквизиты счета и сохраняет их в SQLite.
Через интерфейс Telegram можно просматривать счета, редактировать шапку и позиции, добавлять комментарии и выгружать товары в CSV.

<div align="center">

## 🎯 Как это работает

```mermaid
graph LR
    A[📱 Пользователь] -->|Загружает PDF/Фото| B[🤖 Telegram Бот]
    B -->|Отправляет в OCR| C[🔍 Mindee API]
    C -->|Извлекает данные| D[✏️ Черновик]
    D -->|Редактирование| E[💾 SQLite]
    E -->|Запросы| F[📊 Отчёты]

    style A fill:#4A90E2,stroke:#2c3e50,stroke-width:2px,color:#fff
    style B fill:#50C878,stroke:#2c3e50,stroke-width:2px,color:#fff
    style C fill:#FF6B6B,stroke:#2c3e50,stroke-width:2px,color:#fff
    style D fill:#FFD93D,stroke:#2c3e50,stroke-width:2px,color:#333
    style E fill:#A8E6CF,stroke:#2c3e50,stroke-width:2px,color:#333
    style F fill:#B19CD9,stroke:#2c3e50,stroke-width:2px,color:#fff
```

<table>
<tr>
<td width="33%" align="center">
<img src="https://img.icons8.com/fluency/96/000000/upload-to-cloud.png" width="64"/>
<br/>
<b>📤 Загрузка</b>
<br/>
<sub>Отправьте счёт через Telegram</sub>
</td>
<td width="33%" align="center">
<img src="https://img.icons8.com/fluency/96/000000/artificial-intelligence.png" width="64"/>
<br/>
<b>🔍 Обработка</b>
<br/>
<sub>OCR извлекает данные автоматически</sub>
</td>
<td width="33%" align="center">
<img src="https://img.icons8.com/fluency/96/000000/database.png" width="64"/>
<br/>
<b>💾 Сохранение</b>
<br/>
<sub>Хранение в базе SQLite</sub>
</td>
</tr>
</table>

</div>

<br/>

## ✨ Возможности

| Функция | Описание | Статус |
|---------|----------|--------|
| 🤖 **OCR Обработка** | Автоматическое извлечение через Mindee API | ![](https://img.shields.io/badge/-Готово-success?style=flat-square) |
| 📎 **Множество форматов** | PDF, JPEG, PNG, HEIC, HEIF, WebP | ![](https://img.shields.io/badge/-Готово-success?style=flat-square) |
| ✏️ **Интерактивное редактирование** | Правка через интерфейс Telegram | ![](https://img.shields.io/badge/-Готово-success?style=flat-square) |
| 💾 **Хранение данных** | SQLite с миграциями Alembic | ![](https://img.shields.io/badge/-Готово-success?style=flat-square) |
| 📅 **Запросы по периоду** | Фильтрация по датам и поставщику | ![](https://img.shields.io/badge/-Готово-success?style=flat-square) |
| 💬 **Система комментариев** | Добавление заметок к счетам | ![](https://img.shields.io/badge/-Готово-success?style=flat-square) |
| 📊 **Экспорт CSV** | Выгрузка позиций для анализа | ![](https://img.shields.io/badge/-Готово-success?style=flat-square) |

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

---

<div align="center">

### 🌟 История звёзд

[![Star History Chart](https://api.star-history.com/svg?repos=AmaLS367/InvoiceFlowBot&type=Date)](https://star-history.com/#AmaLS367/InvoiceFlowBot&Date)

<img src="https://capsule-render.vercel.app/api?type=waving&color=gradient&height=100&section=footer"/>

**Сделано с ❤️ от [Ama](https://github.com/AmaLS367)**

</div>
