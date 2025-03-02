import datetime
import os
import re

import pytesseract
from PIL import Image, ImageSequence

from parsers.base_extraction_service import BaseExtractionService


class ParseImageService(BaseExtractionService):
    def __init__(self, image_path: str):
        """
        Initialize with a single image file path.
        The image file may contain multiple pages (e.g., a multi-page TIFF).

        :param image_path: Path to the image file.
        """
        self.image_path = image_path

    def get_num_pages(self) -> int:
        """
        Return the number of pages in the image file.
        For multi-page images (e.g., TIFF), this returns the count of pages.
        """
        try:
            with Image.open(self.image_path) as img:
                pages = list(ImageSequence.Iterator(img))
                return len(pages)
        except Exception as e:
            raise RuntimeError(f"Error opening image {self.image_path}: {e}")

    def parse_to_json(self) -> dict:
        """
        Process the image file using OCR (pytesseract) to extract text.

        This implementation:
          - Iterates over each page in a multi-page image.
          - Uses pytesseract to extract text.
          - Detects URLs in the extracted text using a regex.
          - Returns a JSON structure similar to the PDF parser.
        """
        processed_timestamp = datetime.datetime.utcnow().isoformat() + "Z"
        pages = []

        try:
            with Image.open(self.image_path) as img:
                for idx, page in enumerate(ImageSequence.Iterator(img), start=1):
                    # Use pytesseract to extract text from the current page image.
                    extracted_text = pytesseract.image_to_string(page)

                    # Detect URLs in the extracted text.
                    # This simple regex captures URLs starting with http:// or https://.
                    found_urls = re.findall(r'(https?://\S+)', extracted_text)
                    links = []
                    seen_links = set()
                    for url in found_urls:
                        if url not in seen_links:
                            seen_links.add(url)
                            # In OCR, we may not have separate "anchor" text, so we use the URL.
                            links.append({
                                "text": url,
                                "url": url
                            })

                    pages.append({
                        "page_number": idx,
                        "text": extracted_text.strip(),
                        "links": links
                    })
        except Exception as e:
            raise RuntimeError(f"Error processing image {self.image_path}: {e}")

        return {
            "metadata": {
                "total_pages": len(pages),
                "file_type": os.path.splitext(self.image_path)[1].lower(),
                "processed_at": processed_timestamp
            },
            "pages": pages
        }
