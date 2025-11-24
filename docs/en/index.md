# InvoiceFlowBot Documentation

InvoiceFlowBot is a Telegram assistant that automates invoice capture for finance teams. Users forward PDFs or photos, the bot extracts a structured draft via Mindee, lets the operator review and edit details, and persists confirmed invoices to SQLite.

The workflow removes repetitive manual entry. Accountants receive a ready draft, adjust header fields or line items, add comments, and store the final version with a single command. Historical queries stay available in the same bot chat.

## Documentation map

- [System overview](overview.md) — architecture, components, and the data path from Telegram to the database.
- [Architecture](architecture.md) — high level architecture diagrams and component interactions.
- [Local setup](setup-local.md) — run without Docker, configure the virtual environment and `.env`.
- [Docker setup](setup-docker.md) — container deployment, volume mounting, and upgrades.
- [Configuration](config.md) — every environment variable and how `config.py` reads it.
- [Database](database.md) — SQLite schema, entities, and backup tips.
- [Logging](logging.md) — log files, rotation, and recommended levels.
- [Usage](usage.md) — end-user flow, commands, and inline buttons.
- [Tests](tests.md) — pytest instructions and coverage areas.
- [Troubleshooting](troubleshooting.md) — quick fixes for common issues.
- [Screenshots](screenshots.md) — visual references for the most common bot flows.
- [Architecture decisions (ADR)](../adr/0001-mindee-as-primary-ocr-provider.md) — design decision records for key technology choices.
