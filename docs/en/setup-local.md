<img src="https://capsule-render.vercel.app/api?type=waving&color=gradient&customColorList=12,16,20&height=120&section=header&text=Local+Setup&fontSize=40&animation=fadeIn"/>

<div align="center">

[![Python](https://img.shields.io/badge/Python-3.11+-blue?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![venv](https://img.shields.io/badge/Environment-Virtual-green?style=for-the-badge)](https://docs.python.org/3/library/venv.html)
[![Setup](https://img.shields.io/badge/Guide-Step%20by%20Step-orange?style=for-the-badge)](#-steps)

</div>

## 📋 About

> [!NOTE]
> This guide is for installation without Docker. For quick start, see [Docker setup](setup-docker.md).

## 📋 Prerequisites

- 🐍 Python 3.11 or newer
- 📦 Git installed
- 🤖 Telegram bot token
- Tesseract on `PATH` with the English and Russian language packs. On Debian or Ubuntu, install them with `sudo apt install tesseract-ocr tesseract-ocr-eng tesseract-ocr-rus`. Verify the installed languages with `tesseract --list-langs`.

## 🚀 Steps

1. **Clone the repository and enter the project directory:**
```powershell
git clone https://github.com/AmaLS367/InvoiceFlowBot.git
cd InvoiceFlowBot
```

2. **Create and activate a Windows virtual environment:**
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

3. **Install runtime dependencies:**
```powershell
pip install -e .
```

4. **Create `.env` from the template and set required variables:**
```powershell
Copy-Item .env.example .env
notepad .env
```

Required values:
- `BOT_TOKEN` — token from @BotFather.

Local OCR is the default. Set `OCR_LANGUAGES` to the installed Tesseract language codes, joined with `+`, if you use a different set of languages. Docling downloads its layout and table models the first time it processes a file. Once the models are cached, export `HF_HUB_OFFLINE=1` in the process environment to use them offline.

To use the cloud provider, set `OCR_PROVIDER=mindee` and supply `MINDEE_API_KEY` and `MINDEE_MODEL_ID`.

5. **Run the bot:**
```powershell
python bot.py
```

## ✅ Notes

> [!TIP]
> Send `/start` in Telegram to verify the launch. Check `logs/ocr_engine.log` for startup events. Set `LOG_CONSOLE=1` for application logs on stderr.

> [!WARNING]
> If the bot does not connect to Telegram:
> - Double-check `BOT_TOKEN` in `.env`
> - Confirm internet access
> - Check for proxy restrictions
> - Restart the process after fixing variables
