<img src="https://capsule-render.vercel.app/api?type=waving&color=gradient&customColorList=12,16,20&height=120&section=header&text=Логирование&fontSize=40&animation=fadeIn"/>

<div align="center">

[![Rotating](https://img.shields.io/badge/Handler-Rotating-blue?style=for-the-badge)](https://docs.python.org/3/library/logging.handlers.html)
[![Files](https://img.shields.io/badge/Log%20Files-4-green?style=for-the-badge)](#-файлы-логов)
[![Levels](https://img.shields.io/badge/Levels-Configurable-orange?style=for-the-badge)](#управление-поведением)

</div>

## 📋 О логировании

Модуль `backend.ocr.engine.util` настраивает ротационные логеры при первом запросе к `get_logger`. По умолчанию файлы создаются в каталоге `logs/` в корне проекта или по пути, указанному в `LOG_DIR`.

> [!TIP]
> При сбоях запуска проверьте вывод процесса или `docker compose logs bot`. Для ошибок приложения начните с `errors.log`.

## 📁 Файлы логов

- `ocr_engine.log` — общий поток сообщений приложения, включая шаги OCR и обработку файлов.
- `errors.log` — предупреждения и ошибки уровня `WARNING` и выше.
- `router.log` — сообщения логгера `ocr.router` при вызове синхронного OCR.
- `extract.log` — сообщения синхронной обёртки `backend.ocr.extract`.

Асинхронная обработка вложений Telegram пишет сообщения приложения в `ocr_engine.log`, а предупреждения и ошибки — в `errors.log`.

## Управление поведением

| Переменная | Что меняет |
| --- | --- |
| `LOG_LEVEL` | Основной уровень логирования (например `DEBUG` для диагностики) |
| `LOG_ROTATE_MB` | Максимальный размер отдельных файлов до ротации |
| `LOG_BACKUPS` | Сколько архивных файлов хранить |
| `LOG_CONSOLE` | Дублировать логи приложения в stderr |
| `LOG_DIR` | Выбрать каталог логов. Приложение создаёт его при наличии прав. |

Все обработчики используют `RotatingFileHandler`, поэтому при достижении лимита создаются резервные копии `*.log.1`, `*.log.2` и т.д.

## Рекомендации

- Включайте `LOG_LEVEL=DEBUG` только на тестовых средах — в продакшене это быстро раздувает файлы и может содержать чувствительные данные.
- При отладке контейнера используйте `docker compose logs -f bot` вместе с `LOG_CONSOLE=1`, чтобы видеть потоковые сообщения в реальном времени.
- Следите, чтобы каталог для логов был доступен на запись. При ошибках прав бот не сможет стартовать.
