<img src="https://capsule-render.vercel.app/api?type=waving&color=gradient&customColorList=6,11,20&height=120&section=header&text=База+данных&fontSize=40&animation=fadeIn"/>

<div align="center">

[![SQLite](https://img.shields.io/badge/Database-SQLite-blue?style=for-the-badge&logo=sqlite&logoColor=white)](https://www.sqlite.org/)
[![Alembic](https://img.shields.io/badge/Migrations-Alembic-green?style=for-the-badge)](https://alembic.sqlalchemy.org/)

</div>


## О SQLite

Значение `INVOICE_DB_PATH` по умолчанию — `../data.sqlite`. Относительный путь разрешается от каталога `backend/`. Локально это файл `data.sqlite` в корне проекта, а в Docker — `/app/data.sqlite`. Новая база использует стандартный режим журнала отката SQLite (`delete`).

## Структура

- `invoices` хранит подтверждённые счета, включая поставщика, клиента, номер, дату, итог и путь к исходному файлу.
- `invoice_items` хранит позиции, связанные со счетами.
- `comments` хранит пользовательские комментарии и результаты автоматической проверки сумм.
- `invoice_drafts` хранит один активный черновик на пользователя Telegram.
- `user_languages` хранит выбранный язык интерфейса для каждого пользователя Telegram.

## Миграции

Бот применяет миграции Alembic при старте. Для ручного запуска задайте `BOT_TOKEN` в `.env` или окружении процесса и выполните из корня проекта:

```bash
python -m alembic -c backend/alembic.ini upgrade head
```

Также можно воспользоваться `python scripts/python/migrate.py` или `bash scripts/linux/migrate.sh`. Для отката на одну ревизию остановите бота, сделайте резервную копию и выполните `python scripts/python/migrate.py downgrade -1`. При следующем запуске бот снова применит ожидающие миграции. Alembic применяет миграции к файлу базы приложения. Создание новых миграций описано в [руководстве разработчика](development.md#добавление-новой-миграции).

## Резервная копия и восстановление

Перед копированием файла SQLite остановите бота. Для Docker выполните `docker compose down` и скопируйте базу на хосте. Пример PowerShell для стандартного пути:

```powershell
New-Item -ItemType Directory -Force ./backup | Out-Null
Copy-Item ./data.sqlite "./backup/data-$(Get-Date -Format yyyyMMddHHmmss).sqlite"
```

При нестандартном пути копируйте фактический файл базы. Для восстановления или переноса остановите бота, сохраните копию существующей базы на целевом хосте и поместите бэкап по настроенному пути. При запуске бот применит оставшиеся миграции.
