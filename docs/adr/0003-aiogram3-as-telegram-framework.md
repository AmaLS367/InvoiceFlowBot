# ADR 0003 - aiogram 3 as Telegram framework

## Status

Accepted

## Context

InvoiceFlowBot is a Telegram bot with:

- many handlers and callback flows

- async I/O (OCR, storage, HTTP)

- need for middlewares and dependency injection

We need a framework that is:

- fully async

- actively maintained

- has good support for typing and modern Python

## Decision

We use **aiogram 3** as the Telegram framework:

- All handlers are defined in `handlers/*`.

- Routers and middlewares are used to structure updates.

- Dependency injection is integrated through `core.container.AppContainer` and a custom middleware.

## Consequences

Positive:

- Strong async story and good integration with httpx and aiosqlite.

- Clear router and middleware model.

- Type hints and mypy friendly patterns.

Negative:

- aiogram 3 is still evolving, breaking changes between versions are possible.

- Developer must learn aiogram specifics.

Mitigations:

- Telegram specific code is isolated in the `handlers` layer.

- Business logic in `services` and `domain` is framework agnostic.
