from __future__ import annotations

import os
import shutil
from typing import Any, Dict

from backend.config import ARTIFACTS_DIR, Settings, get_settings
from backend.ocr.engine.types import ExtractionResult
from backend.ocr.engine.util import ensure_dir, file_sha256, get_logger, time_block, write_json
from backend.ocr.providers.base import OcrProvider
from backend.ocr.providers.local_provider import LocalOcrProvider
from backend.ocr.providers.mindee_provider import MindeeOcrProvider

logger = get_logger("ocr.router")


def get_ocr_provider(settings: Settings) -> OcrProvider:
    if settings.OCR_PROVIDER == "mindee":
        return MindeeOcrProvider(settings.MINDEE_API_KEY, settings.MINDEE_MODEL_ID)
    return LocalOcrProvider(settings.OCR_LANGUAGES)


def _copy_source(pdf_path: str, dst_pdf: str) -> None:
    try:
        shutil.copyfile(pdf_path, dst_pdf)
    except Exception as e:
        logger.warning(f"[ROUTER] copy source failed: {e}")


def _result_payload(result: ExtractionResult) -> Dict[str, Any]:
    return {
        "document_id": result.document_id,
        "doc_number": result.doc_number,
        "provider": result.provider,
        "template": result.template,
        "score": result.score,
        "extractor_version": result.extractor_version,
        "supplier": result.supplier,
        "client": result.client,
        "date": result.date,
        "total_sum": result.total_sum,
        "items": [
            {
                "code": it.code,
                "name": it.name,
                "qty": it.qty,
                "price": it.price,
                "total": it.total,
                "page_no": it.page_no,
                "review": it.review,
            }
            for it in result.items
        ],
        "pages": [
            {
                "page_no": p.page_no,
                "width": p.width,
                "height": p.height,
                "header_text": p.header_text,
                "template": p.template,
                "score": p.score,
            }
            for p in result.pages
        ],
        "warnings": result.warnings,
        "review": result.review,
    }


def extract_invoice(pdf_path: str, fast: bool = True, max_pages: int = 12) -> ExtractionResult:
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(pdf_path)

    doc_id = file_sha256(pdf_path)
    settings = get_settings()
    provider = get_ocr_provider(settings)
    logger.info("[ROUTER] %s start path=%s doc_id=%s", settings.OCR_PROVIDER, pdf_path, doc_id)

    doc_dir = os.path.join(ARTIFACTS_DIR, doc_id)
    ensure_dir(doc_dir)

    dst_pdf = os.path.join(doc_dir, "source.pdf")
    if not os.path.exists(dst_pdf):
        _copy_source(pdf_path, dst_pdf)

    with time_block(logger, "router.extract_invoice"):
        result = provider.extract_invoice(
            pdf_path=pdf_path,
            fast=fast,
            max_pages=max_pages,
        )

    if not result.document_id:
        result.document_id = doc_id
    if not result.template:
        result.template = settings.OCR_PROVIDER

    write_json(os.path.join(doc_dir, "extraction.json"), _result_payload(result))

    logger.info(
        f"[ROUTER] {settings.OCR_PROVIDER} done doc_id={result.document_id} template={result.template} "
        f"score={result.score} items={len(result.items)} supplier={result.supplier}"
    )

    return result
