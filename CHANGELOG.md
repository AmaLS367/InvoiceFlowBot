# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

---

## [0.5.0] - 2026-11-18

### Highlights

* **Local OCR by default**: invoices are now recognized on your own machine with Docling and Tesseract. No Mindee account or API key is needed. Mindee remains available as an opt-in provider.
* **Seven interface languages**: Russian, English, German, Spanish, French, Italian and Portuguese, with a per-user language picker and localized Telegram command menus.
* **Per-user invoice listings**: `/invoices` now returns only the requesting user's invoices (previously it could return every user's invoices).
* **Reworked documentation and README**: refreshed guides, an inline demo preview and command examples aligned with the real bot.

### Breaking changes and upgrade notes

* **Default OCR provider changed from Mindee to local.** Deployments that relied on Mindee must set `OCR_PROVIDER=mindee` together with `MINDEE_API_KEY` and `MINDEE_MODEL_ID`.
* **Environment variable names.** `.env.example` now uses `MINDEE_MODEL_ID` (previously `Model_id_mindee`).
* **Database path.** `DB_FILENAME` and `DB_DIR` are gone; the only setting is `INVOICE_DB_PATH`. Relative paths are resolved from the `backend/` directory and the default is `../data.sqlite` (the project root, `/app/data.sqlite` in Docker). If your existing database lives at `backend/data.sqlite`, move it or set `INVOICE_DB_PATH=data.sqlite`.
* **New migration `0002_user_languages`.** It creates the `user_languages` table. Migrations run on startup (`init_db()`); run `alembic upgrade head` from the project root if you manage them manually.
* **Docker image is larger.** It now bundles CPU-only PyTorch, Docling and Tesseract. Docling models are cached in the `ocr-models` volume (`HF_HOME=/app/data/huggingface`) so they survive container restarts.
* **Python API.** `fetch_invoices`, `fetch_invoices_domain`, `InvoiceService.list_invoices` and the container's `fetch_invoices_func` now take `user_id` as their first argument.

### Added

* **Local OCR provider** (`backend/ocr/providers/local_provider.py`, `local_invoice.py`):
  * Docling with the accurate TableFormer mode for PDFs and images, running on CPU with remote services disabled and a 120-second document timeout.
  * Tesseract OCR through `pytesseract`, with first-page text reading for header fields; PDFs are rendered with `pypdfium2`.
  * Configured with `OCR_PROVIDER` (`local` or `mindee`) and `OCR_LANGUAGES` (default `eng+rus`).
  * Provider selection in `backend/ocr/engine/router.py` through `get_ocr_provider()`; `doc_number` and `provider` are now stored in `extraction.json`.
* **Table and totals recovery for complex scans** (`InvoiceTableReader`):
  * Pairs label and value columns in totals boxes, so the grand total is no longer replaced by the subtotal.
  * Infers item columns from cell contents when OCR cannot read the headings.
  * Continues item tables across pages that do not repeat headings.
  * Accepts unit hints in headings, discount columns and wrapped descriptions.
  * Reads accounting brackets as negative amounts.
  * Checks every line total against quantity, price and discount; restores dropped decimal separators and normalizes Cyrillic look-alikes in article codes.
  * Marks derived, corrected and mismatching rows for review. The bot lists them to the user after the draft is shown (`review` flags on items and on the extraction result).
* **Interface localization**:
  * JSON catalogs in `backend/handlers/locales/` (`ru`, `en`, `de`, `es`, `fr`, `it`, `pt`), packaged with the wheel.
  * `/language` command and language picker; the choice is saved per user in SQLite (`backend/storage/user_languages.py`, table `user_languages`).
  * `locale_middleware` resolves the locale from the saved preference, then the Telegram client language, then the default (`ru`).
  * The Telegram command menu is registered per language and updated for the private chat when a user switches language.
  * New users see the language picker before the main menu; returning users go straight to the menu.
