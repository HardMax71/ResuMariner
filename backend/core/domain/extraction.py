from dataclasses import asdict, dataclass, field
from typing import Any

from pydantic import BaseModel, Field


@dataclass
class Link:
    text: str
    url: str


@dataclass
class Page:
    page_number: int
    text: str
    links: list[Link] = field(default_factory=list)


@dataclass
class ParsedDocument:
    file_type: str
    processed_at: str
    pages: list[Page]
    processing_method: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ParsedDocument":
        pages = [
            Page(page_number=p["page_number"], text=p["text"], links=[Link(**link) for link in p.get("links", [])])
            for p in data["pages"]
        ]
        return cls(
            file_type=data["file_type"],
            processed_at=data["processed_at"],
            pages=pages,
            processing_method=data.get("processing_method"),
        )


class OCRExtractedPage(BaseModel):
    page: Page
    confidence: float | None = Field(default=None, ge=0.0, le=1.0)
