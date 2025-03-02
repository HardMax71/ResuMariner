from enum import Enum
from typing import Dict, Any, Optional

from pydantic import BaseModel, Field


class ParserType(str, Enum):
    """Types of document parsers"""
    PDF = "pdf"
    IMAGE = "image"
    DOCX = "docx"


class ProcessingOptions(BaseModel):
    """Options for CV processing"""
    parallel: bool = Field(False, description="Use parallel processing for data fixing")
    generate_review: bool = Field(True, description="Generate CV review")
    store_in_db: bool = Field(True, description="Store processed data in database")

class ProcessingResult(BaseModel):
    """Result of CV processing"""
    structured_data: Dict[str, Any]
    review: Optional[Dict[str, Any]] = None
    processing_time: float
    metadata: Dict[str, Any] = Field(default_factory=dict)
