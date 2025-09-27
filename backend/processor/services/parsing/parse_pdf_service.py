import asyncio
import datetime
from dataclasses import dataclass
from pathlib import Path

import pdfplumber
from pypdf import PdfReader
from pypdf._page import PageObject as PyPDFPage
from pypdf.generic import DictionaryObject, PdfObject

from core.domain.extraction import Link, Page, ParsedDocument

from .base_extraction_service import BaseExtractionService


@dataclass
class PDFWord:
    """Word extracted by pdfplumber with position data."""
    text: str
    x0: float
    x1: float
    top: float
    bottom: float


@dataclass
class PDFBounds:
    """PDF coordinate bounds for a region."""
    x0: float
    x1: float
    top: float
    bottom: float


class ParsePdfService(BaseExtractionService):
    def __init__(self, pdf_path: str):
        self.pdf_path = Path(pdf_path)

    async def parse_to_json(self) -> ParsedDocument:
        pages = await asyncio.to_thread(self._extract_all_pages)
        return self._build_response(pages)

    def _extract_all_pages(self) -> list[Page]:
        """Sync method for PDF extraction, run in thread pool via asyncio.to_thread."""
        pages: list[Page] = []

        with pdfplumber.open(self.pdf_path) as pdf_doc:
            with open(self.pdf_path, "rb") as pdf_file:
                reader = PdfReader(pdf_file)

                for page_num, (plumber_page, pypdf_page) in enumerate(
                        zip(pdf_doc.pages, reader.pages, strict=False), start=1
                ):
                    text = plumber_page.extract_text()
                    links = self._extract_links(plumber_page, pypdf_page)
                    pages.append(Page(page_number=page_num, text=text, links=links))

        return pages

    def _extract_links(self, plumber_page: pdfplumber.page.Page, pypdf_page: PyPDFPage) -> list[Link]:
        annots = pypdf_page.annotations
        if not annots:
            return []

        links: list[Link] = []
        seen_links = set()
        raw_words = plumber_page.extract_words()
        # Only extract the fields we actually use
        words = [
            PDFWord(
                text=w['text'],
                x0=w['x0'],
                x1=w['x1'],
                top=w['top'],
                bottom=w['bottom']
            )
            for w in raw_words
        ]

        for annotation in annots:
            link = self._process_annotation(annotation, plumber_page, words)
            if link and (link.text, link.url) not in seen_links:
                seen_links.add((link.text, link.url))
                links.append(link)

        return links

    def _process_annotation(
            self, annotation: PdfObject, page: pdfplumber.page.Page, words: list[PDFWord]
    ) -> Link | None:
        # get_object() resolves indirect references
        annot_obj = annotation.get_object()
        annot_dict: DictionaryObject = annot_obj  # type: ignore[assignment]

        if annot_dict.get("/Subtype") != "/Link":
            return None

        uri = self._extract_uri(annot_dict)
        if not uri:
            return None

        rect = annot_dict.get("/Rect")
        if not rect:
            return None

        anchor_text = self._find_anchor_text(rect, page.height, words)
        if not anchor_text:
            return None

        return Link(text=anchor_text, url=uri)

    def _extract_uri(self, annotation_obj: DictionaryObject) -> str | None:
        action = annotation_obj.get("/A")
        if not action:
            return None
        action_dict: DictionaryObject = action
        uri = action_dict.get("/URI")
        return str(uri) if uri else None

    def _find_anchor_text(
            self, rect: list[float], page_height: float, words: list[PDFWord]
    ) -> str:
        bounds = self._convert_coordinates(rect, page_height)

        matching_words = [
            word.text.strip()
            for word in words
            if self._word_in_bounds(word, bounds)
        ]

        return " ".join(matching_words).strip()

    def _convert_coordinates(
            self, rect: list[float], page_height: float
    ) -> PDFBounds:
        x0, y0, x1, y1 = rect
        return PDFBounds(
            x0=x0,
            top=page_height - y1,
            x1=x1,
            bottom=page_height - y0,
        )

    def _word_in_bounds(self, word: PDFWord, bounds: PDFBounds) -> bool:
        return (
                word.x0 <= bounds.x1
                and word.x1 >= bounds.x0
                and word.top <= bounds.bottom
                and word.bottom >= bounds.top
        )

    def _build_response(self, pages: list[Page]) -> ParsedDocument:
        return ParsedDocument(
            file_type=self.pdf_path.suffix.lower(),
            processed_at=datetime.datetime.now().isoformat() + "Z",
            pages=pages,
            processing_method="pdf_extract",
        )
