from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import MagicMock, mock_open, patch

from backend.ocr.mindee_client import mindee_predict, mindee_predict_sdk, mindee_struct_to_data


def _fake_sdk_response() -> SimpleNamespace:
    fields = {}
    result = SimpleNamespace(fields=fields)
    inference = SimpleNamespace(result=result)
    return SimpleNamespace(
        inference=inference,
        to_json=lambda: '{"ok": true}',
    )


def test_mindee_predict_sdk_ignores_debug_dump_permission_error() -> None:
    response = _fake_sdk_response()
    fake_client = MagicMock()
    fake_client.enqueue_and_get_result.return_value = response

    with (
        patch("backend.ocr.mindee_client.MINDEE_API", "test-key"),
        patch("backend.ocr.mindee_client.MODEL_ID_MINDEE", "mindee/invoices/v4"),
        patch("backend.ocr.mindee_client.ClientV2", return_value=fake_client),
        patch("backend.ocr.mindee_client.PathInput", return_value="input"),
        patch("backend.ocr.mindee_client.InferenceParameters", return_value="params"),
        patch("backend.ocr.mindee_client.os.makedirs"),
        patch("builtins.open", side_effect=PermissionError("denied")),
    ):
        payload = mindee_predict_sdk("invoice.pdf")

    assert payload is not None
    assert payload == {"ok": True}


def test_mindee_predict_uses_model_id_in_request_url() -> None:
    fake_response = MagicMock()
    fake_response.json.return_value = {"ok": True}
    fake_response.raise_for_status.return_value = None

    with (
        patch("backend.ocr.mindee_client.MINDEE_API", "test-key"),
        patch("backend.ocr.mindee_client.MODEL_ID_MINDEE", "mindee/invoices/v4"),
        patch("backend.ocr.mindee_client.requests.post", return_value=fake_response) as mock_post,
        patch("builtins.open", mock_open(read_data=b"pdf")),
    ):
        payload = mindee_predict("invoice.pdf")

    assert payload == {"ok": True}
    assert mock_post.call_args.args[0] == "https://api.mindee.net/v1/products/mindee/invoices/v4/predict"


def test_mindee_predict_skips_v1_fallback_for_uuid_model_id() -> None:
    with (
        patch("backend.ocr.mindee_client.MINDEE_API", "test-key"),
        patch("backend.ocr.mindee_client.MODEL_ID_MINDEE", "523a12b3-a213-41e2-9dab-65737aaa9d82"),
        patch("backend.ocr.mindee_client.requests.post") as mock_post,
    ):
        payload = mindee_predict("invoice.pdf")

    assert payload is None
    mock_post.assert_not_called()


def test_mindee_struct_to_data_supports_v2_fields_payload() -> None:
    payload = {
        "inference": {
            "result": {
                "fields": {
                    "supplier_name": {"value": "Test Supplier"},
                    "customer_name": {"value": "Test Customer"},
                    "invoice_number": {"value": "INV-001"},
                    "date": {"value": "2025-06-08"},
                    "total_amount": {"value": None},
                    "line_items": {
                        "items": [
                            {
                                "fields": {
                                    "description": {"value": "Item A"},
                                    "quantity": {"value": 5.0},
                                    "unit_price": {"value": 2.25},
                                    "total_price": {"value": 11.25},
                                    "product_code": {"value": "A001"},
                                }
                            },
                            {
                                "fields": {
                                    "description": {"value": "Item B"},
                                    "quantity": {"value": 2.0},
                                    "unit_price": {"value": 1.0},
                                    "total_price": {"value": 2.0},
                                    "product_code": {"value": "B002"},
                                }
                            },
                        ]
                    },
                }
            }
        }
    }

    data = mindee_struct_to_data(payload)

    assert data["supplier"] == "Test Supplier"
    assert data["client"] == "Test Customer"
    assert data["doc_number"] == "INV-001"
    assert data["date"] == "2025-06-08"
    assert len(data["items"]) == 2
    assert data["items"][0]["name"] == "Item A"
    assert data["items"][0]["total"] == 11.25
    assert data["total_sum"] == 13.25
