from django.core.validators import MaxValueValidator, MinValueValidator
from rest_framework import serializers

from core.domain import SearchFilters, SearchRequest, SearchType
from core.domain.resume import EducationStatus


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
    duration_months = serializers.IntegerField(required=False, allow_null=True)
    start = serializers.CharField(required=False, allow_null=True, help_text="Start date (YYYY.MM)")
    end = serializers.CharField(required=False, allow_null=True, help_text="End date (YYYY.MM or NULL for ongoing)")
    employment_type = serializers.CharField(required=False, allow_null=True)
    work_mode = serializers.CharField(required=False, allow_null=True)
    key_points = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        allow_null=True,
        default=list,
        help_text="Key achievements/responsibilities",
    )


class SearchResultSerializer(serializers.Serializer):
    uid = serializers.CharField(help_text="Resume identifier")
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
    languages = serializers.ListField(
        child=serializers.DictField(), required=False, allow_null=True, help_text="Languages with CEFR levels"
    )


class LanguageRequirementSerializer(serializers.Serializer):
    """Serializer for language with CEFR level requirement."""

    language = serializers.CharField(help_text="Language name (e.g., English, Spanish)")
    min_cefr = serializers.CharField(help_text="Minimum CEFR level (A1, A2, B1, B2, C1, C2)")


class LocationRequirementSerializer(serializers.Serializer):
    """Serializer for country with optional cities filter."""

    country = serializers.CharField(help_text="Country name")
    cities = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        allow_null=True,
        help_text="Optional list of cities in this country (null or empty means any city)",
    )


class EducationRequirementSerializer(serializers.Serializer):
    """Serializer for education level with optional status filter."""

    level = serializers.CharField(help_text="Education level (e.g., Bachelor, Master, PhD)")
    statuses = serializers.ListField(
        child=serializers.ChoiceField(choices=[status.value for status in EducationStatus]),
        required=False,
        allow_null=True,
        help_text="Optional list of statuses (null or empty means any status)",
    )


class SearchFiltersSchema(serializers.Serializer):
    """Serializer for search filter parameters."""

    skills = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        allow_null=True,
        help_text="Skills to filter by (includes technologies)",
    )
    role = serializers.CharField(required=False, allow_null=True, help_text="Desired role to filter by")
    company = serializers.CharField(required=False, allow_null=True, help_text="Company to filter by")
    locations = LocationRequirementSerializer(
        many=True,
        required=False,
        allow_null=True,
        help_text="Location requirements (country + optional cities)",
    )
    years_experience = serializers.IntegerField(
        required=False,
        allow_null=True,
        validators=[MinValueValidator(0), MaxValueValidator(50)],
        help_text="Minimum years of experience",
    )
    education = EducationRequirementSerializer(
        many=True,
        required=False,
        allow_null=True,
        help_text="Education requirements (level + optional statuses)",
    )
    languages = LanguageRequirementSerializer(
        many=True,
        required=False,
        allow_null=True,
        help_text="Language requirements with minimum CEFR levels",
    )

    def to_internal_value(self, data) -> SearchFilters:
        validated = super().to_internal_value(data)
        # Convert education statuses to EducationStatus enums if provided
        if validated.get("education"):
            for edu_req in validated["education"]:
                if edu_req.get("statuses"):
                    edu_req["statuses"] = [EducationStatus(s) for s in edu_req["statuses"]]
        return SearchFilters(**validated)


class VectorSearchQuerySchema(serializers.Serializer):
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
    filters = SearchFiltersSchema(required=False, help_text="Optional filters for search")

    def to_internal_value(self, data) -> SearchRequest:
        validated = super().to_internal_value(data)
        return SearchRequest(
            search_type=SearchType.SEMANTIC,
            query=validated["query"],
            limit=validated["limit"],
            min_score=validated["min_score"],
            max_matches_per_result=validated["max_matches_per_result"],
            filters=validated.get("filters", SearchFilters()),
        )


