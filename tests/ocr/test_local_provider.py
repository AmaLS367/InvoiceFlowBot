from types import SimpleNamespace
from unittest.mock import Mock, patch

from docling.datamodel.base_models import ConversionStatus, InputFormat
from docling_core.types.doc import DocItemLabel, DoclingDocument, Size, TableCell, TableData
from PIL import Image

from backend.ocr.providers.local_invoice import invoice_fields, invoice_items
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
