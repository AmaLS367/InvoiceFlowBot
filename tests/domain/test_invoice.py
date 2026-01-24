"""
Unit tests for Invoice domain entity.
"""

from datetime import date
from decimal import Decimal

from backend.domain.invoices import (
    Invoice,
    InvoiceComment,
    InvoiceHeader,
    InvoiceItem,
    InvoiceSourceInfo,
)


def test_invoice_creation_with_header_and_items() -> None:
    """
    Invoice should aggregate header, items and source correctly.
    """
    header = InvoiceHeader(
        supplier_name="Test Supplier",
        customer_name="Test Customer",
        invoice_number="INV-1",
        invoice_date=date(2024, 1, 1),
        total_amount=Decimal("123.45"),
        currency="USD",
    )

    items = [
        InvoiceItem(
            description="Item 1",
            sku="SKU1",
            quantity=Decimal("2"),
            unit_price=Decimal("10"),
            line_total=Decimal("20"),
            currency="USD",
        ),
        InvoiceItem(
            description="Item 2",
            sku="SKU2",
            quantity=Decimal("1"),
            unit_price=Decimal("100"),
            line_total=Decimal("100"),
            currency="USD",
        ),
    ]

    source = InvoiceSourceInfo(
        file_path="/tmp/invoice.pdf",
        file_sha256="abc123",
        provider="mindee",
        raw_payload_path="/tmp/invoice.json",
    )

    invoice = Invoice(
        header=header,
        items=items,
        comments=[],
        source=source,
    )

    assert invoice.header is header
    assert len(invoice.items) == 2
    assert invoice.items[0].description == "Item 1"
    assert invoice.items[1].description == "Item 2"
    assert invoice.source is not None
    assert invoice.source.provider == "mindee"
    assert len(invoice.comments) == 0


def test_invoice_defaults_empty_lists() -> None:
    """
    Invoice should have empty lists for items and comments by default.
    """
    header = InvoiceHeader()
    invoice = Invoice(header=header)

    assert invoice.items == []
    assert invoice.comments == []
    assert invoice.source is None


def test_invoice_total_items_method() -> None:
    """
    Invoice.total_items should return the number of items.
    """
    header = InvoiceHeader()
    items = [
        InvoiceItem(description="Item 1"),
        InvoiceItem(description="Item 2"),
        InvoiceItem(description="Item 3"),
    ]
    invoice = Invoice(header=header, items=items)

    assert invoice.total_items() == 3

    empty_invoice = Invoice(header=header, items=[])
    assert empty_invoice.total_items() == 0


def test_invoice_has_items_method() -> None:
    """
    Invoice.has_items should return True if there are items, False otherwise.
    """
    header = InvoiceHeader()

    invoice_with_items = Invoice(
        header=header,
        items=[InvoiceItem(description="Item 1")],
    )
    assert invoice_with_items.has_items() is True

    invoice_without_items = Invoice(header=header, items=[])
    assert invoice_without_items.has_items() is False


def test_invoice_with_comments() -> None:
    """
    Invoice should store and retrieve comments correctly.
    """
    header = InvoiceHeader()
    comments = [
        InvoiceComment(message="First comment", author="User1"),
        InvoiceComment(message="Second comment", author="User2"),
    ]
    invoice = Invoice(header=header, comments=comments)

    assert len(invoice.comments) == 2
    assert invoice.comments[0].message == "First comment"
    assert invoice.comments[1].message == "Second comment"
    assert invoice.comments[0].author == "User1"
    assert invoice.comments[1].author == "User2"


def test_invoice_with_many_items() -> None:
    """
    Invoice should handle large number of items correctly.
    """
    header = InvoiceHeader()
    items = [InvoiceItem(description=f"Item {i}", quantity=Decimal(str(i))) for i in range(1, 101)]
    invoice = Invoice(header=header, items=items)

    assert invoice.total_items() == 100
    assert invoice.has_items() is True
    assert len(invoice.items) == 100
    assert invoice.items[0].description == "Item 1"
    assert invoice.items[99].description == "Item 100"


def test_invoice_with_many_comments() -> None:
    """
    Invoice should handle large number of comments correctly.
    """
    header = InvoiceHeader()
    comments = [InvoiceComment(message=f"Comment {i}", author=f"User{i}") for i in range(1, 51)]
    invoice = Invoice(header=header, comments=comments)

    assert len(invoice.comments) == 50
    assert invoice.comments[0].message == "Comment 1"
    assert invoice.comments[49].message == "Comment 50"
    assert invoice.comments[0].author == "User1"
    assert invoice.comments[49].author == "User50"


def test_invoice_with_empty_strings() -> None:
    """
    Invoice entities should handle empty strings correctly.
    """
    header = InvoiceHeader(
        supplier_name="",
        customer_name="",
        invoice_number="",
    )
    item = InvoiceItem(description="", sku="")
    Invoice(header=header, items=[item])

    assert header.supplier_name == ""
    assert header.customer_name == ""
    assert header.invoice_number == ""
    assert item.description == ""
    assert item.sku == ""


def test_invoice_with_mixed_currencies() -> None:
    """
    Invoice should handle items with different currencies.
    """
    header = InvoiceHeader(currency="USD")
    items = [
        InvoiceItem(description="USD Item", currency="USD", line_total=Decimal("10")),
        InvoiceItem(description="EUR Item", currency="EUR", line_total=Decimal("20")),
        InvoiceItem(description="No Currency", line_total=Decimal("30")),
    ]
    invoice = Invoice(header=header, items=items)

    assert invoice.items[0].currency == "USD"
    assert invoice.items[1].currency == "EUR"
    assert invoice.items[2].currency is None


def test_invoice_with_partial_header_fields() -> None:
    header = InvoiceHeader(
        supplier_name="Supplier",
        total_amount=Decimal("100"),
    )
    invoice = Invoice(header=header)

    assert invoice.header.supplier_name == "Supplier"
    assert invoice.header.total_amount == Decimal("100")
    assert invoice.header.customer_name is None
    assert invoice.header.invoice_number is None
    assert invoice.header.invoice_date is None


def test_invoice_with_source_info_combinations() -> None:
    header = InvoiceHeader()

    source1 = InvoiceSourceInfo(provider="mindee")
    invoice1 = Invoice(header=header, source=source1)
    assert invoice1.source is not None
    assert invoice1.source.provider == "mindee"
    assert invoice1.source.file_path is None

    source2 = InvoiceSourceInfo(file_path="/tmp/invoice.pdf")
    invoice2 = Invoice(header=header, source=source2)
    assert invoice2.source is not None
    assert invoice2.source.file_path == "/tmp/invoice.pdf"
    assert invoice2.source.provider is None

    source3 = InvoiceSourceInfo(file_sha256="abc123")
    invoice3 = Invoice(header=header, source=source3)
    assert invoice3.source is not None
    assert invoice3.source.file_sha256 == "abc123"
