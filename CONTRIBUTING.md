# Contributing to InvoiceFlowBot

This document describes how to work with the codebase as a developer.

## Development environment

1. Clone the repository:

```powershell
git clone https://github.com/AmaLS367/InvoiceFlowBot.git
cd InvoiceFlowBot
```

2. Create and activate virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

3. Install dependencies in editable mode with dev extras:

```powershell
python -m pip install -e .[dev]
```

## Running tests and checks

Before committing code, run:

```powershell
python -m ruff check .

python -m mypy domain services ocr storage handlers

python -m pytest
```

Coverage configuration is defined in `pyproject.toml`.

Unit tests and integration tests live under the `tests/` package.

## Pre-commit hooks

This project uses `pre-commit` for local checks:

* ruff lint and formatting

* mypy type checking

* bandit security checks

Install and run hooks:

```powershell
pre-commit install

pre-commit run --all-files
```

CI will also run `pre-commit` on every push and pull request.

## Coding guidelines

* Target Python 3.11+.

* Keep layers separated: `domain`, `services`, `ocr`, `storage`, `handlers`, `core`.

* Business logic should live in `services` and `domain`, not in handlers.

* Prefer async I/O for network and database access.

* Add or update tests for any non trivial change in behaviour.

## Documentation

Architecture and design decisions:

* `docs/en/architecture.md` and `docs/ru/architecture.md` for high level diagrams.

* `docs/adr/` for architecture decision records.

If you change the way the bot is configured or deployed, please update the relevant docs in `docs/en` and `docs/ru`.
