from dataclasses import dataclass, field
from enum import StrEnum

from core.domain.resume import EducationStatus


class SearchType(StrEnum):
    SEMANTIC = "semantic"
    STRUCTURED = "structured"
    HYBRID = "hybrid"


CEFR_ORDER = {"A1": 1, "A2": 2, "B1": 3, "B2": 4, "C1": 5, "C2": 6}


@dataclass
class LanguageRequirement:
    """Represents a language with minimum CEFR level requirement"""

    language: str
    min_cefr: str  # "B2" means B2, C1, or C2


@dataclass
class LocationRequirement:
    """Represents a country with optional cities filter"""

    country: str
    cities: list[str] | None = None  # None or empty list means "any city" in that country


@dataclass
class EducationRequirement:
    """Represents an education level with optional status filter"""

    level: str  # Bachelor, Master, PhD, etc.
    statuses: list[EducationStatus] | None = None  # None or empty list means "any status"


@dataclass
class SearchFilters:
    skills: list[str] | None = None
    role: str | None = None
    company: str | None = None
    locations: list[LocationRequirement] | None = None
    years_experience: int | None = None
    education: list[EducationRequirement] | None = None
    languages: list[LanguageRequirement] | None = None


@dataclass
class FilterOption:
    value: str
    count: int


@dataclass
class LanguageOption:
    """Language with available CEFR levels"""

    language: str
    available_levels: list[str]  # CEFR levels present in data
    resume_count: int


@dataclass
class CountryOption:
    """Country with available cities"""

    country: str
    cities: list[str]  # Cities within this country
    resume_count: int


@dataclass
class EducationLevelOption:
    """Education level with available statuses"""

    level: str
    statuses: list[str]  # Education statuses for this level
    resume_count: int


@dataclass
class FilterOptionsResult:
    skills: list[FilterOption] = field(default_factory=list)
    roles: list[FilterOption] = field(default_factory=list)
    companies: list[FilterOption] = field(default_factory=list)
    countries: list[CountryOption] = field(default_factory=list)
    education_levels: list[EducationLevelOption] = field(default_factory=list)
    languages: list[LanguageOption] = field(default_factory=list)


@dataclass
class VectorHit:
    """Single vector match from Qdrant with full metadata"""

    uid: str
    text: str
    score: float
    source: str  # 'skill', 'employment', 'project', etc
    name: str
    email: str
    context: str | None = None


@dataclass
class ResumeSearchResult:
    """Aggregated search result for a single resume"""

    uid: str
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
    languages: list[dict] | None = None

    def __post_init__(self):
        # Always keep matches sorted descending by score
        self.matches.sort(key=lambda h: h.score, reverse=True)

    @classmethod
    def from_matches(cls, uid: str, hits: list[VectorHit]) -> "ResumeSearchResult":
        """Create ResumeSearchResult from vector matches when not found in graph"""
        if not hits:
            return cls(uid=uid, name="Unknown", email="", score=0.0, matches=[])

        first_hit = hits[0]
        return cls(
            uid=uid,
            name=first_hit.name,
            email=first_hit.email,
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
