from __future__ import annotations

import os
import shutil
from typing import Dict, Any

from ocr.engine.types import ExtractionResult
from ocr.engine.util import file_sha256, ensure_dir, write_json, get_logger, time_block
from ocr.providers.base import OcrProvider
from ocr.providers.mindee_provider import MindeeOcrProvider
from config import ARTIFACTS_DIR


logger = get_logger("ocr.router")

# For now the router always uses the Mindee provider.
# The provider instance is kept at module level to allow future extension.
_default_provider: OcrProvider = MindeeOcrProvider()


def _copy_source(pdf_path: str, dst_pdf: str) -> None:
    try:
        shutil.copyfile(pdf_path, dst_pdf)
    except Exception as e:
        logger.warning(f"[ROUTER] copy source failed: {e}")


def _result_payload(result: ExtractionResult) -> Dict[str, Any]:
    return {
        "document_id": result.document_id,
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
    }


def extract_invoice(pdf_path: str, fast: bool = True, max_pages: int = 12) -> ExtractionResult:
    # Parameters fast and max_pages are kept for API compatibility but not used
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(pdf_path)

    doc_id = file_sha256(pdf_path)
    logger.info(f"[ROUTER] mindee start path={pdf_path} doc_id={doc_id}")

    doc_dir = os.path.join(ARTIFACTS_DIR, doc_id)
    ensure_dir(doc_dir)

    dst_pdf = os.path.join(doc_dir, "source.pdf")
    if not os.path.exists(dst_pdf):
        _copy_source(pdf_path, dst_pdf)

    with time_block(logger, "router.mindee_extract"):
        result = _default_provider.extract_invoice(
            pdf_path=pdf_path,
            fast=fast,
            max_pages=max_pages,
        )

    if not result.document_id:
        result.document_id = doc_id
    if not result.template:
        result.template = "mindee"
    if result.score is None or result.score == 0.0:
        result.score = 1.0 if result.items else 0.4

    write_json(os.path.join(doc_dir, "extraction.json"), _result_payload(result))

    logger.info(
        f"[ROUTER] mindee done doc_id={result.document_id} template={result.template} "
        f"score={result.score} items={len(result.items)} supplier={result.supplier}"
    )

    return result

