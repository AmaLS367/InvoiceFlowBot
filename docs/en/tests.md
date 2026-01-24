<img src="https://capsule-render.vercel.app/api?type=waving&color=gradient&customColorList=12,16,20&height=120&section=header&text=Testing&fontSize=40&animation=fadeIn"/>

<div align="center">

[![pytest](https://img.shields.io/badge/Framework-pytest-blue?style=for-the-badge&logo=pytest)](https://pytest.org/)
[![Coverage](https://img.shields.io/badge/Coverage-80%25+-green?style=for-the-badge)](https://coverage.readthedocs.io/)
[![Tests](https://img.shields.io/badge/Tests-160+-orange?style=for-the-badge)](#how-to-run)

</div>

## 📋 About Testing

InvoiceFlowBot uses pytest, with development dependencies defined in `pyproject.toml` under the `[project.optional-dependencies]` section.

> [!NOTE]
> For development, install dev dependencies: `pip install -e .[dev]`

## 🚀 How to run

```powershell
git clone https://github.com/AmaLS367/InvoiceFlowBot.git
cd InvoiceFlowBot
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e .[dev]
pytest
```

Pytest auto-discovers suites under `tests/`.

## Coverage areas

The project has **80% code coverage** with **160+ tests**, covering all major modules:

### Core test files

- `test_invoice_parsing.py` — converts Mindee responses into the internal format, formatting and utilities
- `test_engine_utilities.py` — validates OCR engine helpers and logging utilities
- `test_storage_dates.py` — checks ISO date conversions and database queries
- `test_imports.py` — quick smoke test ensuring core modules import correctly
- `test_invoice_service.py` — service layer tests with mocked OCR and storage:
  - `process_invoice_file` — tests OCR integration and domain model conversion
  - `save_invoice` and `list_invoices` — tests storage layer delegation

### Handler tests

- `handlers/test_callbacks_edit.py` — tests for invoice editing via callback buttons
- `handlers/test_callbacks_misc.py` — tests for miscellaneous callback handlers
- `handlers/test_commands_basic.py` — tests for basic bot commands
- `handlers/test_commands_drafts.py` — tests for draft management
- `handlers/test_commands_invoices_force_reply.py` — tests for invoice queries
- `handlers/test_file_upload_*.py` — tests for file uploads

### OCR tests

- `ocr/test_extract.py` — tests for data extraction from documents
- `ocr/test_async_client.py` — tests for async OCR client
- `ocr/test_router.py` — tests for OCR router

### Storage tests

- `storage/test_mappers.py` — tests for domain-to-DB mapping
- `storage/test_storage_invoices_crud.py` — integration tests for CRUD operations
- `storage/test_storage_migrations.py` — tests for database migrations

### Domain tests

- `domain/test_invoice*.py` — tests for domain models (Invoice, InvoiceHeader, InvoiceItem, etc.)

### Integration tests

- `integration/test_flow_ocr_draft_save.py` — full flow test from OCR to invoice saving

## Code Quality Tools

The project uses automated code quality checks:

- **ruff** — Fast Python linter for code style and common errors
- **mypy** — Static type checker for Python

### Running Quality Checks

```powershell
# Install development dependencies
pip install -e .[dev]

# Run linter
python -m ruff check .

# Run type checker
python -m mypy backend/

# Run tests
python -m pytest
```

You can also run a specific test file:

```powershell
python -m pytest tests/test_invoice_service.py
```

The CI pipeline automatically runs `ruff`, `mypy`, and `pytest` on every push and pull request.

## Development policy

- Ship new features with tests whenever they touch OCR parsing, formatting, or storage logic.
- Run `pytest` locally (or rely on CI) before submitting pull requests.
- Provide anonymized fixtures for tricky OCR cases to prevent regressions.
- Ensure code passes `ruff` and `mypy` checks before submitting pull requests.
