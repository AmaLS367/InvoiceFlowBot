"""
Tests for AppContainer dependency injection.
"""
from __future__ import annotations

import logging

from config import Settings
from core.container import AppContainer, create_app_container
from ocr.async_client import extract_invoice_async
from services.draft_service import DraftService
from services.invoice_service import InvoiceService
from storage.db_async import fetch_invoices_domain_async, save_invoice_domain_async
from storage.drafts_async import delete_draft_invoice, load_draft_invoice, save_draft_invoice
from tests.fakes.fake_ocr import FakeOcr, make_fake_ocr_extractor
from tests.fakes.fake_storage import (
    FakeStorage,
    make_fake_delete_draft_func,
    make_fake_fetch_invoices_func,
    make_fake_load_draft_func,
    make_fake_save_draft_func,
    make_fake_save_invoice_func,
)


def test_app_container_creates_default_dependencies() -> None:
    """Test that AppContainer creates default dependencies when none are provided."""
    config = Settings()  # type: ignore[call-arg]
    container = AppContainer(config=config)

    assert isinstance(container.invoice_service, InvoiceService)
    assert isinstance(container.draft_service, DraftService)

    # Check that services use the default functions
    assert container.invoice_service._ocr_extractor is extract_invoice_async
    assert container.invoice_service._save_invoice_func is save_invoice_domain_async
    assert container.invoice_service._fetch_invoices_func is fetch_invoices_domain_async
    assert container.draft_service._load_draft_func is load_draft_invoice
    assert container.draft_service._save_draft_func is save_draft_invoice
    assert container.draft_service._delete_draft_func is delete_draft_invoice


def test_app_container_accepts_overridden_dependencies() -> None:
    """Test that AppContainer accepts overridden dependencies."""
    config = Settings()  # type: ignore[call-arg]
    fake_storage = FakeStorage()
    fake_ocr = FakeOcr()

    container = AppContainer(
        config=config,
        ocr_extractor=make_fake_ocr_extractor(fake_ocr),
        save_invoice_func=make_fake_save_invoice_func(fake_storage),
        fetch_invoices_func=make_fake_fetch_invoices_func(fake_storage),
        load_draft_func=make_fake_load_draft_func(fake_storage),
        save_draft_func=make_fake_save_draft_func(fake_storage),
        delete_draft_func=make_fake_delete_draft_func(fake_storage),
    )

    assert isinstance(container.invoice_service, InvoiceService)
    assert isinstance(container.draft_service, DraftService)

    # Check that services use the fake functions
    assert container.invoice_service._ocr_extractor is not extract_invoice_async
    assert container.invoice_service._save_invoice_func is not save_invoice_domain_async
    assert container.invoice_service._fetch_invoices_func is not fetch_invoices_domain_async
    assert container.draft_service._load_draft_func is not load_draft_invoice
    assert container.draft_service._save_draft_func is not save_draft_invoice
    assert container.draft_service._delete_draft_func is not delete_draft_invoice


def test_app_container_accepts_overridden_services() -> None:
    """Test that AppContainer accepts pre-constructed service instances."""
    config = Settings()  # type: ignore[call-arg]
    fake_storage = FakeStorage()
    fake_ocr = FakeOcr()

    invoice_service = InvoiceService(
        ocr_extractor=make_fake_ocr_extractor(fake_ocr),
        save_invoice_func=make_fake_save_invoice_func(fake_storage),
        fetch_invoices_func=make_fake_fetch_invoices_func(fake_storage),
        logger=logging.getLogger("test.invoice"),
    )

    draft_service = DraftService(
        load_draft_func=make_fake_load_draft_func(fake_storage),
        save_draft_func=make_fake_save_draft_func(fake_storage),
        delete_draft_func=make_fake_delete_draft_func(fake_storage),
        logger=logging.getLogger("test.draft"),
    )

    container = AppContainer(
        config=config,
        invoice_service=invoice_service,
        draft_service=draft_service,
    )

    assert container.invoice_service is invoice_service
    assert container.draft_service is draft_service


def test_create_app_container_returns_default_container() -> None:
    """Test that create_app_container returns a container with default dependencies."""
    container = create_app_container()

    assert isinstance(container, AppContainer)
    assert isinstance(container.invoice_service, InvoiceService)
    assert isinstance(container.draft_service, DraftService)
    assert container.config is not None