* **Empty OCR detection**: `EmptyOcrResultError` is raised when OCR finishes without any header fields or items, and the user gets a clear message instead of an empty draft.
* **Shared reply dispatcher** for force-reply messages across the drafts and invoices command modules.
* **Comments are shown and saved**: the full invoice view includes a comments section, and draft comments (including the automatic sum-mismatch note) are written to the invoice on save without duplicates.
* **Docker**: Tesseract (`eng`, `rus`) installed in the runtime image, an `ocr-models` volume in `docker-compose.yml` and a pre-created model cache directory.
* **Repository**: `.gitattributes` for consistent line endings and binary file handling; `.gitignore` entries for pytest and storage temp directories and agent configuration files; `workflow_dispatch` trigger for the security workflow.
* **Documentation**: inline demo preview (`demo.webp`) and demo video in `docs/assets/screenshots/`.
* **Tests**: coverage for the local provider, language handling, draft serialization, Mindee response parsing, config paths, handler texts and a full OCR to draft to save integration flow.

### Changed

* **Handlers are language-neutral.** Hard-coded Russian strings were moved out of the handlers into `backend/handlers/texts.py` and the locale catalogs; keyboards, prompts, status messages and invoice cards all go through `texts.t()`.
* **Mindee client**:
  * Uses `enqueue_and_get_result` with `InferenceResponse` and accepts the V2 response shape (`inference.result.fields`, nested line items with a `fields` object, `invoice_date` and `total_amount` fallbacks).
  * The HTTP fallback builds its URL from the configured model id and is skipped for V2 or custom model ids (UUIDs).
  * The debug dump is written to the configured log directory, and a failed dump can no longer turn a successful response into a failed OCR request.
  * The SDK is pinned to `mindee>=4.27.0,<5.0.0`.
* **OCR router** no longer rewrites the provider's score and labels results with the active provider name instead of a fixed `mindee`.
* **Startup** (`bot.py`): the database is initialized with `init_db()` before polling and the localized command menus are registered at launch.
* **Invoice listing**: the SQL for `fetch_invoices` was simplified into one parameterized query that always filters by `user_id`.
* **Packaging** (`pyproject.toml`): new dependencies `docling`, `pypdfium2` and `pytesseract`; added author and project URLs; `backend.ocr.engine` and `backend.ocr.providers` are now listed as packages and locale JSON files as package data; the build requires `setuptools>=84.1.0`; the global `--cov-fail-under=80` gate was removed from the pytest options.
* **Documentation**: READMEs (EN and RU) rewritten and shortened, with the supported languages and local OCR described; all guides in `docs/en` and `docs/ru` updated for local OCR, the database path, Docker setup, command examples and troubleshooting.
* **Images**: the four README screenshots were losslessly optimized (about 26% smaller) by ImgBot.

### Fixed

* **Privacy**: `/invoices` and its force-reply flow returned invoices of all users; they are now scoped to the requesting user. Updates without a user, or sent on behalf of a chat, are ignored.
* **Reply handling**: replies to force-reply prompts for drafts and invoices are routed through one dispatcher, so the two handlers no longer compete for the same message.
* **Comments**: duplicate automatic sum-mismatch comments are no longer added, and draft comments are no longer lost when saving.
* **Config paths**: database and Alembic paths resolve consistently for local and Docker runs, and in-memory databases work in migrations.
* **Uploads**: files that produce no OCR data, or hit an unavailable OCR service, give a specific message; document and photo uploads are logged with user and file details.
* **CI and security**:
  * Upgraded `lychee-action` to v2 and fixed the documentation link check.
  * Raised `setuptools` to `>=84.1.0` for the security audit.
  * Trivy ignores unfixed CVEs.
  * The runtime Docker image applies OS security updates and no longer ships `pip`, `setuptools` or `wheel`; only `site-packages` is copied from the builder stage.

### Removed

* The `DB_FILENAME` and `DB_DIR` settings (replaced by `INVOICE_DB_PATH`).
* The `Model_id_mindee` variable from `.env.example`.
* Hard-coded Mindee model URL in the HTTP fallback.

---

## [0.4.0] - 2026-01-24

### Highlights

