from enum import StrEnum

from pydantic import BaseModel, Field


class SeverityLevel(StrEnum):
    MUST = "must"      # Critical issues
    SHOULD = "should"  # Important recommendations
    ADVISE = "advise"  # Optional improvements


class SectionFeedback(BaseModel):
    must: list[str] | None = Field(default=None, description="Critical issues to fix")
    should: list[str] | None = Field(default=None, description="Important recommendations")
    advise: list[str] | None = Field(default=None, description="Optional improvements")


class ReviewCriteria(BaseModel):
    section_name: str
    must_criteria: str
    should_criteria: str
    advise_criteria: str


class ReviewResult(BaseModel):
    personal_info: SectionFeedback | None = None
    professional_profile: SectionFeedback | None = None
    skills: SectionFeedback | None = None
    employment_history: SectionFeedback | None = None
    projects: SectionFeedback | None = None
    education: SectionFeedback | None = None
    courses: SectionFeedback | None = None
    certifications: SectionFeedback | None = None
    language_proficiency: SectionFeedback | None = None
    awards: SectionFeedback | None = None
    scientific_contributions: SectionFeedback | None = None
    overall_score: int | None = Field(default=None, ge=0, le=100)
    summary: str | None = None


REVIEW_CRITERIA = {
    "personal_info": ReviewCriteria(
        section_name="Personal Information",
        must_criteria="Verify email, phone (international format), full name, LinkedIn URL. Technical roles <3 YoE need GitHub.",
        should_criteria="Check name capitalization and contact clarity.",
        advise_criteria="Suggest improvements for missing/ambiguous info."
    ),
    "professional_profile": ReviewCriteria(
        section_name="Professional Profile",
        must_criteria="Ensure realistic career objectives. Report omissions/unclear statements.",
        should_criteria="Check employment type and role consistency.",
        advise_criteria="Suggest details to strengthen profile."
    ),
    "skills": ReviewCriteria(
        section_name="Skills",
        must_criteria="Verify relevance, categorization, alignment with profile. No proficiency levels.",
        should_criteria="Check grouping and formatting.",
        advise_criteria="Suggest categorization improvements."
    ),
    "employment_history": ReviewCriteria(
        section_name="Employment History",
        must_criteria="Verify dates, company, position, responsibilities, tech stack.",
        should_criteria="Ensure XYZ format: 'Accomplished [X] measured by [Y], by doing [Z]'.",
        advise_criteria="Suggest quantifiable achievements."
    ),
    "projects": ReviewCriteria(
        section_name="Projects",
        must_criteria="Ensure relevance and completeness if section exists.",
        should_criteria="Check description clarity and consistency.",
        advise_criteria="Suggest details for underspecified projects."
    ),
    "education": ReviewCriteria(
        section_name="Education",
        must_criteria="Verify institution, qualification, field, dates.",
        should_criteria="Check date formats and degree naming.",
        advise_criteria="For students/new grads, suggest highlighting coursework/thesis."
    ),
    "courses": ReviewCriteria(
        section_name="Courses",
        must_criteria="Verify name, organization, completion year if courses exist.",
        should_criteria="Check naming consistency and URL validity.",
        advise_criteria="Suggest adding URLs or certificates."
    ),
    "certifications": ReviewCriteria(
        section_name="Certifications",
        must_criteria="Verify dates and issuing organizations if certificates exist.",
        should_criteria="Check relevance and currency.",
        advise_criteria="Suggest removing outdated or adding relevant ones."
    ),
    "language_proficiency": ReviewCriteria(
        section_name="Language Proficiency",
        must_criteria="For international experience, verify CEFR levels.",
        should_criteria="Check language naming consistency.",
        advise_criteria="Suggest adding languages for international candidates."
    ),
    "awards": ReviewCriteria(
        section_name="Awards",
        must_criteria="Verify names, organizations, dates.",
        should_criteria="Ensure descriptions are clear and relevant.",
        advise_criteria="Suggest highlighting prestigious/relevant awards."
    ),
    "scientific_contributions": ReviewCriteria(
        section_name="Scientific Contributions",
        must_criteria="Verify publication details, authors, dates.",
        should_criteria="Check formatting consistency.",
        advise_criteria="Suggest organizing by impact/relevance."
    )
}
