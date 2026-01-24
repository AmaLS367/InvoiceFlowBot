# ADR 0004 - Backend folder structure

## Status

Accepted

## Context

The InvoiceFlowBot project started with a flat structure where all Python modules were in the root directory:

- `core/`, `domain/`, `handlers/`, `ocr/`, `services/`, `storage/` at the root level
- `config.py`, `bot.py`, `healthcheck.py` at the root level
- `alembic/` and `alembic.ini` at the root level

This structure worked for a single-service Telegram bot, but as the project grows:

- The root directory becomes cluttered with many folders and files
- It's unclear what belongs to the backend vs. other potential components (frontend, shared libraries, etc.)
- Future expansion with a frontend or additional services would require restructuring anyway

We want a clean, scalable structure that:
- Separates backend code from configuration and infrastructure files
- Makes it clear where application code lives
- Allows for future expansion (e.g., `frontend/`, `shared/`, etc.)
- Maintains Python package structure for proper imports

## Decision

We move all backend Python code into a `backend/` directory:

- All application modules: `backend/core/`, `backend/domain/`, `backend/handlers/`, `backend/ocr/`, `backend/services/`, `backend/storage/`
- Configuration files: `backend/config.py`, `backend/healthcheck.py`
- Database migrations: `backend/alembic/`, `backend/alembic.ini`
- Entry point `bot.py` remains at the root for simplicity

All imports are updated to use the `backend.*` prefix:
- `from config import ...` → `from backend.config import ...`
- `from core.container import ...` → `from backend.core.container import ...`
- And so on for all modules

## Consequences

Positive:

- Clean root directory with clear separation of concerns
- Scalable structure ready for frontend or additional services
- Clear namespace for backend code (`backend.*`)
- Better organization for larger projects

Negative:

- All imports need to be updated (60-70 files affected)
- Configuration files (Dockerfile, pyproject.toml, CI workflows) need updates
- Alembic configuration needs adjustment for new paths
- Initial refactoring effort required

Mitigations:

- All imports are updated systematically in a single refactoring pass
- Configuration files are updated to reflect new structure
- Tests are updated to use new import paths
- Documentation is updated to reflect new structure
