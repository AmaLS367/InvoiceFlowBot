from __future__ import annotations

from abc import ABC, abstractmethod

from ocr.engine.types import ExtractionResult


class OcrProvider(ABC):
    @abstractmethod
    def extract_invoice(
        self,
        pdf_path: str,
        fast: bool = True,
        max_pages: int = 12,
    ) -> ExtractionResult:
        raise NotImplementedError("extract_invoice must be implemented by subclasses.")
