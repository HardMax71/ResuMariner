import datetime
import os

import pdfplumber
from pypdf import PdfReader

from .base_extraction_service import BaseExtractionService


class ParsePdfService(BaseExtractionService):
    def __init__(self, pdf_path):
        self.pdf_path = pdf_path

    def get_num_pages(self):
        """Get the total number of pages in the PDF"""
        with pdfplumber.open(self.pdf_path) as pdf:
            num_pages = len(pdf.pages)
        return num_pages

    def parse_to_json(self):
        """Parse PDF and return JSON structure with precise link-text association"""
        with pdfplumber.open(self.pdf_path) as pdf:
            with open(self.pdf_path, "rb") as f:
                reader = PdfReader(f)
                pages = []
                file_type = os.path.splitext(self.pdf_path)[1].lower()
                processed_timestamp = datetime.datetime.utcnow().isoformat() + "Z"

                for i, (pl_page, pyp_page) in enumerate(zip(pdf.pages, reader.pages)):
                    # Extract full page text
                    page_text = pl_page.extract_text() or ""
                    # Extract words with coordinates (each word: dict with x0, top, x1, bottom, text)
                    words = pl_page.extract_words()
                    links = []
                    seen_links = set()

                    # Use pypdf to get link annotations (if any)
                    if "/Annots" in pyp_page:
                        annots = pyp_page["/Annots"]
                        for annot in annots:
                            annot_obj = annot.get_object()
                            if annot_obj.get("/Subtype") == "/Link":
                                action = annot_obj.get("/A")
                                if action and action.get("/URI"):
                                    uri = action.get("/URI")
                                    rect = annot_obj.get("/Rect")
                                    # rect is [x0, y0, x1, y1] in PDF coordinates (origin at lower-left)
                                    # Convert to pdfplumber coordinates (origin at top-left)
                                    page_height = pl_page.height
                                    x0, y0, x1, y1 = rect
                                    converted_rect = {
                                        "x0": x0,
                                        "top": page_height - y1,
                                        "x1": x1,
                                        "bottom": page_height - y0,
                                    }
                                    anchor_texts = []
                                    for word in words:
                                        # Check for intersection between the word's bounding box and the link rectangle
                                        if (
                                            word["x0"] <= converted_rect["x1"]
                                            and word["x1"] >= converted_rect["x0"]
                                            and word["top"] <= converted_rect["bottom"]
                                            and word["bottom"] >= converted_rect["top"]
                                        ):
                                            anchor_texts.append(word["text"].strip())
                                    final_text = " ".join(anchor_texts).strip()
                                    if (
                                        final_text
                                        and (final_text, uri) not in seen_links
                                    ):
                                        seen_links.add((final_text, uri))
                                        links.append({"text": final_text, "url": uri})

                    pages.append(
                        {"page_number": i + 1, "text": page_text, "links": links}
                    )

        return {
            "metadata": {
                "total_pages": len(pages),
                "file_type": file_type,
                "processed_at": processed_timestamp,
            },
            "pages": pages,
        }
