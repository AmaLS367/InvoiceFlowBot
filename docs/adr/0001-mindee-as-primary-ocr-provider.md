# ADR 0001 - Mindee as primary OCR provider

## Status

Accepted

## Context

InvoiceFlowBot needs reliable OCR for invoices and receipts:

- structured fields (supplier, customer, dates, totals, line items)

- good support for different layouts and languages

- stable API with predictable latency

- clear commercial and free tier options

We want to avoid maintaining our own low level OCR stack and training pipeline inside this project.

## Decision

We use **Mindee** as the primary OCR provider for invoice extraction:

- HTTP integration is implemented in `ocr/mindee_client.py`.

- The async OCR abstraction is implemented in `ocr/providers/mindee_provider.py` and `ocr/engine/*`.

- The rest of the code depends on `OcrProvider` interface, not on Mindee SDK directly.

## Consequences

Positive:

- Fast path to reliable invoice extraction.

- Simple integration through HTTP API.

- Good quality of item level extraction for typical invoices.

Negative:

- External dependency on a third party API.

- Latency and availability depend on Mindee.

- For full offline mode another provider or engine would be required.

Mitigations:

- All business logic depends on `OcrProvider` abstraction.

- It is possible to plug a different provider or local engine without rewriting handlers and services.

