from types import SimpleNamespace
from unittest.mock import Mock, patch

from docling.datamodel.base_models import ConversionStatus, InputFormat
from docling_core.types.doc import DocItemLabel, DoclingDocument, Size, TableCell, TableData
from PIL import Image

from backend.ocr.providers.local_invoice import InvoiceTableReader, invoice_fields, invoice_items
from backend.ocr.providers.local_provider import LocalOcrProvider


def test_invoice_fields_parse_labels_and_currency():
    assert invoice_fields(
        [
            "Счёт №АБ-012",
            "Поставщик:",
            "ООО Ромашка",
            "Покупатель: Компания Тест",
            "Дата счёта: 18.11.2026",
            "Подытог: 1 000,00",
            "К оплате: 700,00",
            "Итого с НДС: 1 200,50 ₽",
        ]
    ) == {
        "doc_number": "АБ-012",
        "supplier": "ООО Ромашка",
        "client": "Компания Тест",
        "date": "2026-11-18",
        "total_sum": 1200.50,
    }

    assert invoice_fields(["INVOICE #INV-001", "Total Due $1,245.50"]) == {
        "doc_number": "INV-001",
        "total_sum": 1245.50,
    }


def test_invoice_items_skip_totals_and_allow_repeated_headers():
    header = ["Артикул", "Наименование", "Кол-во", "Цена", "Сумма"]
    items = invoice_items(
        [header, ["A1", "Бумага", "2,5", "200,00", "500,00"], header, ["", "Итого", "", "", "500"]],
        page_no=2,
    )

    assert len(items) == 1
    assert (items[0].code, items[0].name, items[0].qty, items[0].price, items[0].total) == (
        "A1",
        "Бумага",
        2.5,
        200.0,
        500.0,
    )
    assert items[0].page_no == 2


def test_local_pdf_result_maps_docling_tables_and_limits_pages(tmp_path):
    path = tmp_path / "invoice.pdf"
    path.touch()
    document = DoclingDocument(name="invoice")
    document.add_page(page_no=1, size=Size(width=600, height=800))
    document.add_text(DocItemLabel.TEXT, "Invoice #INV-123\nInvoice Date: 2026-11-18")
    cells = [
        TableCell(
            text=text,
            row_span=1,
            col_span=1,
            start_row_offset_idx=row,
            end_row_offset_idx=row + 1,
            start_col_offset_idx=col,
            end_col_offset_idx=col + 1,
        )
        for row, values in enumerate([["Description", "Qty", "Unit Price"], ["Paper", "2", "3.50"]])
        for col, text in enumerate(values)
    ]
    document.add_table(TableData(num_rows=2, num_cols=3, table_cells=cells))
    converter = Mock()
    converter.convert.return_value = SimpleNamespace(
        document=document,
        input=SimpleNamespace(format=InputFormat.PDF, page_count=4),
        status=ConversionStatus.SUCCESS,
        errors=[],
    )

    with (
        patch("backend.ocr.providers.local_provider._converter", return_value=converter),
        patch("backend.ocr.providers.local_provider._read_first_page", return_value=""),
    ):
        result = LocalOcrProvider().extract_invoice(str(path), max_pages=1)

    converter.convert.assert_called_once_with(path, page_range=(1, 1), raises_on_error=False)
    assert result.provider == "local"
    assert result.doc_number == "INV-123"
    assert result.date == "2026-11-18"
    assert result.pages[0].height == 800
    assert result.items[0].total == 7
    assert result.warnings == ["local: only the first 1 pages were processed"]


def test_photo_can_recover_missing_fields_with_pytesseract(tmp_path):
    path = tmp_path / "invoice.png"
    Image.new("RGB", (10, 10), "white").save(path)
    converter = Mock()
    converter.convert.return_value = SimpleNamespace(
        document=DoclingDocument(name="invoice"),
        input=SimpleNamespace(format=InputFormat.IMAGE, page_count=1),
        status=ConversionStatus.SUCCESS,
        errors=[],
    )

    with (
        patch("backend.ocr.providers.local_provider._converter", return_value=converter),
        patch("pytesseract.image_to_string", return_value="Invoice #INV-001\nTotal: $42") as ocr,
    ):
        result = LocalOcrProvider("eng").extract_invoice(str(path))

    assert ocr.call_args.kwargs["lang"] == "eng"
    assert result.doc_number == "INV-001"
    assert result.total_sum == 42


def test_accounting_brackets_are_negative_amounts():
    header = ["No.", "SKU", "Description", "Qty", "Unit Price", "Discount", "Line Total"]
    items = invoice_items(
        [
            header,
            ["1", "CR-2101", "Circuit breaker", "3", "(201.97)", "5%", "(575.61)"],
            ["2", "CR-2102", "Busbar connector", "4", "-213.84", "10%", "-769.82"],
            ["3", "CR-2106", "Thermal fuse", "8", "0.00", "10%", "0.00"],
        ],
        page_no=1,
    )

    assert [(item.code, item.price, item.total) for item in items] == [
        ("CR-2101", -201.97, -575.61),
        ("CR-2102", -213.84, -769.82),
        ("CR-2106", 0.0, 0.0),
    ]
    assert invoice_fields(["Subtotal: USD (21,459.98)", "Grand Total: USD (25,751.98)"]) == {
        "total_sum": -25751.98
    }


