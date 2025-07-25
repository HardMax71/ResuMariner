import json
import logging
from datetime import datetime
from typing import Dict

from config import settings
from models.resume_models import ReviewResponse
from services.llm_service import LLMService


class ReviewService:
    def __init__(self, raw_pdf_data: Dict, structured_data):
        """Initialize the review service with PDF and structured data

        Args:
            raw_pdf_data: Raw PDF data with pages containing text
            structured_data: Structured resume data (either Pydantic model or dict)
        """
        self.raw_pdf_data = raw_pdf_data

        # Handle both Pydantic models and dicts
        if hasattr(structured_data, "model_dump"):
            self.structured_data = structured_data.model_dump()
        else:
            self.structured_data = structured_data

        self.current_date = datetime.now().strftime("%m.%Y")

        system_prompt = """You are a professional resume reviewer tasked with evaluating resume quality.

                    For each section, you will provide feedback in three categories:
                    1. MUST: Critical issues that must be addressed (missing information, errors)
                    2. SHOULD: Important recommendations that should be considered
                    3. ADVISE: Optional advice for improvement

                    Follow these guidelines:
                    - Only report genuine issues - if a section is good, return null for that category
                    - Be specific and actionable in your feedback
                    - Do not invent problems that don't exist
                    - Focus on quality, completeness, and professionalism

                    Your response must strictly follow the required Pydantic model structure."""

        self.llm_service = LLMService[ReviewResponse](
            result_type=ReviewResponse, system_prompt=system_prompt
        )

        # Cache full text for reuse
        self.full_text = self._get_full_text()

    def _get_full_text(self) -> str:
        """Extract text content from PDF data"""
        if "pages" in self.raw_pdf_data:
            return "\n".join(p.get("text", "") for p in self.raw_pdf_data["pages"])
        return ""

    def _get_review_rules(self) -> Dict[str, Dict[str, str]]:
        """Get comprehensive review rules for all resume sections"""
        return {
            "personal_info": {
                "MUST": (
                    "Ensure all required personal information is present: valid phone number in international format, "
                    "valid email address, full name. LinkedIn profile URL must be provided. "
                    "For technical positions with <3 YoE, verify GitHub profile is included. "
                    "Report only missing or incorrectly formatted fields."
                ),
                "SHOULD": "Check for consistent capitalization in names and clarity in contact details. Only report discrepancies if found.",
                "ADVISE": "Recommend improvements only if key information is absent or ambiguous.",
            },
            "professional_profile": {
                "MUST": "Ensure career summary and preferences reflect realistic objectives. Report only omissions or unclear statements.",
                "SHOULD": "Check for clarity and consistency in employment types and desired roles. Report any inconsistencies.",
                "ADVISE": "Recommend additional details that would strengthen the professional profile.",
            },
            "skills": {
                "MUST": (
                    "Confirm skills are relevant and properly categorized. Skills should align with professional profile. "
                    "Skills should not include proficiency levels (e.g., 'beginner', 'intermediate'). "
                    "Report missing key skills if evident."
                ),
                "SHOULD": "Check skill grouping and formatting. Report organizational issues.",
                "ADVISE": "Recommend improvements in skill categorization based on career goals.",
            },
            "employment_history": {
                "MUST": (
                    "Verify each employment record includes essential details (dates, company, position, responsibilities) "
                    "and tech stack. Report missing information."
                ),
                "SHOULD": (
                    "Ensure key points are concise and measurable, using XYZ format: "
                    "'Accomplished [X] as measured by [Y], by doing [Z]'. "
                    "Report format inconsistencies."
                ),
                "ADVISE": "Suggest adding quantifiable achievements where appropriate.",
            },
            "projects": {
                "MUST": "If projects section exists, ensure relevance and completeness.",
                "SHOULD": "Review project descriptions for clarity and consistency.",
                "ADVISE": "Recommend additional details for underspecified projects.",
            },
            "education": {
                "MUST": "Ensure educational details (institution, qualification, field, dates) are complete.",
                "SHOULD": "Check date formats, degree naming conventions, and coursework relevance.",
                "ADVISE": "For students/new grads, recommend highlighting relevant coursework or thesis.",
            },
            "courses": {
                "MUST": "Ensure mentioned course entries include name, organization, and completion year."
                "Having any courses mentioned is advised but not mandatory.",
                "SHOULD": "Check consistency in course naming and formatting. Verify URLs are valid.",
                "ADVISE": "Recommend adding course URLs or completion certificate links if missing.",
            },
            "certifications": {
                "MUST": "Verify dates and issuing organizations for certificates, if any certificates are present.",
                "SHOULD": "Review relevance and currency of certifications.",
                "ADVISE": "Suggest removing outdated certifications or adding relevant new ones.",
            },
            "language_proficiency": {
                "MUST": "For international experience, verify standardized proficiency levels (CEFR).",
                "SHOULD": "Check consistency in language naming and levels.",
                "ADVISE": "Recommend adding language skills for candidates with international experience.",
            },
            "awards": {
                "MUST": "Verify award names, organizations, and dates are complete.",
                "SHOULD": "Ensure award descriptions are clear and relevant.",
                "ADVISE": "Suggest highlighting most prestigious or relevant awards.",
            },
            "scientific_contributions": {
                "MUST": "Verify publication details, authors, and dates for accuracy.",
                "SHOULD": "Check formatting consistency across publications and patents.",
                "ADVISE": "Recommend organizing publications by impact or relevance.",
            },
        }

    async def iterative_review(self) -> ReviewResponse:
        """Generate a comprehensive review of the resume

        Returns:
            ReviewResponse: Structured review data as a Pydantic model
        """
        try:
            review_rules = self._get_review_rules()
            keys = [
                k for k in self.structured_data.keys() if k != "validation_metadata"
            ]

            # Prepare structured content for each section
            section_blocks = []
            for key in keys:
                if key in review_rules:
                    rules = review_rules[key]
                    section_data = json.dumps(
                        {key: self.structured_data.get(key)},
                        ensure_ascii=False,
                        default=str,
                    )

                    section_block = f"""
                    SECTION: {key.upper()}

                    Review Guidelines:
                    - MUST: {rules.get("MUST", "Check for critical errors or missing information.")}
                    - SHOULD: {rules.get("SHOULD", "Check for improvements to structure and clarity.")}
                    - ADVISE: {rules.get("ADVISE", "Suggest optional enhancements.")}

                    Section Content:
                    {section_data}
                    """
                    section_blocks.append(section_block)

            all_sections = "\n\n".join(section_blocks)

            # Create the complete prompt
            prompt = f"""Review this resume according to the provided guidelines.

            CURRENT DATE: {self.current_date}

            Full Resume Text:
            {self.full_text[: settings.MAX_TOKENS_IN_RESUME_TO_PROCESS]} 

            RESUME SECTIONS TO REVIEW:
            {all_sections}

            For each section, evaluate against the MUST, SHOULD, and ADVISE criteria.
            If there are no issues in a category, return null for that category.
            Return your analysis as a structured ReviewResponse object following the Pydantic model.
            """

            # Use LLMService wrapper
            response = await self.llm_service.run(prompt, temperature=0.3)
            return response

        except Exception as e:
            logging.error(f"Error generating review: {str(e)}")
            # Return empty review response if error occurs
            return ReviewResponse()
