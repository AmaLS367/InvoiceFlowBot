import json
import os
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Protocol, cast

import requests
from mindee import ClientV2, InferenceParameters
from mindee.input import PathInput
from mindee.parsing.v2.inference_response import InferenceResponse

from backend import config
from backend.ocr.engine.types import ExtractionResult, Item
from backend.ocr.engine.util import file_sha256, get_logger

MINDEE_API = config.MINDEE_API_KEY
MODEL_ID_MINDEE = config.MINDEE_MODEL_ID

# Network timeout for Mindee HTTP calls (seconds).
MINDEE_HTTP_TIMEOUT_SECONDS = 60

logger = get_logger("ocr.mindee")

_UUID_RE = re.compile(
    r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$"
)


class _MindeeResultClient(Protocol):
    def enqueue_and_get_result(
        self,
        response_cls: type[InferenceResponse],
        input_source: PathInput,
        params: InferenceParameters,
    ) -> InferenceResponse: ...


def _mindee_predict_url(model_id: str) -> str:
    normalized = model_id.strip().strip("/")
    return f"https://api.mindee.net/v1/products/{normalized}/predict"


def _dump_sdk_debug(response: Any) -> None:
    log_dir = Path(config.LOG_DIR) if config.LOG_DIR else Path("logs")
    debug_path = log_dir / "mindee_v2_debug.json"

    try:
        os.makedirs(log_dir, exist_ok=True)
        raw_json = getattr(response, "to_json", None)
        if callable(raw_json):
            raw_str = cast(str, raw_json())
        else:
            raw_str = json.dumps(response, default=lambda o: getattr(o, "__dict__", str(o)))
        with open(debug_path, "w", encoding="utf-8") as f:
            json.dump(json.loads(raw_str), f, ensure_ascii=False, indent=2)
    except Exception as exc:
        logger.warning("[Mindee ClientV2] failed to write debug dump to %s: %s", debug_path, exc)


def _field_value(field: Any) -> Optional[Any]:
    if not isinstance(field, dict):
        return None

    if "value" in field:
        return field.get("value")

    values = field.get("values")
    if isinstance(values, list) and values:
        first = values[0]
        if isinstance(first, dict):
            return first.get("value") or first.get("content") or first.get("raw_value")
        return first

    return None


