import datetime
import logging
from pathlib import Path

from pydantic_ai import BinaryContent, ImageUrl

from core.domain.extraction import OCRExtractedPage, ParsedDocument
from core.file_types import get_media_type
from processor.services.llm_service import LLMService

from .base_extraction_service import BaseExtractionService

logger = logging.getLogger(__name__)


class ParseImageService(BaseExtractionService):
    """
    Vision-based image parsing using LLMService with OCR mode.

    Uses the OCR_LLM_* configuration from Django settings.
    """

    def __init__(self, image_path: str):
        self.image_path = Path(image_path)

        system_prompt = """Extract ALL text from the provided image accurately.
            Preserve formatting and structure. Include all URLs found.
            Return JSON strictly matching the provided schema.
        """

        schema_hint = OCRExtractedPage.model_json_schema()
        self.system_prompt = system_prompt + "\nSchema:\n" + str(schema_hint)

        self.llm_service = LLMService(system_prompt=self.system_prompt, output_type=OCRExtractedPage, mode="ocr")

    async def parse_to_json(self) -> ParsedDocument:
        processed_timestamp = datetime.datetime.now().isoformat() + "Z"
        result = ParsedDocument(
            file_type=self.image_path.suffix.lower(),
            processed_at=processed_timestamp,
            pages=[],
            processing_method="vision_llm",
        )

        try:
            image_content = self._load_image()
            # NIT: We also get confidence from OCRExtractedPage; maybe use this field too?
            ocr_result = await self.llm_service.run(
                ["Extract all text from this image. Include any URLs you find.", image_content]
            )
            result.pages.append(ocr_result.output.page)
        except Exception as e:
            logger.error("Vision extraction failed for %s: %s", self.image_path, e)

        return result

    def _load_image(self) -> BinaryContent | ImageUrl:
        str_path = str(self.image_path)

        if str_path.startswith(("http://", "https://")):
            return ImageUrl(url=str_path)

        if not self.image_path.exists():
            raise FileNotFoundError(f"Image file not found: {self.image_path}")

        media_type = get_media_type(self.image_path.suffix)

        with open(self.image_path, "rb") as f:
            return BinaryContent(data=f.read(), media_type=media_type)
