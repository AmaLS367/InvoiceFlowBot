from __future__ import annotations

from threading import get_ident
from unittest.mock import patch

import pytest

from backend.config import Settings
from backend.core.container import AppContainer
from backend.ocr.async_client import extract_invoice_async
from backend.ocr.engine.types import ExtractionResult
from backend.ocr.providers.local_provider import LocalOcrProvider

MINDEE_PAYLOAD = {
    "document": {
        "inference": {
            "pages": [
                {
                    "prediction": {
                        "supplier": {"value": "Test Supplier"},
                        "customer": {"value": "Test Client"},
                        "invoice_number": {"value": "INV-001"},
                        "date": {"value": "2025-01-15"},
                        "total_amount": {"value": 100.0},
                    }
                }
            ]
        }
    }
}


@pytest.mark.asyncio
async def test_upload_service_uses_local_ocr_by_default(tmp_path, monkeypatch):
    monkeypatch.delenv("OCR_PROVIDER", raising=False)
    path = tmp_path / "invoice.pdf"
    path.touch()
    settings = Settings(_env_file=None, BOT_TOKEN="test-token")
    caller = get_ident()

    def extract(provider, filename, fast, max_pages):
        assert get_ident() != caller
        assert provider.languages == "eng+rus"
        assert (filename, fast, max_pages) == (str(path), False, 3)
        return ExtractionResult(document_id="1", doc_number="INV-001", provider="local")

    with patch.object(LocalOcrProvider, "extract_invoice", autospec=True, side_effect=extract):
        invoice = await AppContainer(config=settings).invoice_service.process_invoice_file(
            str(path), fast=False, max_pages=3
        )

    assert invoice.header.invoice_number == "INV-001"
    assert invoice.source.provider == "local"


@pytest.mark.asyncio
async def test_extract_invoice_async_file_not_found(tmp_path):
    with pytest.raises(FileNotFoundError):
        await extract_invoice_async(str(tmp_path / "nonexistent.pdf"))


@pytest.mark.asyncio
@pytest.mark.parametrize("use_sdk", [True, False])
async def test_extract_invoice_async_can_select_mindee(tmp_path, use_sdk):
    path = tmp_path / "invoice.pdf"
    path.touch()
    settings = Settings(
        BOT_TOKEN="test-token", OCR_PROVIDER="mindee", MINDEE_API_KEY="key", MINDEE_MODEL_ID="model"
    )

    with (
        patch(
            "backend.ocr.mindee_client.mindee_predict_sdk",
            return_value=MINDEE_PAYLOAD if use_sdk else None,
        ) as sdk,
        patch("backend.ocr.mindee_client.mindee_predict", return_value=MINDEE_PAYLOAD) as fallback,
    ):
        result = await extract_invoice_async(str(path), settings=settings)

    sdk.assert_called_once_with(str(path), api_key="key", model_id="model")
    assert fallback.called is not use_sdk
    assert result.provider == "mindee"
    assert result.supplier == "Test Supplier"
    assert result.client == "Test Client"
    assert result.doc_number == "INV-001"
    assert result.total_sum == 100.0


@pytest.mark.asyncio
async def test_extract_invoice_async_empty_mindee_payload(tmp_path):
    path = tmp_path / "invoice.pdf"
    path.touch()
    settings = Settings(BOT_TOKEN="test-token", OCR_PROVIDER="mindee")

    with (
        patch("backend.ocr.mindee_client.mindee_predict_sdk", return_value=None),
        patch("backend.ocr.mindee_client.mindee_predict", return_value=None),
    ):
        result = await extract_invoice_async(str(path), settings=settings)

    assert result.provider == "mindee"
    assert result.supplier is None
    assert result.warnings
