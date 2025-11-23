"""
Fake OCR functions for testing.
"""
from __future__ import annotations

from typing import Any

from ocr.engine.types import ExtractionResult


class FakeOcr:
    """
    Fake OCR that records all calls and returns minimal valid responses.
    """

    def __init__(self) -> None:
        self.calls: list[tuple[str, tuple[Any, ...], dict[str, Any]]] = []

    async def extract_invoice_async(
        self,
        pdf_path: str,
        fast: bool = True,
        max_pages: int = 12,
    ) -> ExtractionResult:
        """Fake extract invoice function."""
        self.calls.append(("extract_invoice_async", (pdf_path, fast, max_pages), {}))
        # Return minimal valid ExtractionResult
        return ExtractionResult(
            document_id="fake-doc-id",
            supplier=None,
            client=None,
            date=None,
            total_sum=None,
            template="fake",
            items=[],
            pages=[],
            warnings=[],
        )


# Create callable function that delegates to FakeOcr instance


def make_fake_ocr_extractor(fake_ocr: FakeOcr) -> Any:
    """Create a callable that delegates to fake_ocr.extract_invoice_async."""

    async def fake_extract_invoice(
        pdf_path: str,
        fast: bool = True,
        max_pages: int = 12,
    ) -> ExtractionResult:
        return await fake_ocr.extract_invoice_async(pdf_path, fast, max_pages)

    return fake_extract_invoice


__all__ = [
    "FakeOcr",
    "make_fake_ocr_extractor",
]

