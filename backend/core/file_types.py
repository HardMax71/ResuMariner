"""
Centralized file type registry for the entire application.

This module provides a single source of truth for:
- Allowed file extensions
- Media types (MIME types)
- File signatures for validation
- Parser associations
- File type categories
"""
from enum import StrEnum
from typing import TypedDict


class FileCategory(StrEnum):
    """Categories of files we process."""
    DOCUMENT = "document"
    IMAGE = "image"


class ParserType(StrEnum):
    """Available parser types."""
    PDF = "pdf"
    IMAGE = "image"
    # DOCX = "docx"  # Future: when DOCX parser is implemented


class FileTypeSpec(TypedDict):
    """Specification for a file type."""
    media_type: str
    signature: bytes | None
    parser: ParserType
    category: FileCategory
    max_size_mb: int


# Single source of truth for all file types
FILE_TYPE_REGISTRY: dict[str, FileTypeSpec] = {
    ".pdf": {
        "media_type": "application/pdf",
        "signature": b"%PDF-",
        "parser": ParserType.PDF,
        "category": FileCategory.DOCUMENT,
        "max_size_mb": 10,
    },
    ".jpg": {
        "media_type": "image/jpeg",
        "signature": b"\xff\xd8\xff",
        "parser": ParserType.IMAGE,
        "category": FileCategory.IMAGE,
        "max_size_mb": 5,
    },
    ".jpeg": {
        "media_type": "image/jpeg",
        "signature": b"\xff\xd8\xff",
        "parser": ParserType.IMAGE,
        "category": FileCategory.IMAGE,
        "max_size_mb": 5,
    },
    ".png": {
        "media_type": "image/png",
        "signature": b"\x89PNG\r\n\x1a\n",
        "parser": ParserType.IMAGE,
        "category": FileCategory.IMAGE,
        "max_size_mb": 5,
    },
    # Note: .docx support commented out until parser is implemented
    # ".docx": {
    #     "media_type": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    #     "signature": b"PK\x03\x04",  # ZIP file signature (DOCX is ZIP-based)
    #     "parser": ParserType.DOCX,
    #     "category": FileCategory.DOCUMENT,
    #     "max_size_mb": 10,
    # },
}

# Derived constants for backward compatibility
ALLOWED_EXTENSIONS = set(FILE_TYPE_REGISTRY.keys())
ALLOWED_IMAGE_EXTENSIONS = {
    ext for ext, spec in FILE_TYPE_REGISTRY.items()
    if spec["category"] == FileCategory.IMAGE
}
ALLOWED_DOCUMENT_EXTENSIONS = {
    ext for ext, spec in FILE_TYPE_REGISTRY.items()
    if spec["category"] == FileCategory.DOCUMENT
}

# Media type mappings for easy lookup
MEDIA_TYPE_MAPPING = {
    ext: spec["media_type"]
    for ext, spec in FILE_TYPE_REGISTRY.items()
}

# File signatures for validation
FILE_SIGNATURES = {
    ext: spec["signature"]
    for ext, spec in FILE_TYPE_REGISTRY.items()
    if spec["signature"] is not None
}

# Security patterns (centralized from serializers)
DANGEROUS_CHARS = {"<", ">", ":", '"', "|", "?", "*", "\\", "/", "\x00"}
SUSPICIOUS_PATH_PATTERNS = ["../", "..\\"]
MALWARE_PATTERNS = [
    b"<?php",
    b"<script",
    b"javascript:",
    b"eval(",
    b"cmd.exe",
    b"powershell",
    b"/bin/sh",
]


def get_media_type(extension: str, default: str = "application/octet-stream") -> str:
    """Get media type for an extension with fallback."""
    return MEDIA_TYPE_MAPPING.get(extension.lower(), default)


def get_parser_type(extension: str) -> ParserType | None:
    """Get parser type for an extension."""
    spec = FILE_TYPE_REGISTRY.get(extension.lower())
    return spec["parser"] if spec else None


def validate_file_signature(extension: str, content: bytes) -> bool:
    """Validate file content matches expected signature."""
    signature = FILE_SIGNATURES.get(extension.lower())
    if signature is None:
        return True  # No signature to check
    return content.startswith(signature)
