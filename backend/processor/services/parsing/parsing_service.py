import re
from pathlib import Path

from core.domain.extraction import ParsedDocument
from core.file_types import ParserType, get_parser_type

from .base_extraction_service import BaseExtractionService
from .parse_image_service import ParseImageService
from .parse_pdf_service import ParsePdfService
from .parse_word_service import ParseWordService


class ParsingService:
    def _get_parser(self, file_path: str, file_ext: str) -> BaseExtractionService:
        parser_type = get_parser_type(file_ext)

        match parser_type:
            case ParserType.PDF:
                return ParsePdfService(file_path)
            case ParserType.IMAGE:
                return ParseImageService(file_path)
            case ParserType.WORD:
                return ParseWordService(file_path)
            case _:
                raise ValueError(f"Unsupported file type: {file_ext}")

    async def parse_file(self, file_path: str) -> ParsedDocument:
        file_ext = Path(file_path).suffix.lower()
        parser = self._get_parser(file_path, file_ext)
        return await parser.parse_to_json()

    @staticmethod
    def extract_email_from_document(parsed_doc: ParsedDocument) -> str | None:
        link_urls = " ".join(link.url for page in parsed_doc.pages for link in page.links)
        page_text = " ".join(filter(None, [page.text for page in parsed_doc.pages]))
        combined_text = link_urls + " " + page_text

        match = re.search(r"[\w._%+-]+@[\w.-]+\.[A-Z]{2,}", combined_text, re.I)
        return match.group(0).lower() if match else None
