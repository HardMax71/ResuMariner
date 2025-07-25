from datetime import datetime
from enum import Enum
from typing import Dict, Any, Optional
import os

from pydantic import BaseModel, Field, field_validator
from fastapi import UploadFile

# File validation constants - defined outside class for Pydantic v2 compatibility
ALLOWED_EXTENSIONS = {".pdf", ".jpg", ".jpeg", ".png", ".docx"}
DANGEROUS_CHARS = {"<", ">", ":", '"', "|", "?", "*", "\\", "/", "\x00"}
SUSPICIOUS_PATTERNS = ["../", "..\\"]
FILE_SIGNATURES = {
    ".pdf": b"%PDF-",
    ".jpg": b"\xff\xd8\xff",
    ".jpeg": b"\xff\xd8\xff",
    ".png": b"\x89PNG\r\n\x1a\n",
}
MALWARE_PATTERNS = [
    b"<?php",
    b"<script",
    b"javascript:",
    b"eval(",
    b"cmd.exe",
    b"powershell",
    b"/bin/sh",
]


class JobStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class JobCreate(BaseModel):
    file_path: str

    @field_validator("file_path")
    @classmethod
    def validate_file_path(cls, v):
        if not v or not v.strip():
            raise ValueError("File path cannot be empty")
        return v


class JobUpdate(BaseModel):
    status: Optional[JobStatus] = None
    result: Optional[Dict[str, Any]] = None
    result_url: Optional[str] = None
    error: Optional[str] = None


class Job(BaseModel):
    job_id: str
    status: JobStatus = JobStatus.PENDING
    file_path: str
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    result: Optional[Dict[str, Any]] = None
    result_url: Optional[str] = None
    error: Optional[str] = None
    # Additional fields for compatibility
    user_id: Optional[str] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None

    @field_validator("file_path")
    @classmethod
    def validate_file_path(cls, v):
        if not v or not v.strip():
            raise ValueError("File path cannot be empty")
        return v


class JobResponse(BaseModel):
    job_id: str
    status: JobStatus
    created_at: datetime
    updated_at: datetime
    result_url: Optional[str] = None
    error: Optional[str] = None


class FileUpload(BaseModel):
    """File upload validation model"""

    filename: str = Field(..., min_length=1, max_length=255)
    content: bytes = Field(..., min_length=1024, max_length=10 * 1024 * 1024)
    content_type: Optional[str] = None

    @field_validator("filename")
    @classmethod
    def validate_filename(cls, v):
        # Check dangerous characters using external constants
        if any(char in v for char in DANGEROUS_CHARS):
            raise ValueError("Filename contains dangerous characters")

        # Check suspicious patterns
        if any(pattern in v for pattern in SUSPICIOUS_PATTERNS):
            raise ValueError("Filename contains suspicious patterns")

        # Check extension
        file_ext = os.path.splitext(v)[1].lower()
        if file_ext not in ALLOWED_EXTENSIONS:
            raise ValueError(f"File extension not allowed: {file_ext}")

        return v

    @field_validator("content")
    @classmethod
    def validate_content(cls, v, info):
        if not hasattr(info, "data") or "filename" not in info.data:
            return v

        filename = info.data["filename"]
        file_ext = os.path.splitext(filename)[1].lower()

        # Check file signature
        expected_signature = FILE_SIGNATURES.get(file_ext)
        if expected_signature and not v.startswith(expected_signature):
            raise ValueError(f"Invalid {file_ext} file: missing proper file signature")

        # Check for malware patterns
        if any(pattern in v for pattern in MALWARE_PATTERNS):
            raise ValueError("Suspicious content detected in file")

        # Check for excessive null bytes
        if v.count(b"\x00") > len(v) * 0.5:
            raise ValueError("Excessive null bytes detected")

        return v

    @classmethod
    def from_upload_file(cls, file: UploadFile, content: bytes) -> "FileUpload":
        """Create FileUpload from FastAPI UploadFile"""
        filename = file.filename or "unknown.pdf"  # Default to PDF extension
        return cls(
            filename=filename,
            content=content,
            content_type=file.content_type,
        )
