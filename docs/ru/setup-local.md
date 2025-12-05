# Установка локально

## Предусловия

- Python 3.11 или новее
- Установленный Git
- Аккаунт Telegram с бот-токеном и ключ Mindee

## Шаги запуска

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
- `MINDEE_API_KEY` — API ключ Mindee.
- `Model_id_mindee` — идентификатор модели Mindee для счетов.

5. **Запустите Telegram бот локально:**
```powershell
python bot.py
```

## Примечания

- Успешный запуск отображается сообщениями в консоли о старте бота и регистрациях хендлеров. При ошибках подключения в логах появится предупреждение Aiogram.
- Если бот не подключается к Telegram: проверьте правильность `BOT_TOKEN`, убедитесь в доступе к интернету и отсутствии ограничений прокси. После правки переменных перезапустите процесс.
