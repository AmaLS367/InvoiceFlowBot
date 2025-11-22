import json
import os
from typing import Any, Dict, List, Optional, cast

import requests
from mindee import ClientV2, InferenceParameters

import config
from ocr.engine.types import ExtractionResult, Item
from ocr.engine.util import file_sha256, get_logger

MINDEE_API = config.MINDEE_API_KEY
MODEL_ID_MINDEE = config.MINDEE_MODEL_ID

logger = get_logger("ocr.mindee")


def _field_value(field: Any) -> Optional[Any]:
    if isinstance(field, dict):
        return field.get("value")
    return None


def mindee_predict(path: str) -> Optional[dict]:
    """
    Simple HTTP call to Mindee Invoices v4 endpoint.
    """
    api = MINDEE_API
    if not api:
        logger.warning("[Mindee HTTP] no API key in env")
        return None
    try:
        url = "https://api.mindee.net/v1/products/mindee/invoices/v4/predict"
        with open(path, "rb") as f:
            r = requests.post(
                url,
                headers={"Authorization": f"Token {api}"},
                files={"document": f},
                timeout=60,
            )
        r.raise_for_status()
        return r.json()
    except Exception:
        logger.exception(f"[Mindee] request failed for file {path}")
        return None


def mindee_predict_sdk(path: str) -> Optional[dict]:
    api = MINDEE_API
    model_id = MODEL_ID_MINDEE
    if not api or not model_id:
        logger.warning("[Mindee ClientV2] no API key or model id in env")
        return None
    try:
        client = ClientV2(api_key=api)
        params = InferenceParameters(model_id=model_id, rag=False)
        src = client.source_from_path(path)
        res = client.enqueue_and_get_inference(src, params)

        # Debug dump of raw response
        os.makedirs("logs", exist_ok=True)
        raw_json = getattr(res, "to_json", None)
        if callable(raw_json):
            raw_str = cast(str, raw_json())
        else:
            raw_str = json.dumps(res, default=lambda o: getattr(o, "__dict__", str(o)))
        raw = json.loads(raw_str)
        with open("logs/mindee_v2_debug.json", "w", encoding="utf-8") as f:
            json.dump(raw, f, ensure_ascii=False, indent=2)

        # Normalize fields into prediction structure
        inf = raw.get("inference") or raw.get("document", {}).get("inference") or raw
        pages = inf.get("pages") if isinstance(inf, dict) else None

        prediction: Dict[str, Any] = {}
        if isinstance(inf, dict) and "fields" in inf and isinstance(inf["fields"], list):
            for fld in inf["fields"]:
                name = (fld.get("name") or "").lower()
                val = fld.get("value") if "value" in fld else (fld.get("values") or None)
                if name:
                    prediction[name] = val

        flds = None
        if isinstance(inf, dict):
            flds = inf.get("result", {}).get("fields")
            if not flds and isinstance(inf.get("fields"), dict):
                flds = inf.get("fields")

        if isinstance(flds, dict) and flds:
            def _v(key):
                x = flds.get(key)
                return x.get("value") if isinstance(x, dict) else None

            prediction = {
                "supplier":       {"value": _v("supplier_name")},
                "customer":       {"value": (_v("customer_id") or _v("customer_name"))},
                "invoice_number": {"value": _v("invoice_number")},
                "invoice_date":   {"value": _v("date")},
                "total_amount":   {"value": _v("total_amount")},
            }

            items_norm: List[Dict[str, Any]] = []
            li = flds.get("line_items") or {}
            for it in (li.get("items") or []):
                fields_map = it.get("fields", {})
                product_code = _field_value(fields_map.get("product_code"))
                description = _field_value(fields_map.get("description"))
                quantity = _field_value(fields_map.get("quantity"))
                unit_price = _field_value(fields_map.get("unit_price"))
                total_price = _field_value(fields_map.get("total_price"))
                total_amount = _field_value(fields_map.get("total_amount"))
                items_norm.append({
                    "product_code": {"value": product_code},
                    "description":  {"value": description},
                    "quantity":     {"value": quantity},
                    "unit_price":   {"value": unit_price},
                    "total_amount": {"value": (total_price or total_amount)},
                })
            prediction["line_items"] = items_norm

        if pages and isinstance(pages, list) and pages and "prediction" in pages[0]:
            packed = {"document": {"inference": {"pages": pages}}}
        else:
            packed = {"document": {"inference": {"pages": [{"prediction": prediction}]}}}

        return packed
    except Exception:
        logger.exception(f"[Mindee ClientV2] inference failed for file {path}")
        return None


def extract_text_mindee(path: str) -> str:
    resp = mindee_predict_sdk(path) or mindee_predict(path)
    if not resp:
        return ""
    return "<<MINDEE_STRUCT>>\n" + json.dumps(resp, ensure_ascii=False)


