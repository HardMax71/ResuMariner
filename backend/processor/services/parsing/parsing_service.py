import logging
from pathlib import Path

from rest_framework.exceptions import ValidationError

from core.domain.extraction import ParsedDocument
from core.file_types import ParserType, get_parser_type

from .base_extraction_service import BaseExtractionService
from .parse_image_service import ParseImageService
from .parse_pdf_service import ParsePdfService
from .parse_word_service import ParseWordService

logger = logging.getLogger(__name__)


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
                logger.error("Unsupported file type: %s", file_ext)
                raise ValidationError("Unsupported file type")

    async def parse_file(self, file_path: str) -> ParsedDocument:
        file_ext = Path(file_path).suffix.lower()
        parser = self._get_parser(file_path, file_ext)
        return await parser.parse_to_json()
