from __future__ import annotations

from ocr.engine.router import _result_payload
from ocr.engine.types import ExtractionResult, Item, PageInfo


def test_result_payload_basic():
    """Test _result_payload with basic data."""
    result = ExtractionResult(
        document_id="test-doc",
        supplier="Supplier",
        client="Client",
        date="2025-01-15",
        total_sum=100.0,
        template="test",
        items=[
            Item(code="SKU-1", name="Item 1", qty=2.0, price=25.0, total=50.0, page_no=1),
        ],
        pages=[],
        warnings=[],
    )

    payload = _result_payload(result)

    assert payload["document_id"] == "test-doc"
    assert payload["supplier"] == "Supplier"
    assert payload["client"] == "Client"
    assert payload["date"] == "2025-01-15"
    assert payload["total_sum"] == 100.0
    assert len(payload["items"]) == 1
    assert payload["items"][0]["name"] == "Item 1"


def test_result_payload_with_pages():
    """Test _result_payload with pages."""
    result = ExtractionResult(
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

    payload = _result_payload(result)

    assert len(payload["pages"]) == 1
    assert payload["pages"][0]["page_no"] == 1
    assert payload["pages"][0]["width"] == 800
    assert payload["pages"][0]["header_text"] == "Page 1"


def test_result_payload_with_warnings():
    """Test _result_payload with warnings."""
    result = ExtractionResult(
        document_id="test-doc",
        supplier="Supplier",
        client="Client",
        date="2025-01-15",
        total_sum=100.0,
        template="test",
        items=[],
        pages=[],
        warnings=["warning1", "warning2"],
    )

    payload = _result_payload(result)

    assert payload["warnings"] == ["warning1", "warning2"]


def test_result_payload_with_none_values():
    """Test _result_payload with None values."""
    result = ExtractionResult(
        document_id="test-doc",
        supplier=None,
        client=None,
        date=None,
        total_sum=None,
        template="test",
        items=[],
        pages=[],
        warnings=[],
    )

    payload = _result_payload(result)

    assert payload["supplier"] is None
    assert payload["client"] is None
    assert payload["date"] is None
    assert payload["total_sum"] is None
