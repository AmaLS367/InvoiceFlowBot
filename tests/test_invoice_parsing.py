from datetime import date
from decimal import Decimal

import pytest

from backend.handlers import utils
from backend.ocr.engine.router import _result_payload
from backend.ocr.engine.types import ExtractionResult, Item, PageInfo


def test_result_payload_transforms_dataclasses():
    result = ExtractionResult(
        document_id="doc-1",
        supplier="Acme Inc.",
        client="Client LLC",
        date="2024-10-10",
        total_sum=199.99,
        template="custom",
        score=0.95,
        extractor_version="engine@test",
        items=[
            Item(code="SKU-1", name="Widget", qty=2, price=25.5, total=51.0, page_no=1),
            Item(code=None, name="Service", qty=1, price=148.99, total=148.99, page_no=2),
        ],
        pages=[
            PageInfo(
                page_no=1,
                width=800,
                height=1200,
                header_text="Invoice 1",
                template="tpl-a",
                score=0.88,
            ),
            PageInfo(
                page_no=2,
                width=800,
                height=1200,
                header_text="Invoice 2",
                template="tpl-a",
                score=0.90,
            ),
        ],
        warnings=["missing_tax"],
    )

    payload = _result_payload(result)

    assert payload["document_id"] == "doc-1"
    assert payload["items"][0]["name"] == "Widget"
    assert payload["items"][1]["code"] is None
    assert payload["pages"][0]["width"] == 800
    assert payload["pages"][1]["header_text"] == "Invoice 2"
    assert payload["warnings"] == ["missing_tax"]


def test_format_money_normalizes_numbers():
    assert utils.format_money(25) == "25"
    assert utils.format_money("25.500") == "25.5"
    assert utils.format_money("10.00") == "10"
    assert utils.format_money("not-a-number") == "not-a-number"


def test_fmt_items_and_csv_output():
    items = [
        {"code": "SKU-1", "name": "Widget", "qty": 2, "price": 25.5, "total": 51},
        {"code": "", "name": "Service", "qty": 1, "price": 148.99, "total": 148.99},
    ]

    formatted = utils.fmt_items(items)
    assert "1. [SKU-1] Widget" in formatted
    assert "Кол-во: 2" in formatted
    assert "Сумма: 51" in formatted

    csv_content = utils.csv_bytes(items).decode("utf-8-sig")
    assert "#;name;qty;price;total" in csv_content
    assert "Widget" in csv_content
    assert "Service" in csv_content


def test_format_invoice_summary():
    """Test format_invoice_summary function."""
        from backend.domain.invoices import Invoice, InvoiceHeader

    header = InvoiceHeader(
        subtotal=Decimal("90.00"),
        tax_amount=Decimal("10.00"),
        total_amount=Decimal("100.00"),
        currency="USD",
    )
    invoice = Invoice(header=header)

    summary = utils.format_invoice_summary(invoice)
    assert "Подытог: 90" in summary
    assert "НДС: 10" in summary
    assert "Итого: 100" in summary
    assert "Валюта: USD" in summary


def test_format_invoice_summary_empty():
    """Test format_invoice_summary with empty values."""
        from backend.domain.invoices import Invoice, InvoiceHeader

    header = InvoiceHeader()
    invoice = Invoice(header=header)

    summary = utils.format_invoice_summary(invoice)
    assert summary == ""


def test_csv_bytes_from_items():
    """Test csv_bytes_from_items function."""
        from backend.domain.invoices import InvoiceItem

    items = [
        InvoiceItem(
            description="Item 1",
            quantity=Decimal("2"),
            unit_price=Decimal("25.50"),
            line_total=Decimal("51.00"),
        ),
        InvoiceItem(
            description="Item 2",
            quantity=Decimal("1"),
            unit_price=Decimal("10.00"),
            line_total=Decimal("10.00"),
        ),
    ]

    csv_data = utils.csv_bytes_from_items(items)
    csv_content = csv_data.decode("utf-8-sig")
    assert "#;name;qty;price;total" in csv_content
    assert "Item 1" in csv_content
    assert "Item 2" in csv_content
    assert "2" in csv_content
    assert "25.5" in csv_content


