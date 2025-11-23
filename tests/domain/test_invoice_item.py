"""
Unit tests for InvoiceItem domain entity.
"""

from decimal import Decimal

from domain.invoices import InvoiceItem


def test_invoice_item_basic_creation() -> None:
    """
    InvoiceItem should be created with correct field values and types.
    """
    item = InvoiceItem(
        description="Test Item",
        sku="SKU-123",
        quantity=Decimal("5"),
        unit_price=Decimal("10.50"),
        line_total=Decimal("52.50"),
        currency="USD",
    )

    assert item.description == "Test Item"
    assert item.sku == "SKU-123"
    assert item.quantity == Decimal("5")
    assert item.unit_price == Decimal("10.50")
    assert item.line_total == Decimal("52.50")
    assert item.currency == "USD"

    assert isinstance(item.quantity, Decimal)
    assert isinstance(item.unit_price, Decimal)
    assert isinstance(item.line_total, Decimal)


def test_invoice_item_optional_fields_defaults() -> None:
    """
    Optional fields for InvoiceItem should default to None when not provided.
    """
    item = InvoiceItem(description="Minimal Item")

    assert item.description == "Minimal Item"
    assert item.sku is None
    assert item.currency is None
    assert item.quantity == Decimal("0")
    assert item.unit_price == Decimal("0")
    assert item.line_total == Decimal("0")


def test_invoice_item_with_zero_values() -> None:
    """
    InvoiceItem should handle zero quantity and prices correctly.
    """
    item = InvoiceItem(
        description="Free Item",
        quantity=Decimal("0"),
        unit_price=Decimal("0"),
        line_total=Decimal("0"),
    )

    assert item.quantity == Decimal("0")
    assert item.unit_price == Decimal("0")
    assert item.line_total == Decimal("0")
    assert isinstance(item.quantity, Decimal)
    assert isinstance(item.unit_price, Decimal)
    assert isinstance(item.line_total, Decimal)


def test_invoice_item_with_large_decimal_values() -> None:
    """
    InvoiceItem should handle large Decimal values correctly.
    """
    item = InvoiceItem(
        description="Expensive Item",
        quantity=Decimal("1000000"),
        unit_price=Decimal("999999.99"),
        line_total=Decimal("999999990000"),
    )

    assert item.quantity == Decimal("1000000")
    assert item.unit_price == Decimal("999999.99")
    assert item.line_total == Decimal("999999990000")


def test_invoice_item_with_precise_decimal_values() -> None:
    """
    InvoiceItem should preserve decimal precision correctly.
    """
    item = InvoiceItem(
        description="Precise Item",
        quantity=Decimal("1.23456789"),
        unit_price=Decimal("9.87654321"),
        line_total=Decimal("12.19326377"),
    )

    assert item.quantity == Decimal("1.23456789")
    assert item.unit_price == Decimal("9.87654321")
    assert item.line_total == Decimal("12.19326377")


def test_invoice_item_with_unicode_characters() -> None:
    """
    InvoiceItem should handle unicode characters in description and SKU.
    """
    item = InvoiceItem(
        description="Товар №1 / Item #1 / 商品 #1",
        sku="SKU-测试-тест-テスト",
        currency="USD",
    )

    assert item.description == "Товар №1 / Item #1 / 商品 #1"
    assert item.sku == "SKU-测试-тест-テスト"
    assert item.currency == "USD"


def test_invoice_item_equality() -> None:
    """
    InvoiceItem instances with same values should be equal (dataclass behavior).
    """
    item1 = InvoiceItem(
        description="Test",
        sku="SKU1",
        quantity=Decimal("1"),
        unit_price=Decimal("10"),
        line_total=Decimal("10"),
    )
    item2 = InvoiceItem(
        description="Test",
        sku="SKU1",
        quantity=Decimal("1"),
        unit_price=Decimal("10"),
        line_total=Decimal("10"),
    )

    assert item1 == item2
    assert item1.description == item2.description
    assert item1.sku == item2.sku
