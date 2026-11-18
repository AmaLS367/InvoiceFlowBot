<img src="https://capsule-render.vercel.app/api?type=waving&color=gradient&customColorList=12,16,20&height=200&section=header&text=InvoiceFlowBot&fontSize=60&animation=fadeIn&fontAlignY=35&desc=Автоматическая%20обработка%20счетов%20через%20OCR&descAlignY=55&descSize=20"/>

<div align="center">

<p align="center">
  <img src="https://readme-typing-svg.demolab.com?font=Fira+Code&size=22&duration=3000&pause=1000&center=true&vCenter=true&width=600&lines=%D0%90%D0%B2%D1%82%D0%BE%D0%BC%D0%B0%D1%82%D0%B8%D1%87%D0%B5%D1%81%D0%BA%D0%B0%D1%8F+%D0%BE%D0%B1%D1%80%D0%B0%D0%B1%D0%BE%D1%82%D0%BA%D0%B0+%D1%81%D1%87%D0%B5%D1%82%D0%BE%D0%B2;OCR+%7C+Telegram+%7C+SQLite;%D0%97%D0%B0%D0%B3%D1%80%D1%83%D0%B7%D0%BA%D0%B0+%7C+%D0%A0%D0%B5%D0%B4%D0%B0%D0%BA%D1%82%D0%B8%D1%80%D0%BE%D0%B2%D0%B0%D0%BD%D0%B8%D0%B5+%7C+%D0%A1%D0%BE%D1%85%D1%80%D0%B0%D0%BD%D0%B5%D0%BD%D0%B8%D0%B5;Docling+%26+Tesseract+%2B+Python+3.11%2B" alt="Typing SVG" />
</p>

[![CI](https://img.shields.io/github/actions/workflow/status/AmaLS367/InvoiceFlowBot/ci.yml?style=for-the-badge&logo=github&label=CI&color=success)](https://github.com/AmaLS367/InvoiceFlowBot/actions/workflows/ci.yml)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/downloads/)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg?style=for-the-badge)](https://opensource.org/licenses/Apache-2.0)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg?style=for-the-badge)](https://github.com/astral-sh/ruff)
[![Telegram](https://img.shields.io/badge/Telegram-Бот-blue?style=for-the-badge&logo=telegram)](https://telegram.org/)

<p align="center">
  <img src="https://img.shields.io/badge/OCR-Docling%20%2B%20Tesseract-4A90E2?style=for-the-badge" alt="OCR" />
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
Бот принимает PDF или изображение, локально распознаёт реквизиты счёта и сохраняет подтверждённые данные в SQLite.
Через интерфейс Telegram можно просматривать счета, редактировать шапку и позиции, добавлять комментарии и выгружать товары в CSV.

<div align="center">

## 🎯 Как это работает

```mermaid
graph LR
    A[📱 Пользователь] -->|Загружает PDF/Фото| B[🤖 Telegram Бот]
    B -->|Отправляет в OCR| C[🔍 Docling и Tesseract]
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
| 🤖 **OCR Обработка** | Локальное распознавание через Docling и Tesseract | ![](https://img.shields.io/badge/-Готово-success?style=flat-square) |
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
- Tesseract с английским и русским языковыми пакетами для локальной установки. В Docker они уже включены.
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
OCR_PROVIDER=local
OCR_LANGUAGES=eng+rus
```

При `OCR_PROVIDER=local` счета обрабатываются на сервере бота без API-ключа OCR и платы за документ. При первой обработке скачиваются модели Docling. Для Mindee укажите `OCR_PROVIDER=mindee`, `MINDEE_API_KEY` и `MINDEE_MODEL_ID`. Подробности в [руководстве по локальной установке](docs/ru/setup-local.md).

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
