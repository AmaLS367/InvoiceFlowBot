"""Map English and Russian invoice labels and tables to the OCR result."""

import re
from datetime import datetime
from decimal import ROUND_HALF_UP, Decimal

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
    "discount": r"disc(?:ount)?(?:\.?\s*line)?|скидка",
    "total": r"(?:line )?total|amount|sum|стоимость|сумма|всего",
}
_COLUMNS = {field: re.compile(label, re.IGNORECASE) for field, label in _COLUMN_LABELS.items()}
_CENT = Decimal("0.01")
_CONTINUED = re.compile(r"\bcontinu|продолж|перенос", re.IGNORECASE)
_LABEL_ONLY = re.compile(r"[^\W\d][^:]{0,40}:")
_CODE = re.compile(r"[^\W\d_]{1,6}[-/]?\d[\w./-]*")
# Cyrillic letters that OCR returns for look-alike Latin ones in article codes.
_LATIN_LOOKALIKES = str.maketrans("АВЕКМНОРСТХаеорсух", "ABEKMHOPCTXaeopcyx")


def _number(value: str, *, quantity: bool = False) -> Decimal | None:
    value = re.sub(_CURRENCY, "", value, flags=re.IGNORECASE)
    value = " ".join(value.replace("−", "-").split())
    # Accounting notation prints negative amounts in brackets: (1,250.00).
    brackets = re.fullmatch(r"\(\s*([^()]*?)\s*\)", value)
    if brackets and not brackets[1].startswith(("-", "+")):
        value = f"-{brackets[1]}"
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


def _pair_label_runs(lines: list[str]) -> list[str]:
    """Join "A:", "B:", "1", "2" into "A: 1", "B: 2".

    Layout analysis of a scanned totals box can return the label column before the value
    column; reading the next line after each label would shift every value by one row.
    """
    paired: list[str] = []
    index = 0
    while index < len(lines):
        end = index
        while end < len(lines) and _LABEL_ONLY.fullmatch(lines[end]):
            end += 1
        count = end - index
        values = lines[end : end + count]
        if count > 1 and len(values) == count and not any(map(_LABEL_ONLY.fullmatch, values)):
            paired.extend(f"{label} {value}" for label, value in zip(lines[index:end], values))
            index = end + count
        else:
            paired.extend(lines[index : max(end, index + 1)])
            index = max(end, index + 1)
    return paired


