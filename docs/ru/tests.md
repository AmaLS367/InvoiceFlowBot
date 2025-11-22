# Тесты

Проект использует pytest. Зависимости для тестов вынесены в `requirements-dev.txt`.

## Запуск

```powershell
git clone https://github.com/AmaLS367/InvoiceFlowBot.git
cd InvoiceFlowBot
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
pytest
```

Команда `pytest` автоматически обнаружит тесты в каталоге `tests/`.

## Покрытие

- `test_invoice_parsing.py` — проверка преобразования ответа Mindee в внутреннюю структуру.
- `test_engine_utilities.py` — валидация утилит OCR-движка и логирования.
- `test_storage_dates.py` — конвертация дат, ISO форматы и выборки из БД.
- `test_imports.py` — быстрый smoke-тест импорта ключевых модулей.
- `test_invoice_service.py` — тесты сервисного слоя с замоканными OCR и хранилищем:
  - `process_invoice_file` — проверка интеграции OCR и конвертации в доменную модель
  - `save_invoice` и `list_invoices` — проверка делегирования в слой хранилища

## Инструменты качества кода

В проекте используются автоматические проверки качества кода:

- **ruff** — быстрый линтер Python для проверки стиля кода и распространенных ошибок
- **mypy** — статическая проверка типов для Python

### Запуск проверок качества

```powershell
# Установка зависимостей для разработки
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Запуск линтера
python -m ruff check .

# Запуск проверки типов
python -m mypy domain services ocr storage

# Запуск тестов
python -m pytest
```

Также можно запустить конкретный файл с тестами:

```powershell
python -m pytest tests/test_invoice_service.py
```

CI-пайплайн автоматически запускает `ruff`, `mypy` и `pytest` при каждом push и pull request.

## Политика разработки

- Новые фичи желательно сопровождать тестами, особенно если меняются форматы данных или логика OCR.
- Перед отправкой Pull Request прогоняйте `pytest` локально или в CI.
- Для сложных кейсов Mindee можно добавлять фикстуры с реальными примерами PDF (обезличенными).
- Убедитесь, что код проходит проверки `ruff` и `mypy` перед отправкой pull request.

