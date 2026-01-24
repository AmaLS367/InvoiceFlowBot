<img src="https://capsule-render.vercel.app/api?type=waving&color=gradient&customColorList=6,11,20&height=120&section=header&text=Руководство+по+скриптам&fontSize=40&animation=fadeIn"/>

<div align="center">

[![Python](https://img.shields.io/badge/Python-3.11+-blue?style=for-the-badge&logo=python)](https://www.python.org/)
[![Linux](https://img.shields.io/badge/Linux-Shell-green?style=for-the-badge&logo=linux)](https://www.linux.org/)
[![Windows](https://img.shields.io/badge/Windows-PowerShell-blue?style=for-the-badge&logo=windows)](https://www.microsoft.com/windows)

</div>

## 📋 Обзор

Проект включает набор утилитарных скриптов, организованных по платформам в директории `scripts/`. Эти скрипты предоставляют удобные обертки для типовых задач разработки.

## 📁 Структура директорий

```
scripts/
├── python/          # Основные Python скрипты
│   ├── setup.py     # Установка зависимостей и настройка окружения
│   ├── migrate.py   # Миграции базы данных
│   ├── run.py       # Запуск бота
│   ├── test.py      # Запуск тестов
│   ├── lint.py      # Проверка кода
│   ├── format.py    # Форматирование кода
│   └── context_gen.py  # Генерация контекста проекта
├── linux/           # Обертки для Linux shell
│   ├── setup.sh
│   ├── migrate.sh
│   ├── run.sh
│   ├── test.sh
│   ├── lint.sh
│   └── format.sh
└── windows/         # Обертки для Windows PowerShell
    ├── setup.ps1
    ├── migrate.ps1
    ├── run.ps1
    ├── test.ps1
    ├── lint.ps1
    └── format.ps1
```

## 🐍 Python скрипты

Все Python скрипты находятся в `scripts/python/` и могут быть запущены напрямую или как модули.

### Прямой запуск

```bash
python scripts/python/setup.py
python scripts/python/migrate.py
python scripts/python/run.py
```

### Запуск как модуль

```bash
python -m scripts.python.setup
python -m scripts.python.migrate
python -m scripts.python.run
```

### setup.py

Устанавливает пакет в editable режиме с dev-зависимостями и создает файл `.env` из `.env.example`, если он не существует.

**Использование:**

```bash
# Linux/macOS
./scripts/linux/setup.sh

# Windows PowerShell
.\scripts\windows\setup.ps1

# Прямой Python
python scripts/python/setup.py
```

### migrate.py

Запускает миграции базы данных Alembic. Поддерживает все команды Alembic.

**Использование:**

```bash
# Обновить до последней версии
python scripts/python/migrate.py

# Пользовательская команда Alembic
python scripts/python/migrate.py downgrade -1
python scripts/python/migrate.py revision -m "add new table"
```

### run.py

Применяет миграции базы данных и запускает бота.

**Использование:**

```bash
python scripts/python/run.py
```

### test.py

Запускает pytest с покрытием. Поддерживает аргументы pytest.

**Использование:**

```bash
# Запустить все тесты
python scripts/python/test.py

# Запустить конкретный файл
python scripts/python/test.py tests/test_invoice_service.py

# Запустить с маркером
python scripts/python/test.py -m "not storage_db"
```

### lint.py

Запускает проверки качества кода: ruff check и mypy type checking.

**Использование:**

```bash
python scripts/python/lint.py
```

### format.py

Форматирует код с помощью ruff formatter.

**Использование:**

```bash
python scripts/python/format.py
```

### context_gen.py

Генерирует файл полного контекста проекта (`full_project_context.txt`), содержащий все файлы проекта для AI контекста.

**Использование:**

```bash
python scripts/python/context_gen.py
```

## 🐧 Linux скрипты

Обертки для Linux shell находятся в `scripts/linux/`. Они предоставляют удобные ярлыки для Python скриптов.

**Сделать скрипты исполняемыми:**

```bash
chmod +x scripts/linux/*.sh
```

**Использование:**

```bash
./scripts/linux/setup.sh
./scripts/linux/migrate.sh
./scripts/linux/run.sh
./scripts/linux/test.sh
./scripts/linux/lint.sh
./scripts/linux/format.sh
```

Все скрипты поддерживают передачу аргументов в базовые Python скрипты:

```bash
./scripts/linux/test.sh -m "not storage_db"
./scripts/linux/migrate.sh downgrade -1
```

## 🪟 Windows скрипты

Обертки для Windows PowerShell находятся в `scripts/windows/`.

**Использование:**

```powershell
.\scripts\windows\setup.ps1
.\scripts\windows\migrate.ps1
.\scripts\windows\run.ps1
.\scripts\windows\test.ps1
.\scripts\windows\lint.ps1
.\scripts\windows\format.ps1
```

**Примечание:** Если вы столкнулись с ограничениями политики выполнения, выполните:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Все скрипты поддерживают передачу аргументов:

```powershell
.\scripts\windows\test.ps1 -m "not storage_db"
.\scripts\windows\migrate.ps1 downgrade -1
```

## 🔄 Типовой рабочий процесс

### Первоначальная настройка

```bash
# Linux/macOS
./scripts/linux/setup.sh

# Windows
.\scripts\windows\setup.ps1
```

### Цикл разработки

```bash
# Форматировать код
./scripts/linux/format.sh    # или .\scripts\windows\format.ps1

# Проверить код
./scripts/linux/lint.sh      # или .\scripts\windows\lint.ps1

# Запустить тесты
./scripts/linux/test.sh      # или .\scripts\windows\test.ps1

# Запустить миграции
./scripts/linux/migrate.sh   # или .\scripts\windows\migrate.ps1

# Запустить бота
./scripts/linux/run.sh       # или .\scripts\windows\run.ps1
```

## 📝 Примечания

- Все скрипты автоматически определяют корневую директорию проекта
- Скрипты работают из любого места в проекте
- Python скрипты могут быть запущены напрямую или как модули
- Shell/PowerShell скрипты являются тонкими обертками, которые передают аргументы дальше
- Все скрипты используют относительные пути и являются портативными

---

<div align="center">

<img src="https://capsule-render.vercel.app/api?type=waving&color=gradient&height=100&section=footer"/>

</div>