def test_format_invoice_items_empty():
    """Test format_invoice_items with empty list."""
        from backend.domain.invoices import InvoiceItem

    items: list[InvoiceItem] = []
    result = utils.format_invoice_items(items)
    assert result == "Позиции не распознаны."


def test_format_invoice_items_with_items():
    """Test format_invoice_items with items."""
        from backend.domain.invoices import InvoiceItem

    items = [
        InvoiceItem(
            description="Test Item",
            sku="SKU-001",
            quantity=Decimal("2"),
            unit_price=Decimal("25.00"),
            line_total=Decimal("50.00"),
        ),
    ]

    result = utils.format_invoice_items(items)
    assert "Test Item" in result
    assert "SKU-001" in result
    assert "Кол-во: 2" in result


def test_format_invoice_full():
    """Test format_invoice_full function."""
        from backend.domain.invoices import Invoice, InvoiceHeader, InvoiceItem

    header = InvoiceHeader(
        supplier_name="Supplier",
        customer_name="Customer",
        invoice_number="INV-001",
        invoice_date=date(2025, 1, 15),
        total_amount=Decimal("100.00"),
    )
    items = [
        InvoiceItem(
            description="Item 1",
            quantity=Decimal("2"),
            unit_price=Decimal("25.00"),
            line_total=Decimal("50.00"),
        ),
    ]
    invoice = Invoice(header=header, items=items)

    full_text = utils.format_invoice_full(invoice)
    assert "Supplier" in full_text
    assert "Customer" in full_text
    assert "INV-001" in full_text
    assert "Item 1" in full_text


def test_main_kb():
    """Test main_kb function."""
    kb = utils.main_kb()
    assert kb is not None
    assert len(kb.inline_keyboard) > 0


def test_actions_kb():
    """Test actions_kb function."""
    kb = utils.actions_kb()
    assert kb is not None
    assert len(kb.inline_keyboard) > 0


def test_header_kb():
    """Test header_kb function."""
    kb = utils.header_kb()
    assert kb is not None
    assert len(kb.inline_keyboard) > 0


def test_item_fields_kb():
    """Test item_fields_kb function."""
    kb = utils.item_fields_kb(1)
    assert kb is not None
    assert len(kb.inline_keyboard) > 0


def test_items_index_kb():
    """Test items_index_kb function."""
    kb = utils.items_index_kb(10, 1)
    assert kb is not None
    assert len(kb.inline_keyboard) > 0


@pytest.mark.asyncio
async def test_send_chunked():
    """Test send_chunked function."""
    from tests.fakes.fake_telegram import FakeMessage

    message = FakeMessage()
    long_text = "A" * 5000  # Longer than MAX_MSG (4000)

    await utils.send_chunked(message, long_text)

    # Should send multiple messages
    assert len(message.answers) >= 2


def test_fmt_header():
    """Test fmt_header function."""
    header_dict = {
        "supplier": "Test Supplier",
        "client": "Test Client",
        "date": "2025-01-15",
        "doc_number": "INV-001",
        "total_sum": 100.0,
    }

    result = utils.fmt_header(header_dict)
    assert "Test Supplier" in result
    assert "Test Client" in result
    assert "INV-001" in result


def test_fmt_header_with_none_values():
    """Test fmt_header with None values."""
    header_dict = {
        "supplier": None,
        "client": None,
        "date": None,
        "doc_number": None,
        "total_sum": None,
    }

    result = utils.fmt_header(header_dict)
    assert "—" in result  # Should show dashes for None values


def test_format_invoice_header_with_none():
    """Test format_invoice_header with None values."""
        from backend.domain.invoices import Invoice, InvoiceHeader

    header = InvoiceHeader()
    invoice = Invoice(header=header)

    result = utils.format_invoice_header(invoice)
    assert "—" in result  # Should show dashes for None values


def test_items_index_kb_pagination():
    """Test items_index_kb with pagination."""
    kb = utils.items_index_kb(25, 2, per_page=10)
    assert kb is not None
    # Should have navigation buttons for page 2
    assert len(kb.inline_keyboard) > 0


def test_items_index_kb_first_page():
    """Test items_index_kb on first page."""
    kb = utils.items_index_kb(10, 1, per_page=5)
    assert kb is not None
    # Should not have previous button on first page
    assert len(kb.inline_keyboard) > 0