* **Major project structure refactoring**: All application code moved to `backend/` namespace (instead of scattered across the root).
* **CI/CD and security improvements**: Added separate pipelines for coverage, docker, docs, release, and security scanning.
* **Packaging cleanup**: Version in `pyproject.toml` now properly aligned with release tags.

### Added

* **`backend/` package structure** as a single entry point for application and modules:
  * `backend/core/` - Dependency injection container and middleware
  * `backend/domain/` - Domain models (invoices, drafts)
  * `backend/services/` - Business logic layer (draft_service, invoice_service, async_utils)
  * `backend/storage/` - Async database layer with mappers and drafts persistence
  * `backend/ocr/` - OCR engine with providers and async client
  * `backend/handlers/` - Telegram handlers (commands, callbacks, FSM, DI middleware)
  * `backend/alembic/` - Database migrations
  * `backend/healthcheck.py` - Docker healthcheck script for Python imports
* **Development scripts** (`scripts/`):
  * Python scripts for setup, testing, linting, formatting, migration, and running
  * Platform-specific wrappers (Linux shell, Windows PowerShell)
* **Quality and content checking**:
  * `.lycheeignore` - Link checker ignore patterns
  * `.markdownlint.json` - Markdown linting configuration

### Changed

* **Project structure**:
  * Moved all modules from root (`handlers/`, `ocr/`, `storage/`, `services/`, `domain/`, `core/`, `alembic/`) into `backend/`
  * Updated all imports to use `backend.*` namespace
* **GitHub Actions workflows**:
  * Split single CI into multiple specialized workflows:
    * `ci.yml` - Tests and linting
    * `coverage.yml` - Code coverage reporting
    * `docker.yml` - Docker image build and test
    * `docker-compose.yml` - Docker Compose integration tests
    * `docs.yml` - Documentation link checking
    * `release.yml` - Docker image publishing from version tags and GitHub Releases for `vX.0.0` tags
    * `security.yml` - Security scanning (bandit, pip-audit, Trivy)

### Fixed

* Package version in `pyproject.toml` now correctly matches release `0.4.0` (previously inconsistent in `0.3.0`)
* Fixed import paths in test files (corrected `patch()` calls to use `backend.*` namespace)
* Fixed code formatting and indentation issues across test files
* Fixed import sorting in `backend/alembic/env.py` and `backend/storage/db.py`

### Removed

* Old root-level directories (moved to `backend/`):
  * `handlers/`, `ocr/`, `storage/`, `services/`, `domain/`, `core/`, `alembic/`
* Root-level configuration files (now in `backend/`):
  * `config.py`, `healthcheck.py`, `alembic.ini`

---

## [0.3.0]

### Highlights

* **Full drafts system**: Interactive editing workflow via Telegram callbacks
* **Database migrations**: Alembic-based schema management
* **Mature architecture**: Dependency injection, middleware, and command separation

### Added

* **Drafts functionality**:
  * `domain/drafts.py` - Domain entities and structures for drafts
  * `services/draft_service.py` - Business logic for draft management
  * `handlers/commands_drafts.py` - Draft-related commands
  * `handlers/callbacks_edit.py` - Interactive editing callbacks
* **Async storage layer**:
  * `storage/db_async.py` - Async database operations
  * `storage/drafts_async.py` - Async draft persistence
  * `storage/mappers.py` - Domain-to-storage conversion layer
* **Database migrations**:
  * `alembic/` directory with migration configuration
  * `alembic/versions/0001_initial_schema.py` - Initial database schema
* **Application architecture**:
  * `core/container.py` - Dependency injection container
  * `handlers/di_middleware.py` - DI middleware for handlers
  * `handlers/callback_registry.py` - Callback handler registry
  * `handlers/commands_common.py`, `handlers/commands_invoices.py` - Separated command handlers
  * `handlers/fsm.py` - Finite state machine management
* **OCR improvements**:
  * `ocr/async_client.py` - Async OCR client wrapper
* **Documentation**:
  * `README.ru.md` - Russian README
  * `CONTRIBUTING.md` - Contribution guidelines
