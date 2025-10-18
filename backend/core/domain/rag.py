from enum import StrEnum

from pydantic import BaseModel, Field


class MatchRecommendation(StrEnum):
    STRONG_FIT = "strong_fit"
    MODERATE_FIT = "moderate_fit"
    WEAK_FIT = "weak_fit"


class MatchStrength(BaseModel):
    category: str = Field(description="Strength category (e.g., 'Technical Skills', 'Experience Level')")
    detail: str = Field(description="Specific detail from resume")
    relevance_score: float = Field(ge=0.0, le=1.0, description="How relevant this strength is (0.0-1.0)")


class MatchConcern(BaseModel):
    category: str = Field(description="Concern category (e.g., 'Missing Skill', 'Experience Gap')")
    detail: str = Field(description="Specific concern")
    severity: str = Field(description="Impact level: 'critical', 'moderate', or 'minor'")
    mitigation: str | None = Field(default=None, description="How candidate might address this gap")


class JobMatchExplanation(BaseModel):
    match_score: float = Field(ge=0.0, le=1.0, description="Overall match score (0.0-1.0)")
    recommendation: MatchRecommendation = Field(description="Hiring recommendation category")
    strengths: list[MatchStrength] = Field(
        min_length=1, max_length=5, description="Key strengths (1-5 items, ordered by relevance)"
    )
    concerns: list[MatchConcern] = Field(max_length=5, description="Areas of concern (0-5 items, ordered by severity)")
    summary: str = Field(min_length=50, max_length=500, description="2-3 sentence executive summary")
    key_discussion_points: list[str] = Field(max_length=3, description="Top 3 topics to discuss in interview")


class CandidateScore(BaseModel):
    uid: str
    name: str
    technical_skills: float = Field(ge=0.0, le=10.0, description="Technical skill match (0-10)")
    experience_level: float = Field(ge=0.0, le=10.0, description="Experience relevance (0-10)")
    domain_expertise: float = Field(ge=0.0, le=10.0, description="Domain knowledge fit (0-10)")
    cultural_indicators: float = Field(ge=0.0, le=10.0, description="Cultural alignment signals (0-10)")
    overall_score: float = Field(ge=0.0, le=10.0, description="Weighted average of all dimensions")


class DimensionComparison(BaseModel):
    dimension: str = Field(description="Dimension name (e.g., 'Python Expertise')")
    candidates: dict[str, str] = Field(
        description=(
            "Dictionary with candidate UIDs as keys and assessment text as values. "
            "KEYS MUST BE: The exact UUID strings from the candidate data (e.g., '2bf27a35-d4d1-4df3-8e3f-ba79075aa99e'). "
            "VALUES MUST BE: Assessment text describing their strength (e.g., 'Strong React expertise with 5+ years experience'). "
            "DO NOT use 'Candidate 1', 'Candidate 2', names, or any other identifier as keys. "
            "DO NOT put UIDs as values."
        ),
        json_schema_extra={
            "examples": [
                {
                    "2bf27a35-d4d1-4df3-8e3f-ba79075aa99e": "Strong React and Next.js skills with production experience",
                    "244a047a-b2b6-439f-a508-57bc1cb7552a": "Solid Python and NLP background, limited frontend experience",
                }
            ]
        },
    )
    winner: str = Field(description="UID of strongest candidate in this dimension (exact UUID string)")
    analysis: str = Field(max_length=200, description="Brief comparison analysis for this dimension")


class ComparisonRecommendation(BaseModel):
    scenario: str = Field(description="Hiring scenario (e.g., 'Immediate Impact', 'Long-term Growth')")
    recommended_uid: str
    recommended_name: str
    rationale: str = Field(max_length=200)


class RiskAssessment(BaseModel):
    uid: str = Field(description="Candidate UID")
    risk: str = Field(max_length=300, description="Risk/concern summary for this candidate")


class CandidateComparison(BaseModel):
    executive_summary: str = Field(
        min_length=100, max_length=400, description="2-3 sentence positioning of each candidate's core strength"
    )
    scores: list[CandidateScore] = Field(min_length=2, max_length=5, description="Scores for each candidate")
    dimension_comparisons: list[DimensionComparison] = Field(
        min_length=4, max_length=8, description="Head-to-head comparisons across key dimensions"
    )
    recommendations: list[ComparisonRecommendation] = Field(
        min_length=2, max_length=4, description="Scenario-based recommendations"
    )
    risk_assessment: list[RiskAssessment] = Field(
        min_length=2, max_length=5, description="Risk assessments for each candidate"
    )
    ranked_uids: list[str] = Field(description="UIDs ordered by overall_score (highest first)")


class QuestionCategory(StrEnum):
    TECHNICAL_DEEP_DIVE = "technical_deep_dive"
    BEHAVIORAL = "behavioral"
    PROJECT_ARCHITECTURE = "project_architecture"
    PROBLEM_SOLVING = "problem_solving"
    SYSTEM_DESIGN = "system_design"


class SeniorityLevel(StrEnum):
    JUNIOR = "junior"
    MID_LEVEL = "mid_level"
    SENIOR = "senior"
    STAFF_PLUS = "staff_plus"


class InterviewQuestion(BaseModel):
    category: QuestionCategory
    question: str = Field(min_length=30, max_length=500, description="Interview question")
    assesses: str = Field(max_length=150, description="What skill/knowledge this question validates")
    follow_ups: list[str] = Field(min_length=1, max_length=4, description="Probing follow-up questions")
    red_flags: list[str] = Field(min_length=1, max_length=3, description="Warning signs in candidate's answer")
    good_answer_indicators: list[str] = Field(min_length=1, max_length=3, description="Signs of a strong answer")
    difficulty_level: SeniorityLevel = Field(description="Appropriate difficulty for candidate's level")
    time_estimate_minutes: int = Field(ge=2, le=15, description="Estimated time to discuss this question")


class InterviewQuestionSet(BaseModel):
    candidate_uid: str
    candidate_name: str
    candidate_summary: str = Field(max_length=200, description="Brief summary of candidate's background")
    seniority_level: SeniorityLevel
    questions: list[InterviewQuestion] = Field(
        min_length=6, max_length=12, description="6-12 interview questions covering different categories"
    )
    recommended_duration_minutes: int = Field(ge=30, le=90, description="Total recommended interview time")
    focus_areas: list[str] = Field(max_length=5, description="Key areas to probe based on resume")
    preparation_notes: str = Field(max_length=300, description="Interviewer prep notes about candidate")
