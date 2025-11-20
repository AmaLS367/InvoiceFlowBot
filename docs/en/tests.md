# Tests

InvoiceFlowBot uses pytest, with development dependencies listed in `requirements-dev.txt`.

## How to run

```powershell
git clone https://github.com/AmaLS367/InvoiceFlowBot.git
cd InvoiceFlowBot
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
pytest
```

Pytest auto-discovers suites under `tests/`.

## Coverage areas

- `test_invoice_parsing.py` — converts Mindee responses into the internal format.
- `test_engine_utilities.py` — validates OCR engine helpers and logging utilities.
- `test_storage_dates.py` — checks ISO date conversions and database queries.
- `test_imports.py` — quick smoke test ensuring core modules import correctly.

## Development policy

- Ship new features with tests whenever they touch OCR parsing, formatting, or storage logic.
- Run `pytest` locally (or rely on CI) before submitting pull requests.
- Provide anonymized fixtures for tricky OCR cases to prevent regressions.

