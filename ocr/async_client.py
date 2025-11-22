from __future__ import annotations

from ocr.engine.router import extract_invoice
from ocr.engine.types import ExtractionResult
from ocr.engine.util import get_logger
from services.async_utils import run_blocking_io

logger = get_logger("ocr.async_client")


async def extract_invoice_async(
    pdf_path: str,
    fast: bool = True,
    max_pages: int = 12,
) -> ExtractionResult:
    """
    Async facade over the synchronous OCR router extract_invoice function.

    This function wraps the blocking OCR extraction in an executor to allow
    non-blocking execution in async contexts.

    Args:
        pdf_path: Path to the PDF file to extract invoice data from.
        fast: Whether to use fast extraction mode (default: True).
        max_pages: Maximum number of pages to process (default: 12).

    Returns:
        ExtractionResult containing the extracted invoice data.
    """
    logger.info(
        f"[OCR ASYNC] extract_invoice_async pdf_path={pdf_path!r} fast={fast} max_pages={max_pages}"
    )

    result = await run_blocking_io(
        extract_invoice,
        pdf_path,
        fast,
        max_pages,
    )

    return result


__all__ = ["extract_invoice_async"]

