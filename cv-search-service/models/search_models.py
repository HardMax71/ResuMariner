from typing import Dict, List, Any, Optional

from pydantic import BaseModel, Field, field_validator, model_validator


class SearchMatch(BaseModel):
    """Individual match from search results"""
    text: str = Field(..., description="Matching text")
    score: float = Field(..., description="Similarity score")
    source: str = Field(..., description="Source of text (job, project, etc)")
    context: str = Field("", description="Context for the text")


class JobExperience(BaseModel):
    """Job experience for search results"""
    company: str
    position: str
    duration_months: int  # Integer type for duration_months
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    employment_type: Optional[str] = None
    work_mode: Optional[str] = None


class SearchResult(BaseModel):
    """Individual CV search result"""
    cv_id: str = Field(..., description="CV identifier")
    person_name: str = Field(..., description="Person name")
    email: str = Field(..., description="Email address")
    score: float = Field(..., description="Overall similarity score")
    matches: List[SearchMatch] = Field(..., description="List of matching text segments")
    summary: Optional[str] = Field(None, description="CV summary")
    skills: Optional[List[str]] = Field(None, description="List of skills")
    experiences: Optional[List[JobExperience]] = Field(None, description="List of experiences")
    education: Optional[List[Dict[str, Any]]] = Field(None, description="List of education")
    years_experience: Optional[float] = Field(None, description="Years of experience")
    location: Optional[Dict[str, Optional[str]]] = Field(None, description="Location information")
    desired_role: Optional[str] = Field(None, description="Desired role")


class VectorSearchQuery(BaseModel):
    """Request model for semantic search"""
    query: str = Field(..., description="Search query text")
    limit: int = Field(10, description="Maximum number of results to return")
    min_score: float = Field(0.0, description="Minimum similarity score (0-1)")
    filters: Optional[Dict[str, Any]] = Field(None, description="Optional filters for search")

    @field_validator("query")
    def query_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Search query cannot be empty")
        return v.strip()


class GraphSearchQuery(BaseModel):
    """Request model for structured search"""
    skills: Optional[List[str]] = Field(None, description="Skills to search for")
    technologies: Optional[List[str]] = Field(None, description="Technologies to search for")
    role: Optional[str] = Field(None, description="Desired role to search for")
    company: Optional[str] = Field(None, description="Company to search for")
    location: Optional[str] = Field(None, description="Location to search for")
    years_experience: Optional[int] = Field(None, description="Minimum years of experience")
    limit: int = Field(10, description="Maximum number of results to return")

    @model_validator(mode="after")
    def check_at_least_one_param(self) -> "GraphSearchQuery":
        if not any([
            self.skills,
            self.technologies,
            self.role,
            self.company,
            self.location,
            self.years_experience,
        ]):
            raise ValueError("At least one search parameter must be provided")
        return self


class HybridSearchQuery(BaseModel):
    """Request model for hybrid search (combining semantic and structured)"""
    query: str = Field(..., description="Semantic search query")
    skills: Optional[List[str]] = Field(None, description="Skills to filter by")
    technologies: Optional[List[str]] = Field(None, description="Technologies to filter by")
    role: Optional[str] = Field(None, description="Desired role to filter by")
    company: Optional[str] = Field(None, description="Company to filter by")
    location: Optional[str] = Field(None, description="Location to filter by")
    vector_weight: float = Field(0.7, description="Weight for vector search (0-1)")
    graph_weight: float = Field(0.3, description="Weight for graph search (0-1)")
    limit: int = Field(10, description="Maximum number of results to return")

    @field_validator('vector_weight', 'graph_weight')
    def weights_in_range(cls, v: float) -> float:
        if not 0 <= v <= 1:
            raise ValueError("Weights must be between 0 and 1")
        return v


class SearchResponse(BaseModel):
    """Response model for search operations"""
    results: List[SearchResult] = Field(..., description="Search results")
    total: int = Field(..., description="Total number of results")
    query: str = Field(..., description="Original query")
    search_type: str = Field(..., description="Type of search performed")
    execution_time: float = Field(..., description="Search execution time in seconds")


class FilterOption(BaseModel):
    """Model for a filter option"""
    value: str = Field(..., description="Filter value")
    count: int = Field(..., description="Number of CVs with this value")


class FilterOptions(BaseModel):
    """Response model for available filter options"""
    skills: List[FilterOption] = Field(default_factory=list, description="Available skills")
    technologies: List[FilterOption] = Field(default_factory=list, description="Available technologies")
    roles: List[FilterOption] = Field(default_factory=list, description="Available roles")
    companies: List[FilterOption] = Field(default_factory=list, description="Available companies")
    locations: List[FilterOption] = Field(default_factory=list, description="Available locations")