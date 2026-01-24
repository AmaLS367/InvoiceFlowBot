from datetime import date
from decimal import Decimal
from typing import List

import pytest

from backend.domain.invoices import Invoice, InvoiceHeader, InvoiceItem, InvoiceSourceInfo
from backend.services.invoice_service import InvoiceService


class DummyItem:
    def __init__(
        self,
        name: str,
        code: str,
        qty: float,
        price: float,
        total: float,
    ) -> None:
        self.name = name
        self.code = code
        self.qty = qty
        self.price = price
        self.total = total


class DummyExtractionResult:
    def __init__(
        self,
        supplier: str,
        client: str,
        invoice_date: str,
        total_sum: float,
        items: List[DummyItem],
        document_id: str = "dummy-doc-id",
    ) -> None:
        self.supplier = supplier
        self.client = client
        self.date = invoice_date
        self.total_sum = total_sum
        self.items = items
        self.document_id = document_id
        self.template = None
        self.score = None


@pytest.mark.asyncio
async def test_process_invoice_file_builds_invoice_from_ocr() -> None:
    import logging

    called = {}

    async def fake_extract_invoice_async(
        pdf_path: str, fast: bool = True, max_pages: int = 12
    ) -> DummyExtractionResult:
        called["pdf_path"] = pdf_path
        called["fast"] = fast
        called["max_pages"] = max_pages
        items = [
            DummyItem(name="Item 1", code="SKU1", qty=2.0, price=10.50, total=21.00),
            DummyItem(name="Item 2", code="SKU2", qty=1.0, price=100.00, total=100.00),
        ]
        return DummyExtractionResult(
            supplier="Test Supplier",
            client="Test Customer",
            invoice_date="2024-01-02",
            total_sum=121.00,
            items=items,
        )

    async def fake_save_invoice_func(invoice: Invoice, user_id: int = 0) -> int:
        return 0

    async def fake_fetch_invoices_func(
        from_date: date | None,
        to_date: date | None,
        supplier: str | None = None,
    ) -> List[Invoice]:
        return []

    service = InvoiceService(
        ocr_extractor=fake_extract_invoice_async,
        save_invoice_func=fake_save_invoice_func,
        fetch_invoices_func=fake_fetch_invoices_func,
        logger=logging.getLogger("test"),
    )

    invoice = await service.process_invoice_file(
        pdf_path="tests/data/sample.pdf",
        fast=False,
        max_pages=5,
    )

    assert isinstance(invoice, Invoice)
    assert invoice.header.supplier_name == "Test Supplier"
    assert invoice.header.customer_name == "Test Customer"
    assert invoice.header.total_amount == Decimal("121.00")
    assert len(invoice.items) == 2
    assert invoice.items[0].description == "Item 1"
    assert invoice.items[0].sku == "SKU1"
    assert invoice.items[0].quantity == Decimal("2")
    assert invoice.items[0].unit_price == Decimal("10.50")
    assert invoice.items[0].line_total == Decimal("21.00")
    assert called["pdf_path"] == "tests/data/sample.pdf"
    assert called["fast"] is False
    assert called["max_pages"] == 5


def test_build_invoice_from_extraction():
    """Test build_invoice_from_extraction function."""
    from backend.services.invoice_service import build_invoice_from_extraction

    result = DummyExtractionResult(
        supplier="Test Supplier",
        client="Test Client",
        invoice_date="2025-01-15",
        total_sum=100.0,
        items=[
            DummyItem(name="Item 1", code="SKU-1", qty=2.0, price=25.0, total=50.0),
        ],
    )

    invoice = build_invoice_from_extraction(result)

    assert invoice.header.supplier_name == "Test Supplier"
    assert invoice.header.customer_name == "Test Client"
    assert invoice.header.total_amount == Decimal("100.0")
    assert len(invoice.items) == 1
    assert invoice.items[0].description == "Item 1"
    assert invoice.items[0].sku == "SKU-1"
    assert invoice.source is not None
    assert invoice.source.provider == "mindee"


def test_build_invoice_from_extraction_with_none_values():
    """Test build_invoice_from_extraction with None values."""
    from backend.services.invoice_service import build_invoice_from_extraction

    result = DummyExtractionResult(
        supplier=None,
        client=None,
        invoice_date=None,
        total_sum=None,
        items=[],
    )

    invoice = build_invoice_from_extraction(result)

    assert invoice.header.supplier_name is None
    assert invoice.header.customer_name is None
    assert invoice.header.invoice_date is None
    assert invoice.header.total_amount is None
    assert len(invoice.items) == 0


def test_parse_date_function():
    """Test _parse_date helper function."""
    from backend.services.invoice_service import _parse_date

    # Test ISO format
    result = _parse_date("2025-01-15")
    assert result == date(2025, 1, 15)

    # Test DD.MM.YYYY format
    result = _parse_date("15.01.2025")
    assert result == date(2025, 1, 15)

    # Test None
    result = _parse_date(None)
    assert result is None

    # Test empty string
    result = _parse_date("")
    assert result is None

    # Test invalid format
    result = _parse_date("invalid")
    assert result is None


def test_build_header_function():
    """Test _build_header helper function."""
    from backend.ocr.engine.types import ExtractionResult
    from backend.services.invoice_service import _build_header

    result = ExtractionResult(
        document_id="test",
        supplier="Supplier",
        client="Client",
        date="2025-01-15",
        total_sum=100.0,
        template="test",
        items=[],
        pages=[],
        warnings=[],
    )

    header = _build_header(result)
    assert header.supplier_name == "Supplier"
    assert header.customer_name == "Client"
    assert header.invoice_date == date(2025, 1, 15)
    assert header.total_amount == Decimal("100.0")


def test_build_item_function():
    """Test _build_item helper function."""
    from backend.ocr.engine.types import Item
    from backend.services.invoice_service import _build_item

    item = Item(code="SKU-1", name="Item 1", qty=2.0, price=25.0, total=50.0, page_no=1)
    invoice_item = _build_item(item)

    assert invoice_item.description == "Item 1"
    assert invoice_item.sku == "SKU-1"
    assert invoice_item.quantity == Decimal("2.0")
    assert invoice_item.unit_price == Decimal("25.0")
    assert invoice_item.line_total == Decimal("50.0")


@pytest.mark.asyncio
async def test_save_invoice_delegates_to_storage() -> None:
    import logging

    captured = {}

    async def fake_extract_invoice_async(
        pdf_path: str, fast: bool = True, max_pages: int = 12
    ) -> DummyExtractionResult:
        return DummyExtractionResult(
            supplier="", client="", invoice_date="", total_sum=0.0, items=[]
        )

    async def fake_save_invoice_domain_async(invoice: Invoice, user_id: int = 0) -> int:
        captured["invoice"] = invoice
        captured["user_id"] = user_id
        return 42

    async def fake_fetch_invoices_func(
        from_date: date | None,
        to_date: date | None,
        supplier: str | None = None,
    ) -> List[Invoice]:
        return []

    service = InvoiceService(
        ocr_extractor=fake_extract_invoice_async,
        save_invoice_func=fake_save_invoice_domain_async,
        fetch_invoices_func=fake_fetch_invoices_func,
        logger=logging.getLogger("test"),
    )

    header = InvoiceHeader(
        supplier_name="Test Supplier",
        customer_name="Test Customer",
        invoice_number="INV-1",
        invoice_date=date(2024, 1, 2),
        total_amount=Decimal("121.00"),
        currency="USD",
    )

    items = [
        InvoiceItem(
            description="Item 1",
            sku="SKU1",
            quantity=Decimal("2"),
            unit_price=Decimal("10.50"),
            line_total=Decimal("21.00"),
            currency="USD",
        )
    ]

    source = InvoiceSourceInfo(
        file_path="tests/data/sample.pdf",
        file_sha256="dummy-hash",
        provider="mindee",
        raw_payload_path=None,
    )

    invoice = Invoice(
        header=header,
        items=items,
        comments=[],
        source=source,
    )

    invoice_id = await service.save_invoice(invoice, user_id=123)

    assert invoice_id == 42
    assert "invoice" in captured
    assert captured["invoice"] is invoice
    assert captured["user_id"] == 123


@pytest.mark.asyncio
async def test_list_invoices_delegates_to_storage() -> None:
    import logging

    captured = {}

    async def fake_extract_invoice_async(
        pdf_path: str, fast: bool = True, max_pages: int = 12
    ) -> DummyExtractionResult:
        return DummyExtractionResult(
            supplier="", client="", invoice_date="", total_sum=0.0, items=[]
        )

    async def fake_save_invoice_func(invoice: Invoice, user_id: int = 0) -> int:
        return 0

    header = InvoiceHeader(
        supplier_name="Supplier A",
        customer_name="Customer A",
        invoice_number="INV-1",
        invoice_date=date(2024, 1, 2),
        total_amount=Decimal("100.00"),
        currency="USD",
    )

    invoice = Invoice(
        header=header,
        items=[],
        comments=[],
        source=None,
    )

    async def fake_fetch_invoices_domain_async(
        from_date: date | None,
        to_date: date | None,
        supplier: str | None = None,
    ) -> List[Invoice]:
        captured["from_date"] = from_date
        captured["to_date"] = to_date
        captured["supplier"] = supplier
        return [invoice]

    service = InvoiceService(
        ocr_extractor=fake_extract_invoice_async,
        save_invoice_func=fake_save_invoice_func,
        fetch_invoices_func=fake_fetch_invoices_domain_async,
        logger=logging.getLogger("test"),
    )

    from_date = date(2024, 1, 1)
    to_date = date(2024, 1, 31)
    supplier = "Supplier A"

    invoices = await service.list_invoices(
        from_date=from_date,
        to_date=to_date,
        supplier=supplier,
    )

    assert invoices == [invoice]
    assert captured["from_date"] == from_date
    assert captured["to_date"] == to_date
    assert captured["supplier"] == supplier
