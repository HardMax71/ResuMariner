from dataclasses import dataclass, field
from enum import StrEnum


class SearchType(StrEnum):
    SEMANTIC = "semantic"
    STRUCTURED = "structured"
    HYBRID = "hybrid"


@dataclass
class SearchFilters:
    skills: list[str] | None = None
    technologies: list[str] | None = None
    role: str | None = None
    company: str | None = None
    location: str | None = None
    years_experience: int | None = None


@dataclass
class FilterOption:
    value: str
    count: int


@dataclass
class FilterOptionsResult:
    skills: list[FilterOption] = field(default_factory=list)
    technologies: list[FilterOption] = field(default_factory=list)
    roles: list[FilterOption] = field(default_factory=list)
    companies: list[FilterOption] = field(default_factory=list)
    locations: list[FilterOption] = field(default_factory=list)


@dataclass
class VectorHit:
    """Single vector match from Qdrant with full metadata"""

    resume_id: str
    text: str
    score: float
    source: str  # 'skill', 'employment', 'project', etc
    context: str | None = None
    name: str | None = None
    email: str | None = None


@dataclass
class ResumeSearchResult:
    """Aggregated search result for a single resume"""

    resume_id: str
    name: str
    email: str
    score: float
    matches: list[VectorHit] = field(default_factory=list)

    # Optional enrichment from graph
    summary: str | None = None
    skills: list[str] | None = None
    experiences: list[dict] | None = None
    education: list[dict] | None = None
    years_experience: int | None = None
    location: dict | None = None
    desired_role: str | None = None

    def __post_init__(self):
        # Always keep matches sorted descending by score
        self.matches.sort(key=lambda h: h.score, reverse=True)

    @classmethod
    def from_matches(cls, resume_id: str, hits: list[VectorHit]) -> "ResumeSearchResult":
        """Create ResumeSearchResult from vector matches when not found in graph"""
        if not hits:
            return cls(resume_id=resume_id, name="Unknown", email="", score=0.0, matches=[])

        # Get name and email from first hit if available
        first_hit = hits[0]
        return cls(
            resume_id=resume_id,
            name=first_hit.name or "Unknown",
            email=first_hit.email or "",
            score=max(hit.score for hit in hits),
            matches=hits,
        )


@dataclass
class SearchRequest:
    """Unified search request model"""

    search_type: SearchType
    filters: SearchFilters = field(default_factory=SearchFilters)
    query: str | None = None  # useful for semantic and hybrid search
    limit: int = 10
    min_score: float = 0.0
    max_matches_per_result: int = 10  # Maximum matches to return per resume

    # For hybrid search
    vector_weight: float = 0.7
    graph_weight: float = 0.3


@dataclass
class SearchResponse:
    """Complete search response with metadata"""

    results: list[ResumeSearchResult]
    query: str | None  # Optional for structured search
    search_type: SearchType
    total_found: int
