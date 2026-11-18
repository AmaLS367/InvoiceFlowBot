<img src="https://capsule-render.vercel.app/api?type=waving&color=gradient&customColorList=12,16,20&height=120&section=header&text=Тестирование&fontSize=40&animation=fadeIn"/>

<div align="center">

[![pytest](https://img.shields.io/badge/Framework-pytest-blue?style=for-the-badge&logo=pytest)](https://pytest.org/)
[![Coverage](https://img.shields.io/badge/Coverage-80%25+-green?style=for-the-badge)](https://coverage.readthedocs.io/)

</div>

## 📋 О тестировании

Проект использует pytest. Зависимости для тестов определены в `pyproject.toml` в секции `[project.optional-dependencies]`.

> [!NOTE]
> Для разработки установите dev-зависимости: `pip install -e .[dev]`

## 🚀 Запуск

```powershell
git clone https://github.com/AmaLS367/InvoiceFlowBot.git
cd InvoiceFlowBot
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e .[dev]
$env:BOT_TOKEN = 'test-token'
pytest
```

Команда `pytest` автоматически обнаружит тесты в каталоге `tests/`. В Bash выполните `BOT_TOKEN=test-token python -m pytest`. Тот же тестовый токен подходит для запуска отдельного файла или обёртки.

## Покрытие

Проверка покрытия в CI требует минимум **80%**. В тестах представлены следующие области:

### Основные тестовые файлы

- `tests/test_invoice_parsing.py` — проверка преобразования ответа Mindee в внутреннюю структуру, форматирование и утилиты
- `tests/test_engine_utilities.py` — валидация утилит OCR-движка и логирования
- `tests/test_storage_dates.py` — конвертация дат, ISO форматы и выборки из БД
- `tests/test_imports.py` — быстрый smoke-тест импорта ключевых модулей
- `tests/test_invoice_service.py` — тесты сервисного слоя с замоканными OCR и хранилищем:
  - `process_invoice_file` — проверка интеграции OCR и конвертации в доменную модель
  - `save_invoice` и `list_invoices` — проверка делегирования в слой хранилища

### Тесты обработчиков

- `tests/handlers/test_callbacks_edit.py` — тесты редактирования счетов через callback-кнопки
- `tests/handlers/test_callbacks_misc.py` — тесты вспомогательных callback-обработчиков
- `tests/handlers/test_commands_basic.py` — тесты базовых команд бота
- `tests/handlers/test_commands_drafts.py` — тесты работы с черновиками
- `tests/handlers/test_commands_invoices_force_reply.py` — тесты запросов по счетам
- `tests/handlers/test_languages.py` — локализация меню, сохранение выбора и согласованность переводов
- `tests/handlers/test_file_upload_*.py` — тесты загрузки файлов

### Тесты OCR

- `tests/ocr/test_extract.py` — тесты извлечения данных из документов
- `tests/ocr/test_async_client.py` — тесты асинхронного OCR-клиента
- `tests/ocr/test_router.py` — тесты роутера OCR
- `tests/ocr/test_local_provider.py` — локальное распознавание, разбор таблиц и отметки для проверки

### Тесты хранилища

- `tests/storage/test_mappers.py` — тесты маппинга между доменом и БД
- `tests/storage/test_storage_invoices_crud.py` — интеграционные тесты CRUD операций
- `tests/storage/test_storage_migrations.py` — тесты миграций БД

### Тесты домена

- `tests/domain/test_invoice*.py` — тесты доменных моделей (Invoice, InvoiceHeader, InvoiceItem и др.)

### Интеграционные тесты

- `tests/integration/test_flow_ocr_draft_save.py` — полный flow обработки счета от OCR до сохранения

## Инструменты качества кода

В проекте используются автоматические проверки качества кода:

- **ruff** — быстрый линтер Python для проверки стиля кода и распространенных ошибок
- **mypy** — статическая проверка типов для Python

### Запуск проверок качества

```powershell
# Установка зависимостей для разработки
pip install -e .[dev]

# Запуск линтера
python -m ruff check .

# Запуск проверки типов
python -m mypy backend/

# Запуск тестов
$env:BOT_TOKEN = 'test-token'
python -m pytest
```

Также можно запустить конкретный файл с тестами:

```powershell
python -m pytest tests/test_invoice_service.py
```

CI запускает pre-commit, mypy и pytest при push в `main` или `master` и PR в эти ветки. См. [руководство разработчика](development.md#ci).

## Политика разработки

- Новые фичи желательно сопровождать тестами, особенно если меняются форматы данных или логика OCR.
- Перед отправкой Pull Request прогоняйте `pytest` локально или в CI.
- Для сложных кейсов Mindee можно добавлять фикстуры с реальными примерами PDF (обезличенными).
- Убедитесь, что код проходит проверки `ruff` и `mypy` перед отправкой pull request.