def mindee_struct_to_data(raw: Dict[str, Any]) -> Dict[str, Any]:
    def _extract_prediction(payload: Dict[str, Any]) -> Dict[str, Any]:
        try:
            return payload["document"]["inference"]["pages"][0]["prediction"]
        except Exception:
            return payload.get("document", {}).get("inference", {}).get("prediction", {}) or {}

    def _line_items(doc: Dict[str, Any]) -> List[Dict[str, Any]]:
        items = []
        for li in (doc.get("line_items") or []):
            def _gv(field):
                v = li.get(field) or {}
                if isinstance(v, dict):
                    return v.get("value")
                return None

            items.append({
                "code":  _gv("product_code"),
                "name":  _gv("description") or "",
                "qty":   _gv("quantity"),
                "price": _gv("unit_price"),
                "total": _gv("total_amount"),
            })
        return items

    doc = _extract_prediction(raw)

    items = [{
        "code": it.get("code") or "",
        "name": (it.get("name") or "").strip(),
        "qty": float(it.get("qty") or 0) if it.get("qty") is not None else 0.0,
        "price": float(it.get("price") or 0) if it.get("price") is not None else 0.0,
        "total": float(it.get("total") or 0) if it.get("total") is not None else 0.0,
    } for it in _line_items(doc) if (
        it.get("name") and (it.get("qty") or 0) > 0 and (it.get("price") or 0) > 0 and (it.get("total") or 0) > 0
    )]

    data: Dict[str, Any] = {
        "supplier":   (doc.get("supplier") or {}).get("value") if isinstance(doc.get("supplier"), dict) else None,
        "client":     (doc.get("customer") or {}).get("value") if isinstance(doc.get("customer"), dict) else None,
        "doc_number": (doc.get("invoice_number") or {}).get("value") if isinstance(doc.get("invoice_number"), dict) else None,
        "date":       (doc.get("invoice_date") or {}).get("value") if isinstance(doc.get("invoice_date"), dict) else None,
        "items": items,
        "total_sum":  (doc.get("total_amount") or {}).get("value") if isinstance(doc.get("total_amount"), dict) else None,
    }

    if not data["date"]:
        v = doc.get("date")
        if isinstance(v, dict):
            data["date"] = v.get("value")

    ssum = round(sum(i["qty"] * i["price"] for i in items), 2) if items else 0.0
    tval_raw = data.get("total_sum")
    tval = float(tval_raw) if tval_raw is not None else 0.0
    if tval and abs(ssum - tval) / max(tval, 1.0) > 0.05:
        data["status"] = "needs_review"
        data["note"] = f"sum(items)={ssum} != total={tval}"
    else:
        data["status"] = "ok"
    if not data.get("total_sum") and ssum:
        data["total_sum"] = ssum

    return data


def parse_text_mindee(text: str) -> Dict[str, Any]:
    if not text:
        return {
            "supplier": None,
            "client": None,
            "doc_number": None,
            "date": None,
            "items": [],
            "total_sum": None,
            "status": "empty",
            "warnings": ["mindee: empty text"],
        }

    payload: Optional[Dict[str, Any]] = None
    if text.startswith("<<MINDEE_STRUCT>>"):
        try:
            payload = json.loads(text.split("\n", 1)[1])
        except Exception:
            logger.exception("[Mindee] failed to decode structured payload")
            payload = None
    else:
        try:
            payload = json.loads(text)
        except Exception:
            logger.warning("[Mindee] unexpected payload format")
            payload = None

    if not payload:
        return {
            "supplier": None,
            "client": None,
            "doc_number": None,
            "date": None,
            "items": [],
            "total_sum": None,
            "status": "empty",
            "warnings": ["mindee: payload decoding failed"],
        }

    data = mindee_struct_to_data(payload)
    data.setdefault("warnings", [])
    return data


def build_extraction_result(
    data: Dict[str, Any],
    pdf_path: str,
    *,
    template_name: str = "mindee",
) -> ExtractionResult:
    items_raw = data.get("items") or []
    items_out: List[Item] = []
    for it in items_raw:
        items_out.append(Item(
            code=it.get("code"),
            name=(it.get("name") or "").strip(),
            qty=float(it.get("qty") or 0),
            price=float(it.get("price") or 0),
            total=float(it.get("total") or 0),
            page_no=it.get("page_no"),
        ))

    total_sum_raw = data.get("total_sum")
    try:
        total_sum = float(total_sum_raw) if total_sum_raw is not None else None
    except Exception:
        total_sum = None

    document_id = data.get("document_id") or file_sha256(pdf_path)
    result = ExtractionResult(
        document_id=document_id,
        supplier=data.get("supplier"),
        client=data.get("client"),
        date=data.get("date"),
        total_sum=total_sum,
        template=template_name,
        score=1.0 if items_out else 0.4,
        extractor_version=f"{template_name}@mindee",
        pages=[],
        items=items_out,
        warnings=data.get("warnings", []),
    )
    return result


def extract_invoice_mindee(pdf_path: str) -> ExtractionResult:
    logger.info(f"[Mindee] extract start path={pdf_path}")
    text = extract_text_mindee(pdf_path)
    data = parse_text_mindee(text)
    result = build_extraction_result(data, pdf_path)
    logger.info(f"[Mindee] extract done items={len(result.items)} total={result.total_sum}")
    return result