from datetime import date
from decimal import Decimal
from typing import List

import pytest

import storage.db as storage_db
from domain.invoices import Invoice, InvoiceHeader, InvoiceItem, InvoiceSourceInfo
from services import invoice_service


class DummyItem:
    """
    Minimal test double for an OCR line item.
    """

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
    """
    Minimal test double for an OCR extraction result.
    """

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
async def test_process_invoice_file_builds_invoice_from_ocr(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    process_invoice_file should call OCR router and convert the result into a domain Invoice.
    """
    called = {}

    def fake_extract_invoice(pdf_path: str, fast: bool = True, max_pages: int = 12) -> DummyExtractionResult:
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

    # Mock extract_invoice in the service module where it's imported
    monkeypatch.setattr(invoice_service, "extract_invoice", fake_extract_invoice)

    invoice = await invoice_service.process_invoice_file(
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


@pytest.mark.asyncio
async def test_save_invoice_delegates_to_storage(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    save_invoice should delegate persistence to storage.save_invoice_domain and return its ID.
    """
    captured = {}

    def fake_save_invoice_domain(invoice: Invoice, user_id: int = 0) -> int:
        captured["invoice"] = invoice
        captured["user_id"] = user_id
        return 42

    monkeypatch.setattr(storage_db, "save_invoice_domain", fake_save_invoice_domain)

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

    invoice_id = await invoice_service.save_invoice(invoice, user_id=123)

    assert invoice_id == 42
    assert "invoice" in captured
    assert captured["invoice"] is invoice
    assert captured["user_id"] == 123


@pytest.mark.asyncio
async def test_list_invoices_delegates_to_storage(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    list_invoices should delegate to storage.fetch_invoices_domain and return the result.
    """
    captured = {}

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

    def fake_fetch_invoices_domain(
        from_date: date | None,
        to_date: date | None,
        supplier: str | None = None,
    ) -> List[Invoice]:
        captured["from_date"] = from_date
        captured["to_date"] = to_date
        captured["supplier"] = supplier
        return [invoice]

    monkeypatch.setattr(storage_db, "fetch_invoices_domain", fake_fetch_invoices_domain)

    from_date = date(2024, 1, 1)
    to_date = date(2024, 1, 31)
    supplier = "Supplier A"

    invoices = await invoice_service.list_invoices(
        from_date=from_date,
        to_date=to_date,
        supplier=supplier,
    )

    assert invoices == [invoice]
    assert captured["from_date"] == from_date
    assert captured["to_date"] == to_date
    assert captured["supplier"] == supplier