def test_headers_with_units_and_wrapped_descriptions():
    items = invoice_items(
        [
            [
                "No.",
                "SKU",
                "Description",
                "Qty (pcs)",
                "Unit Price (USD)",
                "Disc. %",
                "Line Total (USD)",
            ],
            ["7", "NP-1707", "Hose connector / Series 27", "8", "31,52", "15%", "214,34"],
            ["", "", "Quality inspection certificate included", "", "", "", ""],
            ["8", "NP-1708", "Valve housing / Series 28", "9", "33,39", "0%", "300,51"],
            ["", "", "Items continued on the next page.", "", "", "", ""],
        ],
        page_no=1,
    )

    assert [(item.code, item.name, item.qty, item.price, item.total) for item in items] == [
        (
            "NP-1707",
            "Hose connector / Series 27 Quality inspection certificate included",
            8.0,
            31.52,
            214.34,
        ),
        ("NP-1708", "Valve housing / Series 28", 9.0, 33.39, 300.51),
    ]


def test_table_continues_on_next_page_without_repeated_header():
    reader = InvoiceTableReader()
    reader.add_table(
        [
            ["No.", "SKU", "Description", "Qty", "Unit Price", "Line Total"],
            ["1", "CT-2101", "Circuit breaker", "3", "201.97", "605.91"],
        ],
        page_no=1,
    )
    reader.add_table([["Subtotal:", "USD 605.91"]], page_no=1)
    reader.add_table([["2", "CT-2123", "Control module", "5", "463.11", "2,315.55"]], page_no=2)

    assert [(item.code, item.page_no) for item in reader.items] == [
        ("CT-2101", 1),
        ("CT-2123", 2),
    ]


def test_line_total_is_checked_against_discount_and_flagged():
    reader = InvoiceTableReader()
    reader.add_table(
        [
            ["SKU", "Description", "Qty", "Unit Price", "Discount", "Line Total"],
            ["NP-1773", "Bearing kit", "8", "154.94", "5%", ""],
            ["NP-1701", "Bearing kit", "2", "20.30", "5%", "38.57"],
            ["MX-2124", "DIN rail terminal", "15", "474.98", "", "712.47"],
            ["NP-1702", "Seal assembly", "3", "22.11", "10%", "59.86"],
        ],
        page_no=4,
    )

    assert [(item.code, item.total, item.review) for item in reader.items] == [
        ("NP-1773", 1177.54, ["total_computed"]),
        ("NP-1701", 38.57, []),
        ("MX-2124", 712.47, ["qty_corrected"]),
        ("NP-1702", 59.86, ["total_mismatch"]),
    ]


def test_label_column_is_paired_with_value_column():
    # OCR of a totals box can list all labels first and all values after them.
    assert invoice_fields(
        [
            "Subtotal:",
            "Freight:",
            "VAT 20%:",
            "Grand Total:",
            "USD 52,044.07",
            "USD 47.50",
            "USD 10,418.31",
            "USD 62,509.88",
        ]
    ) == {"total_sum": 62509.88}


def test_unreadable_headings_are_inferred_from_cell_contents():
    reader = InvoiceTableReader()
    reader.add_table(
        [
            ["", "", "Description", "", "Unit Price", "Discount", "Line Total"],
            ["1", "NP-1701", "Bearing kit", "2", "20.30", "5%", "38.57"],
            ["2", "NP-1702", "Seal assembly", "3", "22.17", "10%", "59.86"],
        ],
        page_no=1,
    )
    reader.add_table(
        [
            ["No.", "SKU", "Description", "Qty", "Unit Price", "Discount", "пе Total"],
            ["73", "NP-1773", "Bearing kit", "8", "154.94", "5%", "1,177.54"],
        ],
        page_no=4,
    )

    assert [(item.code, item.qty, item.total, item.review) for item in reader.items] == [
        ("NP-1701", 2.0, 38.57, []),
        ("NP-1702", 3.0, 59.86, []),
        ("NP-1773", 8.0, 1177.54, []),
    ]


def test_scanned_quantity_without_decimal_point_is_corrected_and_flagged():
    reader = InvoiceTableReader()
    reader.add_table(
        [
            ["No.", "SKU", "Description", "Qty", "Unit Price", "Line Total"],
            ["24", "MX-2124", "Earth clamp", "15", "474.98", "712.47"],
            ["25", "МХ-2125", "Circuit breaker", "7", "486.85", "3,407.95"],
            ["26", "MX-2126", "Busbar connector", "a)", "498.72", "3,989.76"],
            ["27", "MX-2127", "Pilot relay", "2", "184.86", "36972"],
            ["28", "MX-2128", "Pressure gauge", "4", "85.75)", "343.00"],
        ],
        page_no=2,
    )
    reader.finish()

    assert [
        (item.code, item.qty, item.price, item.total, item.review) for item in reader.items
    ] == [
        ("MX-2124", 1.5, 474.98, 712.47, ["qty_corrected"]),
        ("MX-2125", 7.0, 486.85, 3407.95, []),
        ("MX-2126", 8.0, 498.72, 3989.76, ["qty_computed"]),
        ("MX-2127", 2.0, 184.86, 369.72, ["total_corrected"]),
        ("MX-2128", 4.0, 85.75, 343.0, ["price_computed"]),
    ]
