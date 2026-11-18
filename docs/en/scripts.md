<img src="https://capsule-render.vercel.app/api?type=waving&color=gradient&customColorList=6,11,20&height=120&section=header&text=Scripts+Guide&fontSize=40&animation=fadeIn"/>

<div align="center">

[![Python](https://img.shields.io/badge/Python-3.11+-blue?style=for-the-badge&logo=python)](https://www.python.org/)
[![Linux](https://img.shields.io/badge/Linux-Shell-green?style=for-the-badge&logo=linux)](https://www.linux.org/)
[![Windows](https://img.shields.io/badge/Windows-PowerShell-blue?style=for-the-badge&logo=windows)](https://www.microsoft.com/windows)

</div>

## 📋 Overview

The project includes a collection of utility scripts organized by platform in the `scripts/` directory. These scripts provide convenient wrappers for common development tasks.

## 📁 Directory Structure

```
scripts/
├── python/          # Core Python scripts
│   ├── setup.py     # Install dependencies and setup environment
│   ├── migrate.py   # Database migrations
│   ├── run.py       # Run the bot
│   ├── test.py      # Run tests
│   ├── lint.py      # Code linting
│   ├── format.py    # Code formatting
│   └── context_gen.py  # Generate project context
├── linux/           # Linux shell script wrappers
│   ├── setup.sh
│   ├── migrate.sh
│   ├── run.sh
│   ├── test.sh
│   ├── lint.sh
│   └── format.sh
└── windows/         # Windows PowerShell wrappers
    ├── setup.ps1
    ├── migrate.ps1
    ├── run.ps1
    ├── test.ps1
    ├── lint.ps1
    └── format.ps1
```

## 🐍 Python Scripts

All Python scripts are located in `scripts/python/` and can be run directly or as modules.

### Direct execution

```bash
python scripts/python/setup.py
python scripts/python/migrate.py
python scripts/python/run.py
```

### Module execution

```bash
python -m scripts.python.setup
python -m scripts.python.migrate
python -m scripts.python.run
```

### setup.py

Installs the package in editable mode with development dependencies and creates `.env` file from `.env.example` if it doesn't exist.

**Usage:**

```bash
# Linux/macOS
bash scripts/linux/setup.sh

# Windows PowerShell
.\scripts\windows\setup.ps1

# Direct Python
python scripts/python/setup.py
```

### migrate.py

Runs Alembic migrations. Set `BOT_TOKEN` in `.env` or the process environment. Use the direct Alembic command for arguments that contain spaces, such as revision messages.

**Usage:**

```bash
# Upgrade to latest
python scripts/python/migrate.py

# Custom Alembic command
python scripts/python/migrate.py downgrade -1
python -m alembic -c backend/alembic.ini revision -m "add new table"
```

### run.py

Applies database migrations and starts the bot.

**Usage:**

```bash
python scripts/python/run.py
```

### test.py

Runs pytest with coverage and accepts additional pytest arguments. Set `BOT_TOKEN=test-token` in the process environment before running tests.

**Usage:**

```bash
# Run all tests
python scripts/python/test.py

# Run specific test file
python scripts/python/test.py tests/test_invoice_service.py

# Run with marker
python scripts/python/test.py -m "not storage_db"
```

### lint.py

Runs code quality checks: ruff check and mypy type checking.

**Usage:**

```bash
python scripts/python/lint.py
```

### format.py

Formats code using ruff formatter.

**Usage:**

```bash
python scripts/python/format.py
```

### context_gen.py

Writes `full_project_context(0.4.0).txt` in the project root using selected source, configuration, and Markdown files. It skips configured paths such as `.venv`, `data/`, and `logs/`.

**Usage:**

```bash
python scripts/python/context_gen.py
```

## 🐧 Linux Scripts

Linux shell script wrappers are located in `scripts/linux/`. They provide convenient shortcuts to Python scripts.

**Make scripts executable:**

```bash
chmod +x scripts/linux/*.sh
```

**Usage:**

```bash
./scripts/linux/setup.sh
./scripts/linux/migrate.sh
./scripts/linux/run.sh
./scripts/linux/test.sh
./scripts/linux/lint.sh
./scripts/linux/format.sh
```

All scripts support passing arguments to the underlying Python scripts:

```bash
./scripts/linux/test.sh -m "not storage_db"
./scripts/linux/migrate.sh downgrade -1
```

## 🪟 Windows Scripts

Windows PowerShell script wrappers are located in `scripts/windows/`.

**Usage:**

```powershell
.\scripts\windows\setup.ps1
.\scripts\windows\migrate.ps1
.\scripts\windows\run.ps1
.\scripts\windows\test.ps1
.\scripts\windows\lint.ps1
.\scripts\windows\format.ps1
```

**Note:** If you encounter execution policy restrictions, run:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

All scripts support passing arguments:

```powershell
.\scripts\windows\test.ps1 -m "not storage_db"
.\scripts\windows\migrate.ps1 downgrade -1
```

## 🔄 Typical Workflow

### Initial Setup

```bash
# Linux/macOS
bash scripts/linux/setup.sh

# Windows
.\scripts\windows\setup.ps1
```

### Development Cycle

```bash
# Format code
./scripts/linux/format.sh    # or .\scripts\windows\format.ps1

# Lint code
./scripts/linux/lint.sh      # or .\scripts\windows\lint.ps1

# Run tests
./scripts/linux/test.sh      # or .\scripts\windows\test.ps1

# Run migrations
./scripts/linux/migrate.sh   # or .\scripts\windows\migrate.ps1

# Start bot
./scripts/linux/run.sh       # or .\scripts\windows\run.ps1
```

## 📝 Notes

- All scripts automatically detect the project root directory
- Pass the path to a script from another directory. Module invocations such as `python -m scripts.python.setup` should be run from the project root.
- Python scripts can be run directly or as modules
- Shell/PowerShell scripts are thin wrappers that pass arguments through
- All scripts use relative paths and are portable

---

<div align="center">

<img src="https://capsule-render.vercel.app/api?type=waving&color=gradient&height=100&section=footer"/>

</div>
