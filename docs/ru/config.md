<img src="https://capsule-render.vercel.app/api?type=waving&color=gradient&customColorList=12,16,20&height=120&section=header&text=Конфигурация&fontSize=40&animation=fadeIn"/>

<div align="center">

[![dotenv](https://img.shields.io/badge/.env-Configuration-blue?style=for-the-badge)](https://github.com/theskumar/python-dotenv)
[![pydantic](https://img.shields.io/badge/Pydantic-Settings-green?style=for-the-badge&logo=pydantic)](https://docs.pydantic.dev/)
[![Variables](https://img.shields.io/badge/Env%20Vars-11-orange?style=for-the-badge)](#-обязательные-параметры)

</div>

## 📋 О конфигурации

Pydantic Settings читает окружение процесса и файл `.env` из текущего каталога. Переменные окружения имеют приоритет. Локальные команды запускайте из корня проекта.

> [!IMPORTANT]
> Без обязательных параметров бот не запустится!

## 🔑 Обязательные параметры

| Переменная | Назначение | Допустимые значения | Значение по умолчанию |
| --- | --- | --- | --- |
| `BOT_TOKEN` | Токен Telegram бота, используемый Aiogram для подключения | Строка из @BotFather | отсутствует, без значения бот не стартует |

Эти переменные обязательны. Если они не заданы, приложение завершит работу при запуске с понятной ошибкой.

## Опциональные параметры

| Переменная | Назначение | Допустимые значения | Значение по умолчанию |
| --- | --- | --- | --- |
| `OCR_PROVIDER` | Провайдер распознавания | `local`, `mindee` | `local` |
| `OCR_LANGUAGES` | Коды установленных языков Tesseract через `+` | Например, `eng+rus` | `eng+rus` |
| `MINDEE_API_KEY` | Ключ API при `OCR_PROVIDER=mindee` | Ключ Mindee | пусто |
| `MINDEE_MODEL_ID` | Модель при `OCR_PROVIDER=mindee` | Например, `mindee/invoices/v4` или UUID | пусто |
| `INVOICE_DB_PATH` | Путь к файлу SQLite с данными | Абсолютный путь или путь относительно `backend/` | `../data.sqlite` |
| `LOG_LEVEL` | Уровень логирования (используется при настройке корневого логгера) | `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL` | `INFO` |
| `LOG_ROTATE_MB` | Размер файла лога до ротации | Целое число мегабайт | `10` |
| `LOG_BACKUPS` | Количество ротационных копий логов | Целое число | `5` |
| `LOG_CONSOLE` | Дублировать логи приложения в stderr | Включается значениями `1`, `true`, `True` | `0` |
| `LOG_DIR` | Пользовательский путь к каталогу логов | Строка с абсолютным или относительным путем | `logs` в корне проекта |

`ARTIFACTS_DIR` по умолчанию равен `data/artifacts` и применяется синхронным OCR. Обработчик вложений Telegram всегда сохраняет их в `temp/` относительно текущего каталога. Переменная `UPLOAD_FOLDER` объявлена в настройках и пока нигде не используется.

При локальном OCR в Compose `HF_HOME` указывает на том кэша моделей в `/app/data/huggingface`. После загрузки моделей можно задать `HF_HUB_OFFLINE=1` в окружении процесса или в `.env` для Compose.

Если `LOG_DIR` не задан, `backend.ocr.engine.util` создаст каталог `logs/` рядом с исходниками и развернет обработчики `ocr_engine.log`, `errors.log`, `router.log`, `extract.log`.

## Работа с `.env`

- Держите `.env` вне системы контроля версий. Файл `.env.example` служит шаблоном и не содержит секретов.
- После изменения `.env` перезапустите локальный процесс. Для Docker пересоздайте сервис командой `docker compose up -d --force-recreate bot`.
- Для разных окружений (dev, staging, prod) используйте отдельные файлы `.env` с нужными токенами и путями к базе.
