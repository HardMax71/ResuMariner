from dataclasses import dataclass, field

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


class OCRExtractedPage(BaseModel):
    page: Page
    confidence: float | None = Field(default=None, ge=0.0, le=1.0)
