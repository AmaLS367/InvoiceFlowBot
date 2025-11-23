# Tests

InvoiceFlowBot uses pytest, with development dependencies defined in `pyproject.toml` under the `[project.optional-dependencies]` section.

## How to run

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

- `test_invoice_parsing.py` — converts Mindee responses into the internal format.
- `test_engine_utilities.py` — validates OCR engine helpers and logging utilities.
- `test_storage_dates.py` — checks ISO date conversions and database queries.
- `test_imports.py` — quick smoke test ensuring core modules import correctly.
- `test_invoice_service.py` — service layer tests with mocked OCR and storage:
  - `process_invoice_file` — tests OCR integration and domain model conversion
  - `save_invoice` and `list_invoices` — tests storage layer delegation

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
python -m mypy domain services ocr storage

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
