import json
import logging
from datetime import datetime

from django.conf import settings

from core.domain import REVIEW_CRITERIA, Resume, ReviewResult
from core.domain.extraction import ParsedDocument

from .llm_service import LLMService

logger = logging.getLogger(__name__)


class ReviewService:
    """
    Resume review service using structured Pydantic models.
    """

    def __init__(self, parsed_document: ParsedDocument, structured_data: Resume):
        self.parsed_document = parsed_document
        self.structured_data = structured_data.model_dump()
        self.current_date = datetime.now().strftime("%m.%Y")
        self.full_text = self._extract_full_text()
        # Additional metadata from parsed document
        self.file_type = parsed_document.file_type
        self.processed_at = parsed_document.processed_at

        self.llm_service = LLMService(
            system_prompt=self._get_system_prompt(),
            result_type=ReviewResult,
            mode="text"
        )

    def _get_system_prompt(self) -> str:
        return """
        You are a professional resume reviewer evaluating resume quality.

        For each section, provide feedback in three categories:
        - must: Critical issues that MUST be fixed (return null if none)
        - should: Important recommendations (return null if none)
        - advise: Optional improvements (return null if none)

        Guidelines:
        - Only report genuine issues - return null for good sections
        - Be specific and actionable
        - Do not invent problems
        - Focus on quality and professionalism

        Return a structured ReviewResult following the schema.
        """

    def _extract_full_text(self) -> str:
        # ParsedDocument always has pages list, no need to check
        return "\n".join(
            page.text  # Direct access since Page always has text attribute
            for page in self.parsed_document.pages
        )

    def _build_review_prompt(self) -> str:
        sections_to_review = []

        # Only include sections that exist in the resume
        for key, criteria in REVIEW_CRITERIA.items():
            if key in self.structured_data and self.structured_data[key]:
                section_data = json.dumps(
                    {key: self.structured_data[key]},
                    ensure_ascii=False,
                    default=str
                )

                sections_to_review.append(f"""
                SECTION: {criteria.section_name}

                Evaluation Criteria:
                - MUST: {criteria.must_criteria}
                - SHOULD: {criteria.should_criteria}
                - ADVISE: {criteria.advise_criteria}

                Section Data:
                {section_data}
                """)

        return f"""
        Review this resume based on current date: {self.current_date}
        Document type: {self.file_type}, Processed: {self.processed_at}

        Full Resume Text:
        {self.full_text[:settings.MAX_TOKENS_IN_RESUME_TO_PROCESS]}

        SECTIONS TO REVIEW:
        {"".join(sections_to_review)}

        Evaluate each section against its criteria.
        Return null for any category without issues.
        Provide specific, actionable feedback only for real problems.
        """

    async def iterative_review(self) -> ReviewResult:
        """
        Perform iterative review of resume sections.

        Returns:
            Structured ReviewResult as dict
        """
        try:
            prompt = self._build_review_prompt()
            result = await self.llm_service.run(prompt, temperature=0.3)
            logger.info("Resume review completed successfully")
            return result  # type: ignore[no-any-return]

        except Exception as e:
            logger.error(f"Review generation failed: {e}")
            return ReviewResult()
