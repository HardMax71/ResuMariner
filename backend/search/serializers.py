from django.core.validators import MaxValueValidator, MinValueValidator
from rest_framework import serializers

from core.domain import SearchFilters, SearchRequest, SearchType

"""
Note on type ignores for 'source' and 'context' fields:

Django REST Framework's Field base class defines 'source' and 'context' as internal
attributes with specific types (source: Callable[..., Any] | str | None and
context: dict[str, Any]). When we create serializer fields named 'source' or 'context',
mypy incorrectly flags these as type conflicts even though DRF handles this correctly
at runtime.

These are legitimate field names representing data attributes, not the internal
DRF field configuration. The type: ignore comments are necessary because mypy cannot
distinguish between field names and internal attributes in this context.
"""


class SearchMatchSerializer(serializers.Serializer):
    text = serializers.CharField(help_text="Matching text")
    score = serializers.FloatField(help_text="Similarity score")
    source = serializers.CharField(help_text="Source of text (job, project, etc)")  # type: ignore[assignment]
    context = serializers.CharField(
        required=False, allow_null=True, allow_blank=True, default="", help_text="Context for the text"
    )  # type: ignore[assignment]


class JobExperienceSerializer(serializers.Serializer):
    company = serializers.CharField()
    position = serializers.CharField()
    duration_months = serializers.IntegerField()
    start_date = serializers.CharField(required=False, allow_null=True)
    end_date = serializers.CharField(required=False, allow_null=True)
    employment_type = serializers.CharField(required=False, allow_null=True)
    work_mode = serializers.CharField(required=False, allow_null=True)


class SearchResultSerializer(serializers.Serializer):
    resume_id = serializers.CharField(help_text="Resume identifier")
    name = serializers.CharField(help_text="Person name")
    email = serializers.EmailField(help_text="Email address")
    score = serializers.FloatField(help_text="Overall similarity score")
    matches = SearchMatchSerializer(many=True, help_text="List of matching text segments")
    summary = serializers.CharField(required=False, allow_null=True, help_text="Resume summary")
    skills = serializers.ListField(
        child=serializers.CharField(), required=False, allow_null=True, help_text="List of skills"
    )
    experiences = JobExperienceSerializer(many=True, required=False, allow_null=True, help_text="List of experiences")
    education = serializers.ListField(
        child=serializers.DictField(), required=False, allow_null=True, help_text="List of education"
    )
    years_experience = serializers.IntegerField(
        required=False, allow_null=True, validators=[MinValueValidator(0)], help_text="Years of experience"
    )
    location = serializers.DictField(required=False, allow_null=True, help_text="Location information")
    desired_role = serializers.CharField(required=False, allow_null=True, help_text="Desired role")


class SearchFiltersSerializer(serializers.Serializer):
    """Serializer for search filter parameters."""

    skills = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        allow_null=True,
        help_text="Skills to filter by (includes technologies)",
    )
    role = serializers.CharField(required=False, allow_null=True, help_text="Desired role to filter by")
    company = serializers.CharField(required=False, allow_null=True, help_text="Company to filter by")
    location = serializers.CharField(required=False, allow_null=True, help_text="Location to filter by")
    years_experience = serializers.IntegerField(
        required=False,
        allow_null=True,
        validators=[MinValueValidator(0), MaxValueValidator(50)],
        help_text="Minimum years of experience",
    )

    def to_internal_value(self, data):
        validated = super().to_internal_value(data)
        return SearchFilters(**validated)


