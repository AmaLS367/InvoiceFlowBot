# Конфигурация проекта

Конфигурация приложения управляется через модель `Settings` из `config.py` на базе pydantic.

Все значения настроек загружаются из переменных окружения и необязательного файла `.env` в корне проекта.

## Модель Settings

Модель `config.Settings` читает следующие ключи:

- `BOT_TOKEN`  
  Токен Telegram бота. Обязательный параметр.

- `MINDEE_API_KEY`  
  API ключ Mindee для OCR. Обязательный параметр.

- `MINDEE_MODEL_ID`  
  Идентификатор модели Mindee. Обязательный параметр.

- `DB_FILENAME` (или `INVOICE_DB_PATH`)  
  Имя файла базы данных SQLite. По умолчанию `data.sqlite`.

- `DB_DIR`  
  Каталог для файла базы данных. По умолчанию каталог, где находится `config.py` (корень проекта).

- `UPLOAD_FOLDER`  
  Каталог для загруженных файлов. По умолчанию `data/uploads`.

- `ARTIFACTS_DIR`  
  Каталог для артефактов OCR. По умолчанию `data/artifacts`.

- `LOG_LEVEL`  
  Уровень логирования (DEBUG, INFO, WARNING, ERROR). По умолчанию `INFO`.

- `LOG_ROTATE_MB`  
  Максимальный размер файла лога в МБ перед ротацией. По умолчанию `10`.

- `LOG_BACKUPS`  
  Количество резервных копий логов. По умолчанию `5`.

- `LOG_CONSOLE`  
  Включить вывод в консоль (0 или 1). По умолчанию `0`.

- `LOG_DIR`  
  Пользовательский каталог для логов. Необязательный параметр.

Экземпляр настроек создается один раз через `get_settings()` с кешированием, а модуль `config` экспортирует удобные константы вроде `BOT_TOKEN`, `MINDEE_API_KEY` и `DB_PATH`.

## Переменные окружения и файл .env

В `Settings` включена конфигурация:

```python
model_config = SettingsConfigDict(
    env_file=".env",
    env_file_encoding="utf-8",
    extra="ignore",
)
```

Это означает:

* Настройки можно передавать как реальные переменные окружения.
* В локальной разработке удобно использовать `.env` в корне проекта.

Пример файла `.env`:

```env
BOT_TOKEN=123456:ABCDEF_your_bot_token
MINDEE_API_KEY=your-mindee-api-key
MINDEE_MODEL_ID=mindee/invoices/v4

# Необязательная конфигурация базы данных
INVOICE_DB_PATH=data.sqlite
# DB_DIR=D:\invoiceflowbot\data

# Необязательная конфигурация логирования
LOG_LEVEL=INFO
LOG_ROTATE_MB=10
LOG_BACKUPS=5
LOG_CONSOLE=0
LOG_DIR=logs
```

## Использование конфига в коде

Базовые варианты использования:

* Точка входа Telegram бота:

  ```python
  from config import BOT_TOKEN

  bot = Bot(token=BOT_TOKEN)
  ```

* Клиент Mindee:

  ```python
  import config

  MINDEE_API_KEY = config.MINDEE_API_KEY
  ```

* Путь к базе данных:

  ```python
  import config

  DB_PATH = config.DB_PATH
  ```

В прикладном коде не следует вызывать `os.getenv` напрямую. Вместо этого все настройки нужно получать через модуль `config`. Это упрощает тестирование и удерживает конфигурацию в одном месте.

