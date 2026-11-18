from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Item:
    code: Optional[str]
    name: str
    qty: float
    price: float
    total: float
    page_no: Optional[int] = None
    # Reasons to double-check the row, e.g. "total_mismatch" or "total_computed".
    review: List[str] = field(default_factory=list)


@dataclass
class PageInfo:
    page_no: int
    width: int
    height: int
    header_text: Optional[str] = None
    template: Optional[str] = None
    score: Optional[float] = None


@dataclass
class ExtractionResult:
    document_id: str
    doc_number: Optional[str] = None
    supplier: Optional[str] = None
    client: Optional[str] = None
    date: Optional[str] = None
    total_sum: Optional[float] = None
    template: str = "generic"
    score: float = 0.0
    extractor_version: str = "engine@0.1.0"
    pages: List[PageInfo] = field(default_factory=list)
    items: List[Item] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    # Document-level reasons to double-check the result, e.g. "rows_skipped:3".
    review: List[str] = field(default_factory=list)
    provider: Optional[str] = None
