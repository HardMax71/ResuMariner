import re

from core.domain.extraction import ParsedDocument


def extract_email(parsed_doc: ParsedDocument) -> str | None:
    """Extract first valid email from parsed document.

    Args:
        parsed_doc: Parsed document containing text and links

    Returns:
        Lowercase email address if found, None otherwise
    """
    EMAIL_PATTERN = re.compile(r"\b[A-Za-z0-9][A-Za-z0-9._%+-]*@[A-Za-z0-9][A-Za-z0-9.-]*\.[A-Z|a-z]{2,}\b")

    link_urls = " ".join(link.url for page in parsed_doc.pages for link in page.links)
    page_text = " ".join(filter(None, [page.text for page in parsed_doc.pages]))
    combined_text = link_urls + " " + page_text

    match = EMAIL_PATTERN.search(combined_text)
    return match.group(0).lower() if match else None
