from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

import httpx

import config
from ocr.engine.types import ExtractionResult
from ocr.engine.util import get_logger
from ocr.mindee_client import build_extraction_result, mindee_struct_to_data

logger = get_logger("ocr.async_client")


async def _mindee_predict_async(pdf_path: str) -> Dict[str, Any]:
    """
    Call Mindee Invoices HTTP API asynchronously using httpx and return the raw JSON payload.
    """
    api_key = config.MINDEE_API_KEY
    if not api_key:
        logger.warning("[Mindee HTTP async] no API key in config")
        return {}

    url = "https://api.mindee.net/v1/products/mindee/invoices/v4/predict"
    pdf_file = Path(pdf_path)

    if not pdf_file.exists():
        raise FileNotFoundError(str(pdf_file))

    # We follow the same basic contract as mindee_predict: send file as 'document' form field.
    async with httpx.AsyncClient(timeout=60.0) as client:
        with pdf_file.open("rb") as f:
            response = await client.post(
                url,
                headers={"Authorization": f"Token {api_key}"},
                files={"document": ("document", f, "application/pdf")},
            )

    if response.status_code != 200:
        logger.warning(
            "[Mindee HTTP async] non-200 response status=%s body=%s",
            response.status_code,
            response.text[:500],
        )
        return {}

    try:
        payload = response.json()
    except json.JSONDecodeError:
        logger.warning(
            "[Mindee HTTP async] failed to decode JSON response body=%s",
            response.text[:500],
        )
        return {}

    if not isinstance(payload, dict):
        logger.warning(
            "[Mindee HTTP async] unexpected payload type=%s",
            type(payload),
        )
        return {}

    return payload


async def extract_invoice_async(
    pdf_path: str,
    fast: bool = True,
    max_pages: int = 12,
) -> ExtractionResult:
    """
    Asynchronous invoice extraction using Mindee HTTP API and the same normalization
    pipeline as the synchronous Mindee client.
    """
    logger.info(
        "[OCR ASYNC] extract_invoice_async start pdf_path=%r fast=%s max_pages=%s",
        pdf_path,
        fast,
        max_pages,
    )

    raw_payload = await _mindee_predict_async(pdf_path)

    if not raw_payload:
        # Mirror the behaviour of the sync client on failures: produce an "empty" payload with warnings.
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
        # Ensure we always have a warnings list
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
