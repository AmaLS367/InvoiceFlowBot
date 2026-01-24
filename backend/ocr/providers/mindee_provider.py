from __future__ import annotations

from backend.ocr.engine.types import ExtractionResult
from backend.ocr.engine.util import get_logger
from backend.ocr.mindee_client import extract_invoice_mindee
from backend.ocr.providers.base import OcrProvider


class MindeeOcrProvider(OcrProvider):
    def __init__(self) -> None:
        self.logger = get_logger("ocr.provider.mindee")

    def extract_invoice(
        self,
        pdf_path: str,
        fast: bool = True,
        max_pages: int = 12,
    ) -> ExtractionResult:
        self.logger.info(
            f"[PROVIDER] Mindee extract start path={pdf_path} fast={fast} max_pages={max_pages}"
        )

        result = extract_invoice_mindee(pdf_path)

        self.logger.info(
            f"[PROVIDER] Mindee extract done doc_id={result.document_id} items={len(result.items)} "
            f"total={result.total_sum}"
        )

        return result
