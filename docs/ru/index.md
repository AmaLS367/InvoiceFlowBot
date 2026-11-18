<img src="https://capsule-render.vercel.app/api?type=waving&color=gradient&customColorList=6,11,20&height=150&section=header&text=Документация&fontSize=50&animation=fadeIn&fontAlignY=38&desc=InvoiceFlowBot%20•%20Полное%20руководство&descAlignY=60&descSize=18"/>

<div align="center">

<p align="center">
  <img src="https://readme-typing-svg.demolab.com?font=Fira+Code&size=18&duration=3000&pause=1000&center=true&vCenter=true&width=500&lines=%D0%90%D0%B2%D1%82%D0%BE%D0%BC%D0%B0%D1%82%D0%B8%D0%B7%D0%B0%D1%86%D0%B8%D1%8F+%D0%BE%D0%B1%D1%80%D0%B0%D0%B1%D0%BE%D1%82%D0%BA%D0%B8+%D1%81%D1%87%D0%B5%D1%82%D0%BE%D0%B2;Telegram+%2B+OCR+%2B+SQLite;%D0%9F%D0%BE%D0%BB%D0%BD%D0%B0%D1%8F+%D0%B4%D0%BE%D0%BA%D1%83%D0%BC%D0%B5%D0%BD%D1%82%D0%B0%D1%86%D0%B8%D1%8F+%D0%BF%D1%80%D0%BE%D0%B5%D0%BA%D1%82%D0%B0" alt="Typing SVG" />
</p>

</div>

## 📋 О проекте

InvoiceFlowBot помогает финансовым и операционным командам автоматизировать обработку входящих счетов. Пользователь отправляет PDF или фотографию счета в Telegram, бот извлекает структуру документа локально с помощью Docling и Tesseract, предлагает отредактировать данные и сохраняет подтвержденный результат в локальную базу SQLite.

> [!NOTE]
> Такая схема снижает ручной труд и ускоряет приемку счетов: бухгалтер видит подготовленный черновик, редактирует поля и позиции, добавляет комментарии и одним нажатием отправляет запись в хранилище.

## 📚 Разделы руководства

<div align="center">

### 🚀 Быстрый старт

<table>
<tr>
<td width="50%" align="center">
<img src="https://img.icons8.com/fluency/96/000000/laptop.png" width="64"/>
<br/>
<h4>💻 <a href="setup-local.md">Локальная установка</a></h4>
<sub>Python окружение и зависимости</sub>
</td>
<td width="50%" align="center">
<img src="https://img.icons8.com/fluency/96/000000/docker.png" width="64"/>
<br/>
<h4>🐳 <a href="setup-docker.md">Docker установка</a></h4>
<sub>Контейнеризация и развертывание</sub>
</td>
</tr>
</table>

### 📖 Основная документация

</div>

| Раздел | Описание |
|--------|----------|
| 📖 [Обзор системы](overview.md) | Архитектура, компоненты, движение данных |
| 🏗️ [Архитектура](architecture.md) | Диаграммы и взаимодействие компонентов |
| ⚙️ [Конфигурация](config.md) | Переменные окружения и настройки |
| 🗄️ [База данных](database.md) | Структура SQLite и миграции |
| 📝 [Логирование](logging.md) | Файлы логов и уровни |
| 📖 [Использование](usage.md) | Команды и интерактивные кнопки |
| 🧪 [Тесты](tests.md) | Запуск pytest и покрытие кода |
| 👨‍💻 [Разработка](development.md) | Руководство для разработчиков |
| 📜 [Скрипты](scripts.md) | Утилитарные скрипты и обертки |
| 🔧 [Решение проблем](troubleshooting.md) | Типовые ошибки и их решения |
| 📸 [Скриншоты](screenshots.md) | Визуальные примеры |

<details>
<summary><b>📋 Архитектурные решения (ADR)</b></summary>

Документированные решения по ключевым технологиям:

- [ADR-0001: Mindee как основной OCR провайдер](../adr/0001-mindee-as-primary-ocr-provider.md)
- [ADR-0002: SQLite как основное хранилище](../adr/0002-sqlite-as-primary-storage.md)
- [ADR-0003: Aiogram 3 как Telegram фреймворк](../adr/0003-aiogram3-as-telegram-framework.md)

</details>

---

<div align="center">

<img src="https://capsule-render.vercel.app/api?type=waving&color=gradient&height=100&section=footer"/>

</div>
