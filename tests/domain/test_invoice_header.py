from datetime import date
from decimal import Decimal

from backend.domain.invoices import InvoiceHeader


def test_invoice_header_basic_creation() -> None:
    invoice_date = date(2024, 1, 15)
    header = InvoiceHeader(
        supplier_name="Test Supplier",
        customer_name="Test Customer",
        invoice_number="INV-001",
        invoice_date=invoice_date,
        currency="USD",
        total_amount=Decimal("123.45"),
    )

    assert header.supplier_name == "Test Supplier"
    assert header.customer_name == "Test Customer"
    assert header.invoice_number == "INV-001"
    assert header.invoice_date == invoice_date
    assert header.currency == "USD"
    assert header.total_amount == Decimal("123.45")

    assert isinstance(header.invoice_date, date)
    assert isinstance(header.total_amount, Decimal)


def test_invoice_header_defaults_are_none() -> None:
    header = InvoiceHeader()

    assert header.supplier_name is None
    assert header.supplier_tax_id is None
    assert header.customer_name is None
    assert header.customer_tax_id is None
    assert header.invoice_number is None
    assert header.invoice_date is None
    assert header.due_date is None
    assert header.currency is None
    assert header.subtotal is None
    assert header.tax_amount is None
    assert header.total_amount is None


def test_invoice_header_with_all_fields() -> None:
    invoice_date = date(2024, 1, 15)
    due_date = date(2024, 2, 15)
    header = InvoiceHeader(
        supplier_name="Supplier Inc",
        supplier_tax_id="TAX-12345",
        customer_name="Customer LLC",
        customer_tax_id="TAX-67890",
        invoice_number="INV-2024-001",
        invoice_date=invoice_date,
        due_date=due_date,
        currency="EUR",
        subtotal=Decimal("100.00"),
        tax_amount=Decimal("20.00"),
        total_amount=Decimal("120.00"),
    )

    assert header.supplier_name == "Supplier Inc"
    assert header.supplier_tax_id == "TAX-12345"
    assert header.customer_name == "Customer LLC"
    assert header.customer_tax_id == "TAX-67890"
    assert header.invoice_number == "INV-2024-001"
    assert header.invoice_date == invoice_date
    assert header.due_date == due_date
    assert header.currency == "EUR"
    assert header.subtotal == Decimal("100.00")
    assert header.tax_amount == Decimal("20.00")
    assert header.total_amount == Decimal("120.00")


def test_invoice_header_with_different_currencies() -> None:
    currencies = ["USD", "EUR", "GBP", "JPY", "RUB", "CNY"]
    for currency in currencies:
        header = InvoiceHeader(currency=currency, total_amount=Decimal("100"))
        assert header.currency == currency


def test_invoice_header_with_different_dates() -> None:
    dates = [
        date(2020, 1, 1),
        date(2024, 12, 31),
        date(2000, 6, 15),
    ]
    for invoice_date in dates:
        header = InvoiceHeader(invoice_date=invoice_date)
        assert header.invoice_date == invoice_date
        assert isinstance(header.invoice_date, date)


def test_invoice_header_with_unicode_characters() -> None:
    header = InvoiceHeader(
        supplier_name="ООО «Поставщик»",
        customer_name="Customer & Co. Ltd.",
        invoice_number="INV-№2024-001",
    )

    assert header.supplier_name == "ООО «Поставщик»"
    assert header.customer_name == "Customer & Co. Ltd."
    assert header.invoice_number == "INV-№2024-001"


def test_invoice_header_equality() -> None:
    date_val = date(2024, 1, 1)
    header1 = InvoiceHeader(
        supplier_name="Supplier",
        invoice_date=date_val,
        total_amount=Decimal("100"),
    )
    header2 = InvoiceHeader(
        supplier_name="Supplier",
        invoice_date=date_val,
        total_amount=Decimal("100"),
    )

    assert header1 == header2
