# InvoiceFlowBot

Русская документация по проекту InvoiceFlowBot.

## Описание

InvoiceFlowBot это Telegram бот для обработки инвойсов с помощью OCR.  
Бот принимает PDF или изображение, отправляет его в Mindee, извлекает реквизиты счета и сохраняет их в SQLite.  
Через интерфейс Telegram можно просматривать счета, редактировать шапку и позиции, добавлять комментарии и выгружать товары в CSV.

## Требования

- Python 3.11+
- Токен Telegram бота
- Mindee API Key и Model ID
- Доступ к SQLite (идет в комплекте с Python)

## Установка и запуск локально

1. Клонируйте репозиторий и перейдите в папку проекта:

```powershell
git clone https://github.com/AmaLS367/InvoiceFlowBot.git
cd InvoiceFlowBot
```

2. Создайте виртуальное окружение и активируйте его:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

3. Установите зависимости:

```powershell
pip install -e .
```

4. Создайте файл `.env` в корне проекта и задайте переменные окружения:

```env
BOT_TOKEN=123456:ABCDEF_your_bot_token
MINDEE_API_KEY=your-mindee-api-key
MINDEE_MODEL_ID=mindee/invoices/v4
DB_FILENAME=data.sqlite
```

5. Запустите бота:

```powershell
python bot.py
```

Логи по умолчанию пишутся в каталог `logs/`.

## Документация

Подробная документация находится в каталоге `docs/ru`:

* [Обзор](docs/ru/overview.md)
* [Настройка локальной среды](docs/ru/setup-local.md)
* [Запуск в Docker](docs/ru/setup-docker.md)
* [Конфигурация](docs/ru/config.md)
* [База данных](docs/ru/database.md)
* [Тесты](docs/ru/tests.md)
* [Устранение неполадок](docs/ru/troubleshooting.md)
* [Скриншоты](docs/ru/screenshots.md)

Английская версия README находится в файле `README.md`.

