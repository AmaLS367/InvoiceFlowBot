from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from backend.ocr.engine.types import ExtractionResult, Item
from backend.ocr.extract import extract, parse_invoice_text


@pytest.fixture()
def mock_extract_invoice():
    """Mock extract_invoice function."""
    return MagicMock()


def test_extract_wrapper():
    """Test extract function is a wrapper for parse_invoice_text."""
    with patch("backend.ocr.extract.parse_invoice_text") as mock_parse:
        mock_parse.return_value = {"document_id": "test"}
        result = extract("test.pdf", fast=True, max_pages=5)
        mock_parse.assert_called_once_with("test.pdf", fast=True, max_pages=5)
        assert result == {"document_id": "test"}


def test_parse_invoice_text_success():
    """Test parse_invoice_text with successful extraction."""
    expected_result = ExtractionResult(
        document_id="test-doc",
        supplier="Test Supplier",
        client="Test Client",
        date="2025-01-15",
        total_sum=100.0,
        template="test",
        items=[
            Item(code="SKU-1", name="Item 1", qty=2.0, price=25.0, total=50.0, page_no=1),
        ],
        pages=[],
        warnings=[],
    )

    with patch("ocr.extract.extract_invoice", return_value=expected_result):
        with patch("ocr.extract.time_block"):
            with patch("pathlib.Path.exists", return_value=True):
                with patch("os.path.getsize", return_value=1024):
                    result = parse_invoice_text("test.pdf", fast=True, max_pages=12)

                    assert result["document_id"] == "test-doc"
                    assert result["supplier"] == "Test Supplier"
                    assert result["client"] == "Test Client"
                    assert result["date"] == "2025-01-15"
                    assert result["total_sum"] == 100.0
                    assert len(result["items"]) == 1
                    assert result["items"][0]["name"] == "Item 1"


def test_parse_invoice_text_with_warnings():
    """Test parse_invoice_text with warnings."""
    expected_result = ExtractionResult(
        document_id="test-doc",
        supplier=None,
        client=None,
        date=None,
        total_sum=None,
        template="test",
        items=[],
        pages=[],
        warnings=["missing_tax", "low_confidence"],
    )

    with patch("ocr.extract.extract_invoice", return_value=expected_result):
        with patch("ocr.extract.time_block"):
            with patch("pathlib.Path.exists", return_value=True):
                with patch("os.path.getsize", return_value=1024):
                    result = parse_invoice_text("test.pdf", fast=False, max_pages=5)

                    assert result["warnings"] == ["missing_tax", "low_confidence"]


def test_parse_invoice_text_no_items():
    """Test parse_invoice_text with no items."""
    expected_result = ExtractionResult(
        document_id="test-doc",
        supplier="Supplier",
        client="Client",
        date="2025-01-15",
        total_sum=100.0,
        template="test",
        items=[],
        pages=[],
        warnings=[],
    )

    with patch("ocr.extract.extract_invoice", return_value=expected_result):
        with patch("ocr.extract.time_block"):
            with patch("pathlib.Path.exists", return_value=True):
                with patch("os.path.getsize", return_value=1024):
                    result = parse_invoice_text("test.pdf")

                    assert result["items"] == []
                    assert len(result["items"]) == 0


def test_parse_invoice_text_file_not_found():
    """Test parse_invoice_text when file doesn't exist."""
    with patch("pathlib.Path.exists", return_value=False):
        with patch("os.path.getsize", side_effect=OSError("File not found")):
            with patch("backend.ocr.extract.extract_invoice", side_effect=FileNotFoundError):
                with pytest.raises(FileNotFoundError):
                    parse_invoice_text("nonexistent.pdf")


def test_parse_invoice_text_with_pages():
    """Test parse_invoice_text with pages."""
        from backend.ocr.engine.types import PageInfo

    expected_result = ExtractionResult(
        document_id="test-doc",
        supplier="Supplier",
        client="Client",
        date="2025-01-15",
        total_sum=100.0,
        template="test",
        items=[],
        pages=[
            PageInfo(
                page_no=1,
                width=800,
                height=1200,
                header_text="Page 1",
                template="tpl-1",
                score=0.95,
            ),
        ],
        warnings=[],
    )

    with patch("ocr.extract.extract_invoice", return_value=expected_result):
        with patch("ocr.extract.time_block"):
            with patch("pathlib.Path.exists", return_value=True):
                with patch("os.path.getsize", return_value=1024):
                    result = parse_invoice_text("test.pdf")

                    assert len(result["pages"]) == 1
                    assert result["pages"][0]["page_no"] == 1
                    assert result["pages"][0]["width"] == 800


def test_parse_invoice_text_exception_handling():
    """Test parse_invoice_text exception handling."""
    with patch("backend.ocr.extract.extract_invoice", side_effect=RuntimeError("OCR failed")):
        with patch("ocr.extract.time_block"):
            with patch("pathlib.Path.exists", return_value=True):
                with patch("os.path.getsize", return_value=1024):
                    with pytest.raises(RuntimeError):
                        parse_invoice_text("test.pdf")
