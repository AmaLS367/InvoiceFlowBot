from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import MagicMock, mock_open, patch

from backend.ocr.mindee_client import mindee_predict, mindee_predict_sdk


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
    fake_client.enqueue_and_get_inference.return_value = response

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
    assert payload["document"]["inference"]["pages"][0]["prediction"]["line_items"] == []


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
