import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

os.environ.setdefault("BOT_TOKEN", "test-token")

from handlers import utils  # noqa: E402
from ocr.engine.router import _result_payload  # noqa: E402
from ocr.engine.types import ExtractionResult, Item, PageInfo  # noqa: E402


def test_result_payload_transforms_dataclasses():
    result = ExtractionResult(
        document_id="doc-1",
        supplier="Acme Inc.",
        client="Client LLC",
        date="2024-10-10",
        total_sum=199.99,
        template="custom",
        score=0.95,
        extractor_version="engine@test",
        items=[
            Item(code="SKU-1", name="Widget", qty=2, price=25.5, total=51.0, page_no=1),
            Item(code=None, name="Service", qty=1, price=148.99, total=148.99, page_no=2),
        ],
        pages=[
            PageInfo(page_no=1, width=800, height=1200, header_text="Invoice 1", template="tpl-a", score=0.88),
            PageInfo(page_no=2, width=800, height=1200, header_text="Invoice 2", template="tpl-a", score=0.90),
        ],
        warnings=["missing_tax"],
    )

    payload = _result_payload(result)

    assert payload["document_id"] == "doc-1"
    assert payload["items"][0]["name"] == "Widget"
    assert payload["items"][1]["code"] is None
    assert payload["pages"][0]["width"] == 800
    assert payload["pages"][1]["header_text"] == "Invoice 2"
    assert payload["warnings"] == ["missing_tax"]


def test_format_money_normalizes_numbers():
    assert utils.format_money(25) == "25"
    assert utils.format_money("25.500") == "25.5"
    assert utils.format_money("10.00") == "10"
    assert utils.format_money("not-a-number") == "not-a-number"


def test_fmt_items_and_csv_output():
    items = [
        {"code": "SKU-1", "name": "Widget", "qty": 2, "price": 25.5, "total": 51},
        {"code": "", "name": "Service", "qty": 1, "price": 148.99, "total": 148.99},
    ]

    formatted = utils.fmt_items(items)
    assert "1. [SKU-1] Widget" in formatted
    assert "Кол-во: 2" in formatted
    assert "Сумма: 51" in formatted

    csv_content = utils.csv_bytes(items).decode("utf-8-sig")
    assert "#;name;qty;price;total" in csv_content
    assert "Widget" in csv_content
    assert "Service" in csv_content