def invoice_fields(lines: list[str]) -> dict[str, str | float]:
    lines = [
        part
        for line in _pair_label_runs([" ".join(line.split()) for line in lines if line.strip()])
        for part in _INLINE_LABEL.split(line)
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


def _percent(value: str) -> Decimal | None:
    match = re.fullmatch(r"([+-]?\d+(?:[.,]\d+)?)\s*%?", value)
    return Decimal(match[1].replace(",", ".")) if match else None


def _header_columns(cells: list[str]) -> dict[str, int]:
    header: dict[str, int] = {}
    for index, cell in enumerate(cells):
        # Drop unit hints such as "Qty (pcs)", "Unit Price (USD)" or "Disc. %".
        label = re.sub(r"\s*\([^)]*\)", "", cell).strip(" .:%")
        for field, pattern in _COLUMNS.items():
            if pattern.fullmatch(label):
                header.setdefault(field, index)
    if "name" in header and len(header.keys() & {"qty", "price", "total"}) >= 2:
        return header
    return {}


def _infer_columns(header: dict[str, int], body: list[list[str]]) -> dict[str, int]:
    """Fill item columns whose headings OCR could not read from the cell contents."""
    columns = dict(header)
    width = max((len(row) for row in body), default=0)

    def share(index: int, matches) -> float:
        values = [row[index] for row in body if index < len(row) and row[index]]
        return sum(bool(matches(value)) for value in values) / len(values) if values else 0.0

    def is_amount(value: str) -> bool:
        return "%" not in value and _number(value) is not None

    free = [index for index in range(width) if index not in columns.values()]
    if "code" not in columns:
        codes = [index for index in free if share(index, _CODE.fullmatch) >= 0.6]
        if codes:
            columns["code"] = codes[0]
    if "price" in columns:
        left = columns.get("name", -1)
        if "qty" not in columns:
            between = [
                index
                for index in free
                if left < index < columns["price"] and share(index, is_amount) >= 0.6
            ]
            if between:
                columns["qty"] = between[-1]
        if "total" not in columns:
            right = [
                index
                for index in free
                if index > columns["price"] and share(index, is_amount) >= 0.6
            ]
            if right:
                columns["total"] = right[-1]
    return columns


def _decimal_slip(read: str, implied: Decimal) -> bool:
    """True when OCR dropped the decimal separator, e.g. "15" for 1,5."""
    digits = re.sub(r"\D", "", read)
    implied_digits = re.sub(r"\D", "", format(implied.normalize(), "f"))
    return bool(digits) and digits == implied_digits and "." in format(implied.normalize(), "f")


class InvoiceTableReader:
    """Read item rows from the tables of one document in page order.

    A table without its own header continues the previous item table when it has the
    same number of columns, which covers schedules that print headings on page 1 only.
    """

    def __init__(self) -> None:
        self.items: list[Item] = []
        self.skipped_rows = 0
        self._columns: dict[str, int] = {}
        self._width = 0
        self._table = 0
        self._last_item_table = -1

    def add_table(self, rows: list[list[str]], page_no: int | None) -> None:
        self._table += 1
        width = max((len(row) for row in rows), default=0)
        columns = self._columns if width == self._width else {}
        table = [[" ".join(cell.split()) for cell in row] for row in rows]
        for index, cells in enumerate(table):
            header = _header_columns(cells)
            if header:
                body = []
                for row in table[index + 1 :]:
                    if _header_columns(row):
                        break
                    body.append(row)
                columns = self._columns = _infer_columns(header, body)
                self._width = width
                continue
            if columns:
                self._read_row(cells, columns, page_no)

    def finish(self) -> list[Item]:
        """Apply document-wide corrections and return the items."""
        codes = [item.code for item in self.items if item.code]
        latin = sum(code.isascii() for code in codes)
        if codes and latin * 2 >= len(codes):
            for item in self.items:
                if item.code and not item.code.isascii():
                    fixed = item.code.translate(_LATIN_LOOKALIKES)
                    if fixed.isascii():
                        item.code = fixed
        return self.items

    def _read_row(self, row: list[str], columns: dict[str, int], page_no: int | None) -> None:
        cells = {
            field: row[index].strip(" :") if index < len(row) else ""
            for field, index in columns.items()
        }
        name = cells.get("name", "").strip(" .")
        numbers = [cells.get(field, "") for field in ("qty", "price", "total")]
        if not any(numbers) and not cells.get("code") and name:
            # A wrapped description line belongs to the item above it; a page footer does not.
            if (
                self.items
                and self._last_item_table == self._table
                and not _HEADER.match(name)
                and not _CONTINUED.search(name)
            ):
                self.items[-1].name = f"{self.items[-1].name} {name}"
            return
        if not name or re.match(r"^(?:sub\s*total|tax|vat|ндс|подытог)\b", name, re.I):
            return
        if _HEADER.match(name):
            return

        qty = _number(cells.get("qty", ""), quantity=True)
        price = _number(cells.get("price", ""))
        total = _number(cells.get("total", ""))
        discount = _percent(cells.get("discount", "")) or Decimal(0)
        factor = 1 - discount / 100
        review = []
        if total is None and qty is not None and price is not None:
            total = (qty * price * factor).quantize(_CENT, ROUND_HALF_UP)
            review.append("total_computed")
        elif qty is None and price and factor and total is not None:
            qty = (total / (price * factor)).quantize(Decimal("0.001")).normalize()
            review.append("qty_computed")
        elif price is None and qty and factor and total is not None:
            price = (total / (qty * factor)).quantize(_CENT)
            review.append("price_computed")
        elif qty is not None and price is not None and total is not None:
            # Printed line totals may round the discounted unit price first.
            expected = qty * price * factor
            tolerance = max(Decimal("0.05"), abs(total) * Decimal("0.002"))
            if abs(expected - total) > tolerance:
                implied_qty = (
                    (total / (price * factor)).quantize(Decimal("0.001"))
                    if price and factor
                    else None
                )
                if implied_qty is not None and _decimal_slip(cells.get("qty", ""), implied_qty):
                    qty = implied_qty.normalize()
                    review.append("qty_corrected")
                elif _decimal_slip(cells.get("total", ""), expected.quantize(_CENT, ROUND_HALF_UP)):
                    total = expected.quantize(_CENT, ROUND_HALF_UP)
                    review.append("total_corrected")
                else:
                    review.append("total_mismatch")

        if qty is None or price is None or total is None:
            if any(numbers):
                self.skipped_rows += 1
            return
        self.items.append(
            Item(
                code=cells.get("code") or None,
                name=name,
                qty=float(qty),
                price=float(price),
                total=float(total),
                page_no=page_no,
                review=review,
            )
        )
        self._last_item_table = self._table


def invoice_items(rows: list[list[str]], page_no: int | None) -> list[Item]:
    reader = InvoiceTableReader()
    reader.add_table(rows, page_no)
    return reader.finish()
