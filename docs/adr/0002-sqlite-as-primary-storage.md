# ADR 0002 - SQLite as primary storage

## Status

Accepted

## Context

The bot stores invoices, drafts and comments. Requirements:

- simple deployment for small and single user instances

- low maintenance overhead

- transactional guarantees for inserts and updates

- compatibility with async access from Python

We do not need a full blown database cluster for the target use case.

## Decision

We use **SQLite** as the primary storage:

- Schema is managed through Alembic migrations (`alembic/`).

- The main async access layer is `storage/db_async.py` with `AsyncInvoiceStorage`.

- Domain mapping is implemented in `storage/mappers.py`.

## Consequences

Positive:

- Zero configuration database for local and small deployments.

- Simple backups (single file).

- Fits well into Docker images and CI.

Negative:

- Limited concurrency for heavy write workloads.

- No built in horizontal scaling.

- For multi tenant or high throughput SaaS we would need to move to PostgreSQL or similar.

Mitigations:

- Storage access is encapsulated in `AsyncInvoiceStorage`.

- Migration to a different backend is localized in the `storage` package.

