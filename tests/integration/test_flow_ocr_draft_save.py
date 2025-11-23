"""
Integration test for the full business flow: OCR → Draft → Save → Query.

This test verifies the complete flow without Telegram layer, using:
- Real AsyncInvoiceStorage with migrated database
- Fake OCR provider
- Real service instances
"""
from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import List

import pytest

from core.container import AppContainer
from domain.drafts import InvoiceDraft
from ocr.engine.types import ExtractionResult, Item
from tests.fakes.fake_ocr import FakeOcr

pytestmark = pytest.mark.storage_db


def _get_fake_ocr(container: AppContainer) -> FakeOcr:
    """Helper to extract FakeOcr instance from container."""
    # The OCR is wrapped in a function, so we need to access it through invoice_service
    # We'll get it from the container's _ocr_extractor which is a function
    # For testing, we'll need to configure the FakeOcr through the container
    # Since we can't easily extract it, we'll configure it via the container's ocr_extractor
    # Actually, we need to store a reference to FakeOcr in the container or access it differently
    # For now, we'll use a workaround: configure the FakeOcr before creating the container
    # But since the container is created in the fixture, we need another approach
    # Let's store the FakeOcr in the container as an attribute
    if hasattr(container, "_fake_ocr"):
        return container._fake_ocr  # type: ignore[attr-defined]
    # If not available, we'll need to configure it differently
    # For this test, we'll configure the OCR result directly via the extractor function
    raise RuntimeError("FakeOcr not accessible from container")


@pytest.mark.asyncio
async def test_full_flow_ocr_draft_save_and_query(
    integration_flow_container: AppContainer,
) -> None:
    """Test the complete flow: OCR → Draft → Save → Query."""
    container = integration_flow_container

    user_id = 123
    file_path = "test_invoice.pdf"

    # Step 1: Configure OCR to return a predictable result
    # We need to configure the FakeOcr's next_result
    # Since we can't easily access it, we'll patch the extractor function
    # Actually, let's create a custom extractor that returns our test data
    expected_items: List[Item] = [
        Item(
            code="SKU-001",
            name="Item 1",
            qty=2.0,
            price=10.0,
            total=20.0,
        ),
        Item(
            code="SKU-002",
            name="Item 2",
            qty=1.0,
            price=5.0,
            total=5.0,
        ),
    ]

    expected_extraction_result = ExtractionResult(
        document_id="test-doc-id",
        supplier="Flow supplier",
        client="Flow customer",
        date="2025-07-01",
        total_sum=25.0,
        template="mindee",
        items=expected_items,
        pages=[],
        warnings=[],
    )

    # Create a custom extractor function that returns our test result
    async def test_extractor(pdf_path: str, fast: bool = True, max_pages: int = 12) -> ExtractionResult:
        return expected_extraction_result

    # Replace the extractor in the container
    container.invoice_service._ocr_extractor = test_extractor  # type: ignore[attr-defined]

    # Step 2: Process file through OCR (simulate file upload)
    invoice = await container.invoice_service.process_invoice_file(
        pdf_path=file_path,
        fast=True,
        max_pages=12,
    )

    # Verify invoice was created from OCR
    assert invoice is not None
    assert invoice.header.supplier_name == "Flow supplier"
    assert invoice.header.customer_name == "Flow customer"
    assert invoice.header.total_amount == Decimal("25.0")
    assert len(invoice.items) == 2
    assert invoice.items[0].description == "Item 1"
    assert invoice.items[0].quantity == Decimal("2.0")
    assert invoice.items[0].unit_price == Decimal("10.0")
    assert invoice.items[0].line_total == Decimal("20.0")

    # Step 3: Create draft (as handlers do)
    draft = InvoiceDraft(
        invoice=invoice,
        path=file_path,
        raw_text="",
        comments=[],
    )
    await container.draft_service.set_current_draft(user_id=user_id, draft=draft)

    # Verify draft was saved
    loaded_draft = await container.draft_service.get_current_draft(user_id)
    assert loaded_draft is not None
    assert loaded_draft.invoice.header.supplier_name == "Flow supplier"
    assert len(loaded_draft.invoice.items) == 2

    # Step 4: Save invoice to database (as handlers do when user clicks "Save")
    invoice_to_save = loaded_draft.invoice
    invoice_id = await container.invoice_service.save_invoice(invoice_to_save, user_id=user_id)

    # Verify invoice was saved
    assert invoice_id > 0

    # Clear draft after saving
    await container.draft_service.clear_current_draft(user_id)

    # Verify draft was cleared
    cleared_draft = await container.draft_service.get_current_draft(user_id)
    assert cleared_draft is None

    # Step 5: Query invoices from database (as handlers do when listing invoices)
    # Query by date range that includes our invoice date
    from_date = date(2025, 7, 1)
    to_date = date(2025, 7, 31)
    invoices = await container.invoice_service.list_invoices(
        from_date=from_date,
        to_date=to_date,
        supplier=None,
    )

    # Verify invoice was retrieved
    assert len(invoices) >= 1

    # Find our invoice by supplier name
    loaded_invoice = next(
        (inv for inv in invoices if inv.header.supplier_name == "Flow supplier"),
        None,
    )
    assert loaded_invoice is not None

    # Step 6: Verify all fields match
    assert loaded_invoice.header.supplier_name == "Flow supplier"
    assert loaded_invoice.header.customer_name == "Flow customer"
    assert loaded_invoice.header.total_amount == Decimal("25.0")

    assert len(loaded_invoice.items) == 2
    assert loaded_invoice.items[0].description == "Item 1"
    assert loaded_invoice.items[0].sku == "SKU-001"
    assert loaded_invoice.items[0].quantity == Decimal("2.0")
    assert loaded_invoice.items[0].unit_price == Decimal("10.0")
    assert loaded_invoice.items[0].line_total == Decimal("20.0")

    assert loaded_invoice.items[1].description == "Item 2"
    assert loaded_invoice.items[1].sku == "SKU-002"
    assert loaded_invoice.items[1].quantity == Decimal("1.0")
    assert loaded_invoice.items[1].unit_price == Decimal("5.0")
    assert loaded_invoice.items[1].line_total == Decimal("5.0")

