from __future__ import annotations

from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from ocr.async_client import _mindee_predict_async


@pytest.mark.asyncio
async def test_mindee_predict_async_success():
    """Test _mindee_predict_async with successful prediction."""
    test_path = "test.pdf"
    expected_result = {"document": {"inference": {"pages": [{"prediction": {}}]}}}

    with patch("ocr.async_client.mindee_predict_sdk", return_value=expected_result):
        with patch("pathlib.Path.exists", return_value=True):
            result = await _mindee_predict_async(test_path)
            assert result == expected_result


@pytest.mark.asyncio
async def test_mindee_predict_async_file_not_found():
    """Test _mindee_predict_async when file doesn't exist."""
    test_path = "nonexistent.pdf"

    with patch("pathlib.Path.exists", return_value=False):
        with pytest.raises(FileNotFoundError):
            await _mindee_predict_async(test_path)


@pytest.mark.asyncio
async def test_mindee_predict_async_fallback():
    """Test _mindee_predict_async fallback to mindee_predict."""
    test_path = "test.pdf"
    expected_result = {"document": {"inference": {"pages": [{"prediction": {}}]}}}

    with patch("ocr.async_client.mindee_predict_sdk", return_value=None):
        with patch("ocr.async_client.mindee_predict", return_value=expected_result):
            with patch("pathlib.Path.exists", return_value=True):
                result = await _mindee_predict_async(test_path)
                assert result == expected_result


@pytest.mark.asyncio
async def test_mindee_predict_async_no_result():
    """Test _mindee_predict_async when both methods return None."""
    test_path = "test.pdf"

    with patch("ocr.async_client.mindee_predict_sdk", return_value=None):
        with patch("ocr.async_client.mindee_predict", return_value=None):
            with patch("pathlib.Path.exists", return_value=True):
                result = await _mindee_predict_async(test_path)
                assert result == {}


@pytest.mark.asyncio
async def test_extract_invoice_async_success():
    """Test extract_invoice_async with successful extraction."""
    from ocr.async_client import extract_invoice_async
    from ocr.engine.types import ExtractionResult

    test_path = "test.pdf"
    mock_payload = {
        "document": {
            "inference": {
                "pages": [
                    {
                        "prediction": {
                            "supplier_name": {"value": "Test Supplier"},
                            "customer_name": {"value": "Test Client"},
                            "invoice_number": {"value": "INV-001"},
                            "date": {"value": "2025-01-15"},
                            "total_amount": {"value": 100.0},
                            "line_items": {"items": []},
                        }
                    }
                ]
            }
        }
    }

    with patch("ocr.async_client._mindee_predict_async", return_value=mock_payload):
        with patch("ocr.async_client.build_extraction_result") as mock_build:
            mock_build.return_value = ExtractionResult(
                document_id="test",
                supplier="Test Supplier",
                client="Test Client",
                date="2025-01-15",
                total_sum=100.0,
                template="mindee",
                items=[],
                pages=[],
                warnings=[],
            )

            result = await extract_invoice_async(test_path, fast=True, max_pages=12)

            assert result.supplier == "Test Supplier"
            assert result.client == "Test Client"
            assert result.total_sum == 100.0


@pytest.mark.asyncio
async def test_extract_invoice_async_empty_payload():
    """Test extract_invoice_async with empty payload."""
    from ocr.async_client import extract_invoice_async

    test_path = "test.pdf"

    with patch("ocr.async_client._mindee_predict_async", return_value={}):
        with patch("ocr.async_client.build_extraction_result") as mock_build:
            from ocr.engine.types import ExtractionResult

            mock_build.return_value = ExtractionResult(
                document_id="test",
                supplier=None,
                client=None,
                date=None,
                total_sum=None,
                template="mindee",
                items=[],
                pages=[],
                warnings=["mindee async: payload is empty or invalid"],
            )

            result = await extract_invoice_async(test_path)

            assert result.supplier is None
            assert len(result.warnings) > 0

