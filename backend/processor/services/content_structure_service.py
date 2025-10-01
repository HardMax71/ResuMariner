import json
import logging
from datetime import datetime

from django.conf import settings

from core.domain import Resume
from core.domain.extraction import ParsedDocument

from .llm_service import LLMService


class LLMContentStructureService:
    def __init__(self, pdf_parser_output: ParsedDocument):
        self.raw_data = pdf_parser_output
        self.current_date = datetime.now().strftime("%B %d, %Y")

        system_prompt = (
            "You are a resume parser. Extract information from resumes and return structured data "
            "exactly matching the schema."
        )
        self.llm_service = LLMService(system_prompt=system_prompt, result_type=Resume)

    def _prepare_prompt(self, text: str, links: list[dict]) -> str:
        return f"""
Today's date: {self.current_date}

CRITICAL PROCESSING RULES:
- RETURN JSON WITH FILLED IN DATA, DO NOT RETURN JSON WITH SCHEMA AND WITHOUT ANY DATA!
- CONTENT VALUES PRESERVE ORIGINAL LANGUAGE
- **TRANSLATION REQUIREMENT**: ALL locations (city, country), languages (language names), roles (desired_role),
  and skills MUST BE TRANSLATED TO ENGLISH if found in a non-English language. Use the standard English names.
  Examples: "Москва" → "Moscow", "Español" → "Spanish", "Python разработчик" → "Python Developer"
- USE DEFAULT FORMATTING AND CAPITALIZATION, NO EXCESSIVE CAPSLOCK USAGE
- IF CONTENT VALUE HAS REQUIREMENT HOW TO RETURN DATA, IN PARTICULAR - SEPARATORS, USE THEM
- IF SOME DATA INTERFERES WITH POSSIBLE VALUES FOR KEYS (SAY, ONE OF PROPOSED) BUT IRL IT'S NOT, -
  SET THE ACTUAL VALUE.
- IF PROVIDED JSON WITH DATA IS MALFORMED (E.G. SINGLE QUOTES INSTEAD OF DOUBLE QUOTES) - FIX IT.
- IF KEY POINTS HAVE DELIMITERS LIKE '-', '.', AND SUCH BEFORE ACTUAL TEXT - REMOVE THEM

URL HANDLING RULES:
- EXTRACT ALL URLS FROM THE 'Provided URLs' SECTION.
- FOR EACH URL, ANALYZE ITS CONTENT AND CONTEXT:
    - IF THE URL CONTAINS INDICATORS OF A COMPANY PROFILE (E.G., 'linkedin.com/company/')
      AND THE COMPANY NAME IS MENTIONED IN THE RESUME, ASSIGN THIS URL TO THAT COMPANY'S "company_url" FIELD.
    - IF THE URL INDICATES A PROJECT OR CODE REPOSITORY (E.G., CONTAINS 'github.com' OR IS CLEARLY RELATED TO A
      PROJECT NAME), ASSIGN THIS URL TO THE CORRESPONDING PROJECT'S "url" FIELD.
    - IF A URL IS AMBIGUOUS OR DOES NOT CLEARLY MATCH A SPECIFIC ENTITY, PLACE IT UNDER THE "other_links" FIELD
      WITH A SUITABLE LABEL.
- ENSURE THAT NO URL IS LEFT UNMAPPED OR DUPLICATED:
    - IF A URL CAN BE ACCURATELY ASSOCIATED WITH A SPECIFIC ENTITY (COMPANY OR PROJECT), IT MUST ONLY APPEAR IN
      THAT ENTITY'S FIELD.
    - DO NOT INCLUDE COMPANY OR PROJECT URLS IN THE "other_links" FIELD. ONLY THOSE URLS THAT CANNOT BE ATTRIBUTED
      ELSEWHERE SHOULD REMAIN IN "other_links".
- WHEN MAPPING, USE EXACT STRING MATCHES FOR ENTITY NAMES FROM THE RESUME. IF A URL IS AMBIGUOUS, USE THE CONTEXT
  OF THE SURROUNDING TEXT TO MAKE THE BEST ASSIGNMENT.

Validation Guardrails:
- Company names must match exactly (case-sensitive)
- Skills include ALL technical and soft capabilities (Python, React, Docker, Leadership, etc.)
- Links must exist in original document
- Extract skills from ANY mention: skills sections, tech stacks, tool lists, technologies used

SECTION-SPECIFIC RULES:

PERSONAL INFO:
- Location: TRANSLATE city and country names to English (e.g., "Paris, France" not "Paris, Frankreich")
- Personal name: Capitalize first letters (e.g., John Doe)
- If employment types are not explicitly specified - put a list of all possible employment types,
  same applies to work modes.

EXPERIENCE/EMPLOYMENT_HISTORY:
- CRITICAL: Only include actual work experience, internships, and professional positions.
- DO NOT include education (degrees, university attendance) as employment history.
- Education (Bachelor's, Master's, PhD, etc.) must ONLY go in the education section, never in employment_history.
- Responsibilities: Use exact bullet points verbatim.
- Skills: Extract ALL technologies, tools, frameworks, languages mentioned (Stack:, Technologies:, Tools:, etc.)
  and TRANSLATE to English (e.g., "реакт" → "React", "питон" → "Python")
- If a starting month is not explicitly mentioned (e.g., "2022 - Present"), ASSUME "01.2022 - Present".

EDUCATION:
- Status: Convert to one of the allowed English statuses.
- Qualification: Use the degree title (e.g., Bachelor, Master) rather than the study field.
- Any coursework mentioned should go to the "coursework" field, not "extras".
- If location of university isn't explicitly specified, try to guess based on the country/name of the university.
  Guess must be 99%+ correct, so if you're unsure, set all fields in location to null.


PROJECTS:
- Only include personal projects that are explicitly stated as pet projects or were completed outside of employment.
- DO NOT duplicate any project details already present in the employment_history section.
- Skills: Extract ALL technologies, tools, frameworks mentioned in each project and TRANSLATE to English
- If no qualifying projects are mentioned, set "projects" to null.

LANGUAGE PROFICIENCY:
- Convert any proficiency descriptions to the CEFR level (A1, A2, B1, B2, C1, C2, or Native).
- TRANSLATE all language names to English (e.g., "Français" → "French", "中文" → "Chinese")

LOCATION:
- TRANSLATE all city and country names to English (e.g., "München" → "Munich", "Deutschland" → "Germany")
- If only the country is specified, set "city" to null. Do not copy the country name into the city or state
  fields unless explicitly provided.

CERTIFICATIONS:
- If no certifications are mentioned, set "certifications" to null.

VALIDATION METADATA RULES:
1. COUNT AND REPORT:
   - The exact number of characters in the provided resume text (excluding whitespace)
   - The exact number of links from the 'Provided URLs' section
2. NEVER REPORT 0 UNLESS THE INPUT IS TRULY EMPTY.

Current input stats for reference:
- Resume text length: {len("".join(text.split()))} characters
- Number of provided links: {len(links)}

Return JSON with the following structure (KEYS IN ENGLISH, VALUES IN ORIGINAL LANGUAGE UNLESS SPECIFIED OTHERWISE):
{json.dumps(Resume.model_json_schema())}

Provided URLs:
{links}

Resume Text (PROCESS VERBATIM):
{text[: settings.MAX_TOKENS_IN_RESUME_TO_PROCESS]}
"""

    async def structure_content(self) -> Resume:
        full_text = "\n".join(p.text for p in self.raw_data.pages)
        links = [{"text": link.text, "url": link.url} for page in self.raw_data.pages for link in page.links]
        try:
            prompt = self._prepare_prompt(full_text, links)
            result = await self.llm_service.run(prompt)
            logging.info("Successfully structured resume content")
            return result  # type: ignore[no-any-return]

        except Exception as e:
            logging.error(f"Content structuring failed: {str(e)}")
            return await self._handle_error(full_text, links)

    async def _handle_error(self, text: str, links: list[dict]) -> Resume:
        retry_system_prompt = (
            "You are a specialized resume parser. Extract exact information from resumes "
            "and return a fully compliant JSON object matching the schema. "
        )

        retry_service = LLMService(system_prompt=retry_system_prompt, result_type=Resume)

        enhanced_prompt = (
            "IMPORTANT: Return a valid JSON object matching the Resume schema exactly.\n\n"
            "Focus on these common issues:\n"
            "1. All required fields must be present\n"
            "2. Format dates as MM.YYYY\n"
            "3. Use null for missing values, not empty strings\n"
            "4. Use exactly the enum values specified\n\n"
        ) + self._prepare_prompt(text, links)

        result = await retry_service.run(enhanced_prompt, temperature=0.1)
        return result  # type: ignore[no-any-return]
