<img src="https://capsule-render.vercel.app/api?type=waving&color=gradient&customColorList=12,16,20&height=120&section=header&text=Локальная+установка&fontSize=35&animation=fadeIn"/>

<div align="center">

[![Python](https://img.shields.io/badge/Python-3.11+-blue?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![venv](https://img.shields.io/badge/Environment-Virtual-green?style=for-the-badge)](https://docs.python.org/3/library/venv.html)
[![Setup](https://img.shields.io/badge/Guide-Step%20by%20Step-orange?style=for-the-badge)](#шаги-запуска)

</div>

## 📋 О руководстве

> [!NOTE]
> Это руководство для установки без Docker. Для быстрого старта используйте [Docker](setup-docker.md).

## 📋 Предусловия

- 🐍 Python 3.11 или новее
- 📦 Установленный Git
- 🤖 Аккаунт Telegram с бот-токеном
- Tesseract в `PATH` с английским и русским языковыми пакетами. На Debian и Ubuntu установите их командой `sudo apt install tesseract-ocr tesseract-ocr-eng tesseract-ocr-rus`. Список установленных языков показывает `tesseract --list-langs`.

## 🚀 Шаги запуска

1. **Клонируйте репозиторий и перейдите в каталог проекта:**
```powershell
git clone https://github.com/AmaLS367/InvoiceFlowBot.git
cd InvoiceFlowBot
```

2. **Создайте виртуальное окружение под Windows PowerShell и активируйте его:**
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

3. **Установите зависимости для рабочего режима:**
```powershell
pip install -e .
```

4. **Создайте файл `.env` на основе `.env.example` и заполните ключевые переменные:**
```powershell
Copy-Item .env.example .env
notepad .env
```

Обязательные параметры:
- `BOT_TOKEN` — токен бота из @BotFather.

Локальное распознавание включено по умолчанию. Чтобы изменить набор языков, укажите в `OCR_LANGUAGES` коды установленных пакетов Tesseract через `+`. При первой обработке Docling скачает модели разметки и таблиц. Чтобы использовать скачанные модели без доступа к интернету, задайте `HF_HUB_OFFLINE=1`.

Для облачного распознавания задайте `OCR_PROVIDER=mindee`, `MINDEE_API_KEY` и `MINDEE_MODEL_ID`.

5. **Запустите Telegram бот локально:**
```powershell
python bot.py
```

## ✅ Примечания

> [!TIP]
> Успешный запуск отображается сообщениями в консоли о старте бота и регистрациях хендлеров.

> [!WARNING]
> Если бот не подключается к Telegram:
> - Проверьте правильность `BOT_TOKEN`
> - Убедитесь в доступе к интернету
> - Проверьте отсутствие ограничений прокси
> - После правки переменных перезапустите процесс