class VectorSearchQuerySerializer(serializers.Serializer):
    query = serializers.CharField(min_length=1, help_text="Search query text")
    limit = serializers.IntegerField(default=10, help_text="Maximum number of results to return")
    min_score = serializers.FloatField(
        default=0.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        help_text="Minimum similarity score (0-1)",
    )
    max_matches_per_result = serializers.IntegerField(
        default=10,
        required=False,
        validators=[MinValueValidator(1), MaxValueValidator(100)],
        help_text="Maximum number of matches to return per result",
    )
    filters = SearchFiltersSerializer(required=False, help_text="Optional filters for search")

    def to_internal_value(self, data):
        validated = super().to_internal_value(data)
        return SearchRequest(
            search_type=SearchType.SEMANTIC,
            query=validated["query"],
            limit=validated["limit"],
            min_score=validated["min_score"],
            max_matches_per_result=validated["max_matches_per_result"],
            filters=validated.get("filters", SearchFilters()),
        )


class GraphSearchQuerySerializer(serializers.Serializer):
    query = serializers.CharField(
        required=False, allow_blank=True, default="", help_text="Optional query (not used for structured search)"
    )
    filters = SearchFiltersSerializer(required=False, help_text="Search filters")
    limit = serializers.IntegerField(default=10, help_text="Maximum number of results to return")

    def to_internal_value(self, data):
        validated = super().to_internal_value(data)
        return SearchRequest(
            search_type=SearchType.STRUCTURED,
            query=validated.get("query"),  # Include query even if empty
            filters=validated.get("filters", SearchFilters()),
            limit=validated["limit"],
        )


class HybridSearchQuerySerializer(serializers.Serializer):
    query = serializers.CharField(help_text="Semantic search query")
    filters = SearchFiltersSerializer(required=False, help_text="Search filters")
    vector_weight = serializers.FloatField(
        default=0.7,
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        help_text="Weight for vector search (0-1)",
    )
    graph_weight = serializers.FloatField(
        default=0.3,
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        help_text="Weight for graph search (0-1)",
    )
    limit = serializers.IntegerField(default=10, help_text="Maximum number of results to return")
    max_matches_per_result = serializers.IntegerField(
        default=10,
        required=False,
        validators=[MinValueValidator(1), MaxValueValidator(100)],
        help_text="Maximum number of matches to return per result",
    )

    def to_internal_value(self, data):
        validated = super().to_internal_value(data)
        return SearchRequest(
            search_type=SearchType.HYBRID,
            query=validated["query"],
            filters=validated.get("filters", SearchFilters()),
            limit=validated["limit"],
            max_matches_per_result=validated["max_matches_per_result"],
            vector_weight=validated["vector_weight"],
            graph_weight=validated["graph_weight"],
        )


class SearchResponseSerializer(serializers.Serializer):
    results = SearchResultSerializer(many=True, help_text="Search results")
    query = serializers.CharField(required=False, allow_null=True, allow_blank=True, help_text="Original query")
    search_type = serializers.CharField(help_text="Type of search performed")


class FilterOptionSerializer(serializers.Serializer):
    value = serializers.CharField(help_text="Filter value")
    count = serializers.IntegerField(help_text="Number of CVs with this value")


class FilterOptionsSerializer(serializers.Serializer):
    skills = FilterOptionSerializer(many=True, default=list, help_text="Available skills (includes technologies)")
    roles = FilterOptionSerializer(many=True, default=list, help_text="Available roles")
    companies = FilterOptionSerializer(many=True, default=list, help_text="Available companies")
    locations = FilterOptionSerializer(many=True, default=list, help_text="Available locations")


class VectorHitSerializer(serializers.Serializer):
    resume_id = serializers.CharField(help_text="Resume identifier")
    text = serializers.CharField(default="", help_text="Matched text fragment")
    score = serializers.FloatField(default=0.0, help_text="Match score")
    source = serializers.CharField(default="unknown", help_text="Source of the fragment")  # type: ignore[assignment]
    context = serializers.CharField(required=False, allow_null=True, default="", help_text="Context of the fragment")  # type: ignore[assignment]
    name = serializers.CharField(required=False, allow_null=True, default="Unknown", help_text="Person name")
    email = serializers.EmailField(required=False, allow_null=True, default="", help_text="Email")
