from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Any, Dict

from ocr.engine.types import ExtractionResult
from ocr.engine.util import get_logger
from ocr.mindee_client import (
    build_extraction_result,
    mindee_predict,
    mindee_predict_sdk,
    mindee_struct_to_data,
)

logger = get_logger("ocr.async_client")


async def _mindee_predict_async(pdf_path: str) -> Dict[str, Any]:
    pdf_file = Path(pdf_path)
    if not pdf_file.exists():
        raise FileNotFoundError(str(pdf_file))

    # Use the official SDK (same as sync path) to avoid URL/version mismatches.
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None

    def _do_predict() -> Dict[str, Any]:
        resp = mindee_predict_sdk(str(pdf_file)) or mindee_predict(str(pdf_file))
        return resp or {}

    if loop:
        return await loop.run_in_executor(None, _do_predict)
    return _do_predict()


async def extract_invoice_async(
    pdf_path: str,
    fast: bool = True,
    max_pages: int = 12,
) -> ExtractionResult:
    logger.info(
        "[OCR ASYNC] extract_invoice_async start pdf_path=%r fast=%s max_pages=%s",
        pdf_path,
        fast,
        max_pages,
    )

    raw_payload = await _mindee_predict_async(pdf_path)

    if not raw_payload:
        data: Dict[str, Any] = {
            "supplier": None,
            "client": None,
            "doc_number": None,
            "date": None,
            "items": [],
            "total_sum": None,
            "status": "empty",
            "warnings": ["mindee async: payload is empty or invalid"],
        }
    else:
        data = mindee_struct_to_data(raw_payload)
        if "warnings" not in data or data["warnings"] is None:
            data["warnings"] = []
        elif not isinstance(data["warnings"], list):
            data["warnings"] = [str(data["warnings"])]

    result = build_extraction_result(
        data=data,
        pdf_path=pdf_path,
        template_name="mindee",
    )

    logger.info(
        "[OCR ASYNC] extract_invoice_async done items=%s total_sum=%s supplier=%r client=%r",
        len(result.items),
        result.total_sum,
        result.supplier,
        result.client,
    )

    return result


__all__ = ["extract_invoice_async"]
