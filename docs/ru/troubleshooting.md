<img src="https://capsule-render.vercel.app/api?type=waving&color=gradient&customColorList=6,11,20&height=120&section=header&text=Решение+проблем&fontSize=35&animation=fadeIn"/>

<div align="center">

<p align="center">
  <img src="https://readme-typing-svg.demolab.com?font=Fira+Code&size=18&duration=3000&pause=1000&center=true&vCenter=true&width=500&lines=%D0%A2%D0%B8%D0%BF%D0%BE%D0%B2%D1%8B%D0%B5+%D0%BE%D1%88%D0%B8%D0%B1%D0%BA%D0%B8;%D0%91%D1%8B%D1%81%D1%82%D1%80%D1%8B%D0%B5+%D1%80%D0%B5%D1%88%D0%B5%D0%BD%D0%B8%D1%8F;%D0%9F%D1%80%D0%BE%D0%B2%D0%B5%D1%80%D0%BA%D0%B0+%D0%BB%D0%BE%D0%B3%D0%BE%D0%B2" alt="Typing SVG" />
</p>

[![Solutions](https://img.shields.io/badge/Solutions-6+-blue?style=for-the-badge)](#-о-руководстве)
[![Quick Fix](https://img.shields.io/badge/Fix-Fast-green?style=for-the-badge)](#-sqlite3operationalerror-unable-to-open-database-file)
[![Logs](https://img.shields.io/badge/Check-Logs-orange?style=for-the-badge)](#логи-не-пишутся)

</div>

## 📋 О руководстве

Сначала проверьте вывод команды, которая завершилась с ошибкой. В Docker выполните `docker compose logs bot`. Предупреждения и исключения приложения по умолчанию пишутся в `logs/errors.log`.

## ❌ sqlite3.OperationalError: unable to open database file

Убедитесь, что `./data.sqlite` на хосте является обычным файлом и доступен контейнеру на запись. Если Docker создал каталог с этим именем, остановите сервис через `docker compose down`, проверьте содержимое каталога и переименуйте его. Затем создайте отсутствующий файл по [руководству Docker](setup-docker.md#запуск-контейнера). Существующий файл базы сохраните.

## Бот не отвечает в Telegram

Проверьте `BOT_TOKEN` и доступ к `api.telegram.org`. После изменения окружения перезапустите локальный процесс. После изменения `.env` для Docker выполните `docker compose up -d --force-recreate bot`.

## Ошибки локального распознавания

Проверьте, что `tesseract --list-langs` показывает языки из `OCR_LANGUAGES` (по умолчанию `eng+rus`). При первом распознавании нужен доступ к Hugging Face, если модели Docling ещё не загружены.

## Ошибки Mindee API

При `OCR_PROVIDER=mindee` проверьте `MINDEE_API_KEY`, `MINDEE_MODEL_ID` и доступ к Mindee. Предупреждения провайдера и записанные исключения доступны в `logs/errors.log`.

## Ошибки обработки файлов

Попробуйте загрузить корректный PDF, JPEG, PNG или WebP. Перед загрузкой преобразуйте HEIC/HEIF в JPEG или PNG. Если преобразование изображения внутри бота завершилось ошибкой, исключение будет в `logs/errors.log`.

## Ошибки сервиса распознавания

Сообщение «Сервис распознавания сейчас недоступен» может появиться с любым провайдером. Проверьте `OCR_PROVIDER` и выполните соответствующие проверки выше. Подробности ошибки провайдера или обработчика загрузки ищите в `logs/errors.log`.

## Docker контейнер мгновенно завершается

Выполните `docker compose logs bot`, проверьте `BOT_TOKEN` и права записи пользователя контейнера в файл базы и каталог логов. Ошибки Alembic и конфигурации могут появляться в выводе контейнера при старте.

## Логи не пишутся

Проверьте уровень логирования и используемый каталог. Приложение создаёт каталог при наличии прав. Если `LOG_DIR` относительный, ищите каталог от текущей рабочей директории. Чтобы продублировать логи приложения в stderr, задайте `LOG_CONSOLE=1` и перезапустите процесс или пересоздайте контейнер.
