from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from threading import Lock
from typing import TYPE_CHECKING, cast

from backend.ocr.engine.types import ExtractionResult, PageInfo
from backend.ocr.engine.util import file_sha256
from backend.ocr.providers.base import OcrProvider
from backend.ocr.providers.local_invoice import invoice_fields, invoice_items

if TYPE_CHECKING:
    from docling.document_converter import DocumentConverter

_CONVERSION_LOCK = Lock()


@lru_cache(maxsize=1)
def _converter(languages: str) -> DocumentConverter:
    from docling.datamodel.accelerator_options import AcceleratorDevice, AcceleratorOptions
    from docling.datamodel.base_models import InputFormat
    from docling.datamodel.pipeline_options import (
        PdfPipelineOptions,
        TableFormerMode,
        TableStructureOptions,
        TesseractCliOcrOptions,
    )
    from docling.document_converter import DocumentConverter, ImageFormatOption, PdfFormatOption

    options = PdfPipelineOptions(
        accelerator_options=AcceleratorOptions(device=AcceleratorDevice.CPU),
        document_timeout=120,
        enable_remote_services=False,
        ocr_options=TesseractCliOcrOptions(lang=languages.split("+")),
        table_structure_options=TableStructureOptions(mode=TableFormerMode.ACCURATE),
    )
    return DocumentConverter(
        allowed_formats=[InputFormat.PDF, InputFormat.IMAGE],
        format_options={
            InputFormat.PDF: PdfFormatOption(pipeline_options=options),
            InputFormat.IMAGE: ImageFormatOption(pipeline_options=options),
        },
    )


def _read_first_page(source: Path, languages: str, is_pdf: bool) -> str:
    from PIL import Image, ImageOps
    from pypdfium2 import PdfDocument
    from pytesseract import image_to_string

    if not is_pdf:
        with Image.open(source) as image:
            return cast(
                str, image_to_string(ImageOps.exif_transpose(image), lang=languages, timeout=30)
            )

    pdf = PdfDocument(source)
    try:
        page = pdf[0]
        # The native text layer is already available to Docling. OCR only scanned pages.
        if page.get_textpage().get_text_bounded().strip():
            return ""
        scale = min(3.0, 2500 / max(page.get_size()))
        image = page.render(scale=scale).to_pil()
        return cast(str, image_to_string(image, lang=languages, timeout=30))
    finally:
        pdf.close()


class LocalOcrProvider(OcrProvider):
    def __init__(self, languages: str = "eng+rus") -> None:
        self.languages = languages

    def extract_invoice(
        self,
        pdf_path: str,
        fast: bool = True,
        max_pages: int = 12,
    ) -> ExtractionResult:
        from docling.datamodel.base_models import ConversionStatus, InputFormat
        from docling_core.types.doc import TextItem
        from pypdfium2 import PdfiumError

        if max_pages < 1:
            raise ValueError("max_pages must be positive")

        source = Path(pdf_path)
        # Reuse the models and bound concurrent CPU and memory use across uploads.
        with _CONVERSION_LOCK:
            conversion = _converter(self.languages).convert(
                source, page_range=(1, max_pages), raises_on_error=False
            )
            if conversion.status not in {
                ConversionStatus.SUCCESS,
                ConversionStatus.PARTIAL_SUCCESS,
            }:
                details = "; ".join(error.error_message for error in conversion.errors)
                raise RuntimeError(f"Docling conversion failed: {details or conversion.status}")

            document = conversion.document
            lines = [
                line
                for item, _ in document.iterate_items()
                if isinstance(item, TextItem)
                for line in item.text.splitlines()
            ]
            items = []
            for table in document.tables:
                page_no = table.prov[0].page_no if table.prov else None
                rows = [[cell.text for cell in row] for row in table.data.grid]
                items.extend(invoice_items(rows, page_no))
                # Docling may group header fields and totals into two-column tables.
                lines.extend(f"{row[0]}: {row[1]}" for row in rows if len(row) == 2)

            fields = invoice_fields(lines)
            warnings = [error.error_message for error in conversion.errors]
            if len(fields) < 5 or not fast:
                # Whole-page OCR can recover header rows split into separate layout blocks.
                try:
                    text = _read_first_page(
                        source, self.languages, conversion.input.format == InputFormat.PDF
                    )
                except (OSError, RuntimeError, PdfiumError) as exc:
                    warnings.append(f"local: could not reread the first page: {exc}")
                else:
                    fields.update(invoice_fields(text.splitlines()))
        if conversion.input.page_count > max_pages:
            warnings.append(f"local: only the first {max_pages} pages were processed")
        if not fields and not items:
            warnings.append("local: no invoice fields or line items recognized")

        return ExtractionResult(
            document_id=file_sha256(pdf_path),
            doc_number=_text_field(fields, "doc_number"),
            supplier=_text_field(fields, "supplier"),
            client=_text_field(fields, "client"),
            date=_text_field(fields, "date"),
            total_sum=_amount_field(fields),
            template="local",
            extractor_version="local@1",
            pages=[
                PageInfo(
                    page_no=number, width=round(page.size.width), height=round(page.size.height)
                )
                for number, page in sorted(document.pages.items())
            ],
            items=items,
            warnings=warnings,
            provider="local",
        )


def _text_field(fields: dict[str, str | float], name: str) -> str | None:
    value = fields.get(name)
    return value if isinstance(value, str) else None


def _amount_field(fields: dict[str, str | float]) -> float | None:
    value = fields.get("total_sum")
    return value if isinstance(value, float) else None