class GraphSearchQuerySchema(serializers.Serializer):
    query = serializers.CharField(
        required=False, allow_blank=True, default="", help_text="Optional query (not used for structured search)"
    )
    filters = SearchFiltersSchema(required=False, help_text="Search filters")
    limit = serializers.IntegerField(default=10, help_text="Maximum number of results to return")

    def to_internal_value(self, data) -> SearchRequest:
        validated = super().to_internal_value(data)
        return SearchRequest(
            search_type=SearchType.STRUCTURED,
            query=validated.get("query"),  # Include query even if empty
            filters=validated.get("filters", SearchFilters()),
            limit=validated["limit"],
        )


class HybridSearchQuerySchema(serializers.Serializer):
    query = serializers.CharField(help_text="Natural language search query")
    filters = SearchFiltersSchema(
        required=False,
        help_text="Structured filters (skills, location, etc.) - results MUST match these requirements",
    )
    limit = serializers.IntegerField(default=10, help_text="Maximum number of results to return")
    max_matches_per_result = serializers.IntegerField(
        default=10,
        required=False,
        validators=[MinValueValidator(1), MaxValueValidator(100)],
        help_text="Maximum number of matches to return per result",
    )

    def to_internal_value(self, data) -> SearchRequest:
        validated = super().to_internal_value(data)
        return SearchRequest(
            search_type=SearchType.HYBRID,
            query=validated["query"],
            filters=validated.get("filters", SearchFilters()),
            limit=validated["limit"],
            max_matches_per_result=validated["max_matches_per_result"],
        )


class SearchResponseSerializer(serializers.Serializer):
    results = SearchResultSerializer(many=True, help_text="Search results")
    query = serializers.CharField(required=False, allow_null=True, allow_blank=True, help_text="Original query")
    search_type = serializers.CharField(help_text="Type of search performed")


class FilterOptionSerializer(serializers.Serializer):
    value = serializers.CharField(help_text="Filter value")
    count = serializers.IntegerField(help_text="Number of CVs with this value")


class LanguageOptionSerializer(serializers.Serializer):
    language = serializers.CharField(help_text="Language name")
    available_levels = serializers.ListField(child=serializers.CharField(), help_text="CEFR levels available in data")
    resume_count = serializers.IntegerField(help_text="Number of resumes with this language")


class CountryOptionSerializer(serializers.Serializer):
    country = serializers.CharField(help_text="Country name")
    cities = serializers.ListField(child=serializers.CharField(), help_text="Cities in this country")
    resume_count = serializers.IntegerField(help_text="Number of resumes in this country")


class EducationLevelOptionSerializer(serializers.Serializer):
    level = serializers.CharField(help_text="Education level")
    statuses = serializers.ListField(child=serializers.CharField(), help_text="Education statuses for this level")
    resume_count = serializers.IntegerField(help_text="Number of resumes with this level")


class FilterOptionsSerializer(serializers.Serializer):
    skills = FilterOptionSerializer(many=True, default=list, help_text="Available skills (includes technologies)")
    roles = FilterOptionSerializer(many=True, default=list, help_text="Available roles")
    companies = FilterOptionSerializer(many=True, default=list, help_text="Available companies")
    countries = CountryOptionSerializer(many=True, default=list, help_text="Available countries with cities")
    education_levels = EducationLevelOptionSerializer(
        many=True, default=list, help_text="Available education levels with statuses"
    )
    languages = LanguageOptionSerializer(many=True, default=list, help_text="Available languages with CEFR levels")


class VectorHitSerializer(serializers.Serializer):
    uid = serializers.CharField(help_text="Resume identifier")
    text = serializers.CharField(default="", help_text="Matched text fragment")
    score = serializers.FloatField(default=0.0, help_text="Match score")
    source = serializers.CharField(default="unknown", help_text="Source of the fragment")  # type: ignore[assignment]
    context = serializers.CharField(required=False, allow_null=True, default="", help_text="Context of the fragment")  # type: ignore[assignment]
