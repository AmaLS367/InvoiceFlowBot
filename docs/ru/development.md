<img src="https://capsule-render.vercel.app/api?type=waving&color=gradient&customColorList=12,16,20&height=120&section=header&text=Разработка&fontSize=40&animation=fadeIn"/>

<div align="center">

[![Alembic](https://img.shields.io/badge/Migrations-Alembic-blue?style=for-the-badge)](https://alembic.sqlalchemy.org/)
[![CI/CD](https://img.shields.io/badge/Pipeline-GitHub%20Actions-green?style=for-the-badge&logo=github)](https://github.com/features/actions)
[![Dev Tools](https://img.shields.io/badge/Tools-Complete-orange?style=for-the-badge)](#миграции-базы-данных)

</div>

## 📋 О руководстве

> [!IMPORTANT]
> Перед началом разработки установите dev-зависимости: `pip install -e .[dev]`

## Переводы интерфейса

Чтобы добавить язык, скопируйте [английский каталог](../../backend/handlers/locales/en.json) в файл с двухбуквенным кодом ISO 639-1, например `fr.json`. Переведите значения и сохраните ключи и параметры подстановки. Добавьте код и название языка в `LANGUAGES` в [`texts.py`](../../backend/handlers/texts.py). Список языков и меню команд Telegram используют этот реестр.

## 🗄️ Миграции базы данных

Схема базы данных управляется через Alembic поверх SQLite.

### Как поднимается схема

Во время запуска схема БД создается или обновляется через вызов `backend.storage.db.init_db()`.
Эта функция внутри выполняет команду:

```powershell
python -m alembic -c backend/alembic.ini upgrade head
```

Любая точка входа, которая использует базу данных, должна один раз вызвать `init_db()` перед работой со стореджем.

### Запуск миграций локально

Чтобы локальная база была в актуальном состоянии, достаточно выполнить:

```powershell
python -m alembic -c backend/alembic.ini upgrade head
```

Миграции применятся к файлу базы, путь к которому задан в `backend.storage.db.DB_PATH`.

### Добавление новой миграции

Если вы меняете структуру таблиц, нужно добавить миграцию.

Рекомендуемый порядок действий:

1. Не править SQL в коде напрямую. Сначала создайте миграцию.

2. Сгенерировать заготовку миграции:

   ```powershell
   python -m alembic revision -m "описание_изменения"
   ```

3. Открыть файл из `backend/alembic/versions/` и вручную описать SQL в функциях `upgrade` и `downgrade` под SQLite.

4. Применить миграцию:

   ```powershell
   python -m alembic -c backend/alembic.ini upgrade head
   ```

Для SQLite автоматическая генерация схемы ограничена, поэтому миграции описываются вручную.

### Миграции и тесты

Тесты, которые используют базу данных, работают с теми же миграциями:

* В тесте можно подменить `backend.storage.db.DB_PATH` на временный файл.

* Вызов `backend.storage.db.init_db()` применит все миграции к этой временной базе.

Так тестовая схема всегда совпадает с боевой.

### Docker и миграции

При запуске бота в Docker миграции должны быть применены до старта процесса приложения.

Типичный паттерн — запускать:

```powershell
python -m alembic -c backend/alembic.ini upgrade head
python bot.py
```

из entrypoint-скрипта.

### CI пайплайн

В GitHub Actions выполняются шаги:

1. Установка dev-зависимостей и пакета в editable-режиме:

   ```powershell
   python -m pip install -e .[dev]
   ```

2. Применение миграций Alembic:

   ```powershell
   python -m alembic -c backend/alembic.ini upgrade head
   ```

3. Запуск статических проверок и тестов:

   ```powershell
   python -m ruff check .
   python -m mypy backend/
   python -m pytest
   ```
