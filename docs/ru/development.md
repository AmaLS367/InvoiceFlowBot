<img src="https://capsule-render.vercel.app/api?type=waving&color=gradient&customColorList=12,16,20&height=120&section=header&text=Разработка&fontSize=40&animation=fadeIn"/>

<div align="center">

[![Alembic](https://img.shields.io/badge/Migrations-Alembic-blue?style=for-the-badge)](https://alembic.sqlalchemy.org/)
[![CI/CD](https://img.shields.io/badge/Pipeline-GitHub%20Actions-green?style=for-the-badge&logo=github)](https://github.com/features/actions)
[![Dev Tools](https://img.shields.io/badge/Tools-Complete-orange?style=for-the-badge)](#database-migrations)

</div>

## 📋 О руководстве

> [!IMPORTANT]
> Перед началом разработки установите dev-зависимости: `pip install -e .[dev]`

## Переводы интерфейса

Чтобы добавить язык, скопируйте [английский каталог](../../backend/handlers/locales/en.json) в файл с двухбуквенным кодом ISO 639-1, например `nl.json`. Переведите значения и сохраните ключи и параметры подстановки. Добавьте код и название языка в `LANGUAGES` в [`texts.py`](../../backend/handlers/texts.py). Список языков и меню команд Telegram используют этот реестр.

<a name="database-migrations"></a>

## 🗄️ Миграции базы данных

Схема базы данных управляется через Alembic поверх SQLite.

### Как поднимается схема

Во время запуска схема БД создается или обновляется через вызов `backend.storage.db.init_db()`.
Функция обновляет схему до `head` через Python API Alembic. Эквивалентная команда:

```powershell
python -m alembic -c backend/alembic.ini upgrade head
```

Любая точка входа, которая использует базу данных, должна один раз вызвать `init_db()` перед работой со стореджем.

### Запуск миграций локально

В корне проекта задайте `BOT_TOKEN` в `.env` или окружении, затем выполните:

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
   python -m alembic -c backend/alembic.ini revision -m "описание_изменения"
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

Интеграционные тесты хранилища используют те же ревизии Alembic на временных базах SQLite.

### Docker и миграции

Точка входа Docker применяет миграции перед запуском бота:

```powershell
python -m alembic -c backend/alembic.ini upgrade head
python bot.py
```

## CI

При push в `main` или `master` и PR в эти ветки [CI](../../.github/workflows/ci.yml) использует Python 3.11, устанавливает `.[dev]`, применяет миграции с тестовым токеном и запускает pre-commit и mypy. Затем запускает две группы тестов:

```bash
pytest --import-mode=importlib -m "not storage_db"
pytest --import-mode=importlib -m "storage_db" --no-cov
```

[Coverage](../../.github/workflows/coverage.yml) требует минимум 80% покрытия. [Docker Build](../../.github/workflows/docker.yml) и [Compose](../../.github/workflows/docker-compose.yml) проверяют образ и конфигурацию контейнера. Docker healthcheck проверяет импорты Python. [Docs](../../.github/workflows/docs.yml) проверяет ссылки при изменениях документации. [Security](../../.github/workflows/security.yml) запускает Bandit, pip-audit и Trivy для тех же веток и еженедельно.

[Release](../../.github/workflows/release.yml) публикует Docker-образ в GHCR по тегам `v*` с помощью `GITHUB_TOKEN`. Релиз на GitHub создаётся для тегов вида `vX.0.0`.