* **DevSecOps**:
  * `.pre-commit-config.yaml` - Pre-commit hooks configuration
  * `bandit.yaml` - Security linting configuration
  * Expanded test coverage across all modules

### Changed

* **Refactored modules**:
  * `handlers/` - Restructured command/callback architecture with FSM and DI integration
  * `ocr/` - Transitioned to modular provider approach with async support
  * `storage/` - Added async operations and mappers
  * `docs/` - Updated structure and content
* **Packaging**:
  * Migrated from `requirements.txt` to `pyproject.toml` for dependency management
  * Consolidated linting configs (removed `.ruff.toml`, `mypy.ini`)

### Fixed

* Multiple fixes in tests and handlers for stability after feature expansion
* Stabilized draft and callback functionality

### Removed

* Old configuration files:
  * `.ruff.toml`, `mypy.ini`
  * `requirements.txt`, `requirements-dev.txt`

---

## [0.2.0]

### Highlights

* **Modular architecture**: Introduced domain, service, and storage layers
* **OCR provider abstraction**: Modular OCR system with provider pattern
* **Docker support**: Containerization and deployment automation
* **Bilingual documentation**: English and Russian documentation structure

### Added

* **Documentation**:
  * `docs/` directory with language separation (`docs/en/`, `docs/ru/`)
  * `docs/assets/` - Screenshots and visual assets
* **Architectural layers**:
  * `domain/` - Invoice domain models and structures
  * `services/` - Service layer (`invoice_service.py`)
* **OCR providers**:
  * `ocr/providers/base.py` - Base provider interface
  * `ocr/providers/mindee_provider.py` - Mindee provider implementation
  * Proper package structure in `ocr/`
* **Docker**:
  * `Dockerfile` - Container image definition
  * `docker-compose.yml` - Docker Compose configuration
  * `.dockerignore` - Docker build exclusions
* **Tooling**:
  * `pyproject.toml` - Centralized project configuration
  * `.ruff.toml`, `mypy.ini` - Initial quality tooling setup
* **Storage package**:
  * `storage/__init__.py` - Package initialization

### Changed

* **OCR engine**:
  * Refactored `ocr/engine/*`, `ocr/extract.py`, `ocr/mindee_client.py` for provider pattern
* **Handlers**:
  * Added `handlers/callbacks.py` with improved command/state management
* **Configuration**:
  * Updated `bot.py`, `config.py`, `.env.example`, `.gitignore`
* **Tests**:
  * Expanded test suite (parsing, storage dates, engine utilities)

### Fixed

* Improved stability of file processing and OCR field extraction

---

## [0.1.0] - 2025

### Highlights

* **Initial MVP release**: Basic bot functionality with OCR and storage

### Added

* **Telegram bot**:
  * `bot.py` - Main bot entry point
* **Configuration**:
  * `config.py` - Configuration management
  * `requirements.txt`, `requirements-dev.txt` - Dependency management
* **OCR layer**:
  * `ocr/extract.py` - OCR extraction logic
  * `ocr/mindee_client.py` - Mindee API client
  * `ocr/engine/*` - OCR engine (router, types, utilities)
* **Handlers**:
  * `handlers/commands.py` - Bot commands
  * `handlers/file.py` - File upload handling
  * `handlers/state.py` - State management
  * `handlers/utils.py` - Utility functions
* **Storage**:
  * `storage/db.py` - SQLite database operations
* **CI/CD**:
  * `.github/workflows/ci.yml` - Basic CI pipeline
* **Tests**:
  * Basic unit tests for OCR utilities, parsing, and storage dates

---

[Unreleased]: https://github.com/AmaLS367/InvoiceFlowBot/compare/v0.5.0...HEAD
[0.5.0]: https://github.com/AmaLS367/InvoiceFlowBot/compare/v0.4.0...v0.5.0
[0.4.0]: https://github.com/AmaLS367/InvoiceFlowBot/compare/v0.3.0...v0.4.0
[0.3.0]: https://github.com/AmaLS367/InvoiceFlowBot/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/AmaLS367/InvoiceFlowBot/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/AmaLS367/InvoiceFlowBot/releases/tag/v0.1.0
