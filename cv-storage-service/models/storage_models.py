from typing import Dict, List, Any, Optional

from pydantic import BaseModel, Field, field_validator


class StoreRequest(BaseModel):
    """Request model for storing CV data"""

    job_id: str = Field(..., description="Unique identifier for the CV processing job")
    cv_data: Dict[str, Any] = Field(..., description="Structured CV data")

    @field_validator("cv_data")
    def validate_cv_data(cls, v):
        """Validate CV data has minimum required fields"""
        if not v:
            raise ValueError("CV data cannot be empty")

        # Check for essential fields
        if "personal_info" not in v:
            raise ValueError("CV data must contain personal_info section")

        if "contact" not in v.get("personal_info", {}):
            raise ValueError("CV data must contain personal_info.contact section")

        # Email is optional - the route handles unknown emails
        # if "email" not in v.get("personal_info", {}).get("contact", {}):
        #     raise ValueError("CV data must contain personal_info.contact.email")

        return v


class StoreResponse(BaseModel):
    """Response model for CV storage operation"""

    graph_id: str = Field(..., description="ID of the CV in the graph database")
    vector_count: int = Field(0, description="Number of vector embeddings stored")


class VectorPayload(BaseModel):
    """Individual vector with metadata"""

    vector: List[float] = Field(..., description="Vector embedding")
    text: str = Field(..., description="Text that was embedded")
    person_name: Optional[str] = Field(None, description="Person name")
    email: Optional[str] = Field(None, description="Email address")
    source: str = Field(..., description="Source of text (employment, project, etc.)")
    context: Optional[str] = Field(None, description="Context for the text")


class VectorStoreRequest(BaseModel):
    """Request model for storing pre-computed vectors"""

    cv_id: str = Field(..., description="CV identifier")
    vectors: List[VectorPayload] = Field(
        ..., description="List of vectors with metadata"
    )


class VectorStoreResponse(BaseModel):
    """Response model for vector storage operation"""

    status: str = Field("success", description="Operation status")
    vector_count: int = Field(..., description="Number of vectors stored")
