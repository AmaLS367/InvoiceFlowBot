from __future__ import annotations

import os
from typing import Any, Dict, List

from ocr.engine.router import extract_invoice
from ocr.engine.types import ExtractionResult
from ocr.engine.util import get_logger, time_block

logger = get_logger("ocr.extract")


def parse_invoice_text(pdf_path: str, fast: bool = True, max_pages: int = 12) -> Dict[str, Any]:
    # Start and file metadata
    try:
        size = os.path.getsize(pdf_path) if os.path.exists(pdf_path) else -1
    except Exception:
        size = -1
    logger.info(f"[EXTRACT] start path={pdf_path} size={size} fast={fast} max_pages={max_pages}")

    # Call router with timing and error handling
    try:
        with time_block(logger, "router.extract_invoice"):
            result: ExtractionResult = extract_invoice(
                pdf_path=pdf_path, fast=fast, max_pages=max_pages
            )
    except Exception:
        logger.exception(f"[EXTRACT] failed path={pdf_path}")
        raise

    # Transform results
    items_out: List[Dict[str, Any]] = []
    for it in result.items:
        items_out.append(
            {
                "code": it.code,
                "name": it.name,
                "qty": it.qty,
                "price": it.price,
                "total": it.total,
                "page_no": it.page_no,
            }
        )

    out: Dict[str, Any] = {
        "document_id": result.document_id,
        "supplier": result.supplier,
        "client": result.client,
        "date": result.date,
        "total_sum": result.total_sum,
        "template": result.template,
        "score": result.score,
        "extractor_version": result.extractor_version,
        "items": items_out,
        "pages": [
            {
                "page_no": p.page_no,
                "width": p.width,
                "height": p.height,
                "template": p.template,
                "score": p.score,
            }
            for p in result.pages
        ],
        "warnings": result.warnings,
    }

    # Summary and useful WARN/DEBUG logs
    pages_cnt = len(result.pages or [])
    logger.info(
        f"[EXTRACT] done id={out.get('document_id')} template={out.get('template')} "
        f"score={out.get('score')} items={len(items_out)} pages={pages_cnt} supplier={out.get('supplier')}"
    )
    if out.get("warnings"):
        logger.warning(f"[EXTRACT] warnings={out['warnings']}")
    if not items_out:
        logger.warning("[EXTRACT] no_items_detected")

    # Short preview for debugging
    try:
        preview_names = [i["name"] for i in items_out[:3]]
        logger.debug(f"[EXTRACT] items_preview={preview_names}")
        pages_preview = [{"no": p["page_no"], "score": p["score"]} for p in out["pages"][:3]]
        logger.debug(f"[EXTRACT] pages_preview={pages_preview}")
    except Exception:
        pass

    return out


def extract(pdf_path: str, *args, **kwargs) -> Dict[str, Any]:
    return parse_invoice_text(pdf_path, *args, **kwargs)
