from __future__ import annotations

import asyncio
from pathlib import Path

from backend.config import Settings, get_settings
from backend.ocr.engine.router import get_ocr_provider
from backend.ocr.engine.types import ExtractionResult


async def extract_invoice_async(
    pdf_path: str,
    fast: bool = True,
    max_pages: int = 12,
    *,
    settings: Settings | None = None,
) -> ExtractionResult:
    if not Path(pdf_path).is_file():
        raise FileNotFoundError(pdf_path)

    provider = get_ocr_provider(settings or get_settings())
    return await asyncio.to_thread(provider.extract_invoice, pdf_path, fast, max_pages)
