from __future__ import annotations

from abc import ABC, abstractmethod

from ocr.engine.types import ExtractionResult


class OcrProvider(ABC):
    """
    Base interface for OCR providers that can extract invoices.
    """

    @abstractmethod
    def extract_invoice(
        self,
        pdf_path: str,
        fast: bool = True,
        max_pages: int = 12,
    ) -> ExtractionResult:
        """
        Run invoice extraction for a given PDF or image and return a parsed result.

        Args:
            pdf_path: Path to the PDF or image file to process.
            fast: Whether to use fast processing mode (provider-specific).
            max_pages: Maximum number of pages to process (provider-specific).

        Returns:
            ExtractionResult containing extracted invoice data.
        """
        raise NotImplementedError("extract_invoice must be implemented by subclasses.")

