from datetime import datetime
from typing import Literal, NamedTuple

from pydantic import BaseModel, Field

from core.domain.resume import Resume
from core.domain.review import ReviewResult


class ProcessingMetadata(BaseModel):
    """Metadata about the processing job."""

    filename: str = ""
    file_ext: str = ""
    source: str = ""
    page_count: int = 0
    graph_stored: bool = False
    vector_stored: bool = False
    vector_count: int = 0
    graph_error: str | None = None
    vector_error: str | None = None
    review_generated: bool = False
    review_error: str | None = None


class ProcessingResult(BaseModel):
    """Complete result from resume processing."""

    resume: Resume
    review: ReviewResult | None = None
    metadata: ProcessingMetadata = Field(default_factory=ProcessingMetadata)


class ResumeResponse(BaseModel):
    """API response for resume endpoints."""

    uid: str = Field(description="Resume unique identifier")
    status: Literal["pending", "processing", "completed", "failed"] = Field(description="Processing status")
    created_at: datetime
    updated_at: datetime
    completed_at: datetime | None = None
    result: ProcessingResult | None = Field(default=None, description="Processing result when completed")
    error: str | None = None


class EmbeddingTextData(NamedTuple):
    text: str
    source: str
    context: str | None = None
