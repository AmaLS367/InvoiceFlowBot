# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
  * `backend/healthcheck.py` - Health check endpoint
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
    * `release.yml` - Docker image publishing (releases only for major versions)
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

## [0.1.0] - 2025-XX-XX

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

[0.4.0]: https://github.com/AmaLS367/InvoiceFlowBot/compare/v0.3.0...v0.4.0
[0.3.0]: https://github.com/AmaLS367/InvoiceFlowBot/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/AmaLS367/InvoiceFlowBot/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/AmaLS367/InvoiceFlowBot/releases/tag/v0.1.0
