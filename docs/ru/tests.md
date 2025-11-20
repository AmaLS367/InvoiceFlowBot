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

## Политика разработки

- Новые фичи желательно сопровождать тестами, особенно если меняются форматы данных или логика OCR.
- Перед отправкой Pull Request прогоняйте `pytest` локально или в CI.
- Для сложных кейсов Mindee можно добавлять фикстуры с реальными примерами PDF (обезличенными).

