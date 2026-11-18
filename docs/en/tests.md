<img src="https://capsule-render.vercel.app/api?type=waving&color=gradient&customColorList=12,16,20&height=120&section=header&text=Testing&fontSize=40&animation=fadeIn"/>

<div align="center">

[![pytest](https://img.shields.io/badge/Framework-pytest-blue?style=for-the-badge&logo=pytest)](https://pytest.org/)
[![Coverage](https://img.shields.io/badge/Coverage-80%25+-green?style=for-the-badge)](https://coverage.readthedocs.io/)

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
$env:BOT_TOKEN = 'test-token'
pytest
```

Pytest auto-discovers suites under `tests/`. On Bash, run `BOT_TOKEN=test-token python -m pytest`. You can reuse the test token for individual suites and the test wrapper.

## Coverage areas

The coverage workflow enforces a minimum of **80%**. The suite covers these areas:

### Core test files

- `tests/test_invoice_parsing.py` — converts Mindee responses into the internal format, formatting and utilities
- `tests/test_engine_utilities.py` — validates OCR engine helpers and logging utilities
- `tests/test_storage_dates.py` — checks ISO date conversions and database queries
- `tests/test_imports.py` — quick smoke test ensuring core modules import correctly
- `tests/test_invoice_service.py` — service layer tests with mocked OCR and storage:
  - `process_invoice_file` — tests OCR integration and domain model conversion
  - `save_invoice` and `list_invoices` — tests storage layer delegation

### Handler tests

- `tests/handlers/test_callbacks_edit.py` — tests for invoice editing via callback buttons
- `tests/handlers/test_callbacks_misc.py` — tests for miscellaneous callback handlers
- `tests/handlers/test_commands_basic.py` — tests for basic bot commands
- `tests/handlers/test_commands_drafts.py` — tests for draft management
- `tests/handlers/test_commands_invoices_force_reply.py` — tests for invoice queries
- `tests/handlers/test_languages.py` — localized menus, persisted preferences, and catalog consistency
- `tests/handlers/test_file_upload_*.py` — tests for file uploads

### OCR tests

- `tests/ocr/test_extract.py` — tests for data extraction from documents
- `tests/ocr/test_async_client.py` — tests for async OCR client
- `tests/ocr/test_router.py` — tests for OCR router
- `tests/ocr/test_local_provider.py` — local extraction, table parsing and review markers

### Storage tests

- `tests/storage/test_mappers.py` — tests for domain-to-DB mapping
- `tests/storage/test_storage_invoices_crud.py` — integration tests for CRUD operations
- `tests/storage/test_storage_migrations.py` — tests for database migrations

### Domain tests

- `tests/domain/test_invoice*.py` — tests for domain models (Invoice, InvoiceHeader, InvoiceItem, etc.)

### Integration tests

- `tests/integration/test_flow_ocr_draft_save.py` — full flow test from OCR to invoice saving

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
$env:BOT_TOKEN = 'test-token'
python -m pytest
```

You can also run a specific test file:

```powershell
python -m pytest tests/test_invoice_service.py
```

CI runs pre-commit, mypy, and pytest on pushes to `main` or `master` and pull requests targeting either branch. See the [development guide](development.md#ci-pipeline).

## Development policy

- Ship new features with tests whenever they touch OCR parsing, formatting, or storage logic.
- Run `pytest` locally (or rely on CI) before submitting pull requests.
- Provide anonymized fixtures for tricky OCR cases to prevent regressions.
- Ensure code passes `ruff` and `mypy` checks before submitting pull requests.