def mindee_predict(path: str) -> Optional[dict]:
    api = MINDEE_API
    model_id = MODEL_ID_MINDEE
    if not api or not model_id:
        logger.warning("[Mindee HTTP] no API key or model id in env")
        return None
    if "/" not in model_id or _UUID_RE.match(model_id):
        logger.info("[Mindee HTTP] skipping v1 fallback for v2/custom model id %s", model_id)
        return None
    try:
        url = _mindee_predict_url(model_id)
        with open(path, "rb") as f:
            r = requests.post(
                url,
                headers={"Authorization": f"Token {api}"},
                files={"document": f},
                timeout=MINDEE_HTTP_TIMEOUT_SECONDS,
            )
        r.raise_for_status()
        return cast(Dict[str, Any], r.json())
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
        params = InferenceParameters(
            model_id=model_id,
            rag=False,
        )
        input_source = PathInput(path)
        result_client = cast(_MindeeResultClient, client)
        response = result_client.enqueue_and_get_result(InferenceResponse, input_source, params)

        # Debug dump must never turn a successful SDK response into a failed OCR request.
        _dump_sdk_debug(response)

        raw_json = getattr(response, "to_json", None)
        if callable(raw_json):
            try:
                payload = json.loads(cast(str, raw_json()))
                if isinstance(payload, dict):
                    return payload
            except Exception:
                logger.exception("[Mindee ClientV2] failed to decode response.to_json() for file %s", path)

        fields: Dict[str, Any] = getattr(response.inference.result, "fields", {})

        def _simple_value(field_name: str) -> Optional[Any]:
            field = fields.get(field_name)
            return getattr(field, "value", None) if field is not None else None

        supplier = _simple_value("supplier_name")
        customer = _simple_value("customer_name") or _simple_value("customer_id")
        invoice_number = _simple_value("invoice_number")
        invoice_date = _simple_value("date")
        total_amount = _simple_value("total_amount")

        items_norm: List[Dict[str, Any]] = []
        line_items_field = fields.get("line_items")
        if line_items_field is not None:
            for item in getattr(line_items_field, "items", []):
                item_fields = getattr(item, "fields", {})

                def _item_value(field_name: str) -> Optional[Any]:
                    fld = item_fields.get(field_name)
                    return getattr(fld, "value", None) if fld is not None else None

                product_code = _item_value("product_code")
                description = _item_value("description")
                quantity = _item_value("quantity")
                unit_price = _item_value("unit_price")
                total_price = _item_value("total_price")
                total_amount_item = _item_value("total_amount")

                items_norm.append(
                    {
                        "product_code": {"value": product_code},
                        "description": {"value": description},
                        "quantity": {"value": quantity},
                        "unit_price": {"value": unit_price},
                        "total_amount": {"value": (total_price or total_amount_item)},
                    }
                )

        prediction: Dict[str, Any] = {
            "supplier": {"value": supplier},
            "customer": {"value": customer},
            "invoice_number": {"value": invoice_number},
            "invoice_date": {"value": invoice_date},
            "total_amount": {"value": total_amount},
            "line_items": items_norm,
        }

        packed = {
            "document": {
                "inference": {
                    "pages": [
                        {
                            "prediction": prediction,
                        }
                    ]
                }
            }
        }

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
            pred = payload["document"]["inference"]["pages"][0]["prediction"]
            return cast(Dict[str, Any], pred)
        except Exception:
            pred = payload.get("document", {}).get("inference", {}).get("prediction", {}) or {}
            if pred:
                return cast(Dict[str, Any], pred)

        v2_fields = payload.get("inference", {}).get("result", {}).get("fields", {}) or {}
        if not v2_fields:
            v2_fields = payload.get("_raw_http", {}).get("inference", {}).get("result", {}).get("fields", {}) or {}

        if isinstance(v2_fields, dict) and v2_fields:
            return {
                "supplier": v2_fields.get("supplier") or v2_fields.get("supplier_name"),
                "customer": (
                    v2_fields.get("customer")
                    or v2_fields.get("customer_name")
                    or v2_fields.get("customer_id")
                ),
                "invoice_number": v2_fields.get("invoice_number"),
                "invoice_date": v2_fields.get("invoice_date") or v2_fields.get("date"),
                "date": v2_fields.get("date"),
                "total_amount": (
                    v2_fields.get("total_amount")
                    or v2_fields.get("amount_due")
                    or v2_fields.get("total_including_tax")
                    or v2_fields.get("total_net")
                ),
                "line_items": v2_fields.get("line_items") or [],
            }

        return {}

    def _line_items(doc: Dict[str, Any]) -> List[Dict[str, Any]]:
        items: List[Dict[str, Any]] = []

        raw_line_items = doc.get("line_items") or []

        if isinstance(raw_line_items, dict) and "items" in raw_line_items:
            candidate_items = raw_line_items.get("items") or []
            if isinstance(candidate_items, list):
                raw_line_items = candidate_items

        if isinstance(raw_line_items, dict) and "values" in raw_line_items:
            candidate_values = raw_line_items.get("values") or []
            if isinstance(candidate_values, list):
                raw_line_items = candidate_values

        if not isinstance(raw_line_items, list):
            return items

        for li in raw_line_items:
            if not isinstance(li, dict):
                continue

            fields_candidate = li.get("fields")
            item_fields = fields_candidate if isinstance(fields_candidate, dict) else li

            product_code = _field_value(item_fields.get("product_code"))
            description = _field_value(item_fields.get("description"))
            quantity = _field_value(item_fields.get("quantity"))
            unit_price = _field_value(item_fields.get("unit_price"))
            total_amount = _field_value(item_fields.get("total_amount") or item_fields.get("total_price"))

            items.append(
                {
                    "code": product_code,
                    "name": (description or "").strip(),
                    "qty": quantity,
                    "price": unit_price,
                    "total": total_amount,
                }
            )

        return items

    doc = _extract_prediction(raw)

    items = [
        {
            "code": it.get("code") or "",
            "name": (it.get("name") or "").strip(),
            "qty": float(it.get("qty") or 0) if it.get("qty") is not None else 0.0,
            "price": float(it.get("price") or 0) if it.get("price") is not None else 0.0,
            "total": float(it.get("total") or 0) if it.get("total") is not None else 0.0,
        }
        for it in _line_items(doc)
        if (
            it.get("name")
            and (it.get("qty") or 0) > 0
            and (it.get("price") or 0) > 0
            and (it.get("total") or 0) > 0
        )
    ]

    data: Dict[str, Any] = {
        "supplier": _field_value(doc.get("supplier")),
        "client": _field_value(doc.get("customer")),
        "doc_number": _field_value(doc.get("invoice_number")),
        "date": _field_value(doc.get("invoice_date")),
        "items": items,
        "total_sum": _field_value(doc.get("total_amount")),
    }

    if not data["date"]:
        v = doc.get("date")
        if isinstance(v, dict):
            data["date"] = _field_value(v)

    ssum = round(sum(float(i["qty"]) * float(i["price"]) for i in items), 2) if items else 0.0
    tval_raw = data.get("total_sum")
    tval = float(tval_raw) if tval_raw is not None else 0.0
    if tval and abs(ssum - tval) / max(tval, 1.0) > 0.05:
        data["status"] = "needs_review"
        data["note"] = f"sum(items)={ssum} != total={tval}"
    else:
        data["status"] = "ok"
    if not data.get("total_sum") and ssum:
        data["total_sum"] = ssum

    if not items and doc.get("line_items"):
        logger.warning("[Mindee] line_items present in payload but parsed items list is empty")

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
        items_out.append(
            Item(
                code=it.get("code"),
                name=(it.get("name") or "").strip(),
                qty=float(it.get("qty") or 0),
                price=float(it.get("price") or 0),
                total=float(it.get("total") or 0),
                page_no=it.get("page_no"),
            )
        )

    total_sum_raw = data.get("total_sum")
    try:
        total_sum = float(total_sum_raw) if total_sum_raw is not None else None
    except Exception:
        total_sum = None

    document_id = data.get("document_id") or file_sha256(pdf_path)
    result = ExtractionResult(
        document_id=document_id,
        doc_number=data.get("doc_number"),
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
