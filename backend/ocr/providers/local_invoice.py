"""Map English and Russian invoice labels and tables to the OCR result."""

import re
from datetime import datetime
from decimal import Decimal

from backend.ocr.engine.types import Item

_HEADER_LABELS = {
    "doc_number": (
        r"invoice\s*(?:number\b|no\b|(?=[#№]))|"
        r"(?:сч[её]т(?:-фактура)?\s*(?=№)|номер\s+сч[её]та)"
    ),
    "supplier": r"supplier(?:\s+name)?|vendor(?:\s+name)?|seller|bill from|поставщик|продавец",
    "client": (
        r"bill(?:ed)? to|customer(?:\s+name)?|buyer|client(?:\s+name)?|"
        r"покупатель|заказчик|клиент|плательщик"
    ),
    "date": r"invoice\s+date|date\s+of\s+issue|date|дата(?:\s+(?:сч[её]та|выставления))?",
    "amount_due": r"amount due|balance due|total due|к оплате|итого к оплате",
    "total_sum": (
        r"grand total|invoice total|total amount|total(?:\s+incl\.?\s+(?:vat|tax))?|"
        r"всего к оплате|всего(?:\s+с\s+ндс)?|итого(?:\s+с\s+ндс)?"
    ),
}
_HEADER = re.compile(
    r"^(?:" + "|".join(f"(?P<{field}>{labels})" for field, labels in _HEADER_LABELS.items()) + r")"
    r"(?=\s|[:#№.]|$)\s*[:#№.]?\s*(?P<value>.*)$",
    re.IGNORECASE,
)
_INLINE_LABEL = re.compile(
    r"\s+(?=(?:" + "|".join(_HEADER_LABELS.values()) + r")\s*[:#№])", re.IGNORECASE
)
_DATE = re.compile(r"\b(?:\d{4}[-./]\d{1,2}[-./]\d{1,2}|\d{1,2}[-./]\d{1,2}[-./]\d{4})\b")
_CURRENCY = r"(?:[$€£₽֏₸]|\b(?:USD|EUR|GBP|RUB|AMD|KZT|руб(?:\.|лей)?)(?!\w))"
_NUMBER = re.compile(r"[+-]?(?:\d{1,3}(?: \d{3})+|\d+)(?:[.,]\d+)*")
_COLUMN_LABELS = {
    "name": r"description|item(?: name| description)?|product(?: name)?|"
    r"наименование(?: товара| работ| услуг)?|товар|описание|номенклатура",
    "code": r"sku|item code|product code|code|артикул|код",
    "qty": r"qty|quantity|кол[.\s-]*во|количество",
    "price": r"unit price|price(?: per unit)?|rate|цена(?: за единицу)?",
    "total": r"(?:line )?total|amount|sum|стоимость|сумма|всего",
}
_COLUMNS = {field: re.compile(label, re.IGNORECASE) for field, label in _COLUMN_LABELS.items()}


def _number(value: str, *, quantity: bool = False) -> Decimal | None:
    value = re.sub(_CURRENCY, "", value, flags=re.IGNORECASE)
    value = " ".join(value.replace("−", "-").split())
    if not _NUMBER.fullmatch(value):
        return None

    value = value.replace(" ", "")
    # The rightmost separator is decimal when both conventions are present.
    match = re.search(r"([.,])(\d+)$", value)
    if match is None:
        return Decimal(value)
    mixed_separators = "," in value and "." in value
    fractional = (
        mixed_separators
        or len(match[2]) != 3
        or value.lstrip("+-").startswith(("0,", "0."))
        or (quantity and value.count(match[1]) == 1)
    )
    integer = value[: match.start()] if fractional else value
    if not re.fullmatch(r"[+-]?(?:\d+|\d{1,3}(?:[.,]\d{3})+)", integer):
        return None
    integer = re.sub(r"[.,]", "", integer)
    return Decimal(f"{integer}.{match[2]}" if fractional else integer)


def _date(value: str) -> str | None:
    match = _DATE.search(value)
    if match is None:
        return None
    first, second, third = re.split(r"[-./]", match[0])
    if len(first) == 4:
        year, month, day = first, second, third
    elif int(second) > 12:
        year, month, day = third, first, second
    else:
        year, month, day = third, second, first
    try:
        return datetime(int(year), int(month), int(day)).date().isoformat()
    except ValueError:
        return None


def invoice_fields(lines: list[str]) -> dict[str, str | float]:
    lines = [
        part
        for line in lines
        if line.strip()
        for part in _INLINE_LABEL.split(" ".join(line.split()))
    ]
    fields: dict[str, str | float] = {}
    for index, line in enumerate(lines):
        match = _HEADER.match(line)
        if match is None:
            continue
        field = next(name for name in _HEADER_LABELS if match[name] is not None)
        if field in fields:
            continue
        value = match["value"].strip()
        if not value and index + 1 < len(lines) and not _HEADER.match(lines[index + 1]):
            value = lines[index + 1]
        if not value:
            continue
        if field == "doc_number":
            number = re.match(r"[\w./-]+", value.lstrip(" .:#№"))
            if number:
                fields[field] = number[0]
        elif field == "date":
            date_value = _date(value)
            if date_value is not None:
                fields[field] = date_value
        elif field in {"total_sum", "amount_due"}:
            amount = _number(value)
            if amount is not None:
                fields[field] = float(amount)
        else:
            fields[field] = value
    if "amount_due" in fields:
        fields.setdefault("total_sum", fields.pop("amount_due"))
    return fields


def invoice_items(rows: list[list[str]], page_no: int | None) -> list[Item]:
    items = []
    columns: dict[str, int] = {}
    for row in rows:
        labels = [" ".join(cell.split()).strip(" .:") for cell in row]
        header: dict[str, int] = {}
        for index, label in enumerate(labels):
            for field, pattern in _COLUMNS.items():
                if pattern.fullmatch(label):
                    header.setdefault(field, index)
        if "name" in header and len(header.keys() & {"qty", "price", "total"}) >= 2:
            columns = header
            continue
        if not columns:
            continue

        cells = {field: labels[index] for field, index in columns.items() if index < len(labels)}
        name = cells.get("name", "")
        if not name or re.match(r"^(?:sub\s*total|tax|vat|ндс|подытог)\b", name, re.I):
            continue
        if _HEADER.match(name):
            continue
        qty = _number(cells.get("qty", ""), quantity=True)
        price = _number(cells.get("price", ""))
        total = _number(cells.get("total", ""))
        if qty is None and price and total is not None:
            qty = total / price
        if price is None and qty and total is not None:
            price = total / qty
        if total is None and qty is not None and price is not None:
            total = qty * price
        if qty is not None and price is not None and total is not None:
            items.append(
                Item(
                    code=cells.get("code") or None,
                    name=name,
                    qty=float(qty),
                    price=float(price),
                    total=float(total),
                    page_no=page_no,
                )
            )
    return items
