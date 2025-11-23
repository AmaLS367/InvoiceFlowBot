from __future__ import annotations

from ocr.engine.types import ExtractionResult
from ocr.engine.util import get_logger
from ocr.mindee_client import extract_invoice_mindee
from ocr.providers.base import OcrProvider


class MindeeOcrProvider(OcrProvider):
    """
    OCR provider that delegates invoice extraction to the Mindee client.
    """

    def __init__(self) -> None:
        self.logger = get_logger("ocr.provider.mindee")

    def extract_invoice(
        self,
        pdf_path: str,
        fast: bool = True,
        max_pages: int = 12,
    ) -> ExtractionResult:
        """
        Extract invoice data using Mindee.

        The fast and max_pages parameters are accepted for API compatibility,
        but the current Mindee client does not use them directly.
        """
        self.logger.info(
            f"[PROVIDER] Mindee extract start path={pdf_path} fast={fast} max_pages={max_pages}"
        )

        # Current Mindee client ignores fast and max_pages.
        result = extract_invoice_mindee(pdf_path)

        self.logger.info(
            f"[PROVIDER] Mindee extract done doc_id={result.document_id} items={len(result.items)} "
            f"total={result.total_sum}"
        )

        return result
