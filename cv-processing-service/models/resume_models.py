from enum import Enum
from typing import List, Any
from typing import Optional

from pydantic import BaseModel, Field
from pydantic import EmailStr
from pydantic import HttpUrl
from pydantic_extra_types.phone_numbers import PhoneNumber

# -- Common data types ---

DATE_MMYYYY_REGEX = r'^(?:(0[1-9]|1[0-2])\.\d{4}|\d{4})$'
DATE_MMYYYY_OR_CURRENT_REGEX = r'^(?:(0[1-9]|1[0-2])\.\d{4}|\d{4}|current)$'


class WorkMode(str, Enum):
    ONSITE = "onsite"
    HYBRID = "hybrid"
    REMOTE = "remote"


work_mode_values = [mode for mode in WorkMode]


class EmploymentType(str, Enum):
    FULL_TIME = "full-time"
    PART_TIME = "part-time"
    CONTRACT = "contract"


employment_type_values = [mode for mode in EmploymentType]


class EducationStatus(str, Enum):
    COMPLETED = "completed"
    ONGOING = "ongoing"
    INCOMPLETE = "incomplete"


edu_status_values = [mode for mode in EducationStatus]


# --- Reused pydantic models ---

class Location(BaseModel):
    city: str | None = Field(
        ...,
        description="City"
    )
    state: str | None = Field(
        ...,
        description="State"
    )
    country: str | None = Field(
        ...,
        description="Country"
    )


# --- Personal Info Section Models ---

class ContactLinks(BaseModel):
    telegram: HttpUrl | None = Field(
        None,
        description="verbatim URL MUST START WITH with http(s)://t.me or alike if exists else null"
    )
    linkedin: HttpUrl = Field(
        None,
        description="verbatim URL MUST START WITH with http(s):// if exists else null"
    )
    github: HttpUrl | None = Field(
        None,
        description="verbatim URL MUST START WITH with http(s):// if exists else null"
    )
    other_links: dict[str, HttpUrl] | None = Field(
        None,
        description="Other links - if exists, must be a dict of links, where each key is a link name and each value is a valid HTTP URL starting with http(s)://"
    )


class Contact(BaseModel):
    email: EmailStr = Field(
        ...,
        description="verbatim email"
    )
    phone: PhoneNumber | None = Field(
        None,
        description="exact phone string or null if placeholder (+XXXX.., +123456789 or alike) found"
    )
    links: ContactLinks | None = Field(
        ...,
        description="Various contact links"
    )


class WorkAuthorization(BaseModel):
    citizenship: str | None = Field(
        None,
        description="citizenship if mentioned else null"
    )
    work_permit: bool | None = Field(
        None,
        description="true/false/null if insufficient data"
    )
    visa_sponsorship_required: bool | None = Field(
        None,
        description="true/false/null if insufficient data"
    )


class Demographics(BaseModel):
    current_location: Location | None = Field(
        ...,
        description="Current location with city, state, and country"
    )
    work_authorization: WorkAuthorization = Field(
        ...,
        description="Work authorization details including citizenship, work permit, and visa sponsorship."
    )


class PersonalInfo(BaseModel):
    name: str = Field(
        ...,
        description="Exact name header, formatted as 'John Doe' (first letter capitalized, others lowercase unless properly cased). If provided in all caps, adjust formatting accordingly."
    )
    resume_lang: str = Field(
        ...,
        description="ISO 639-1 code of the language used in the resume"
    )
    contact: Contact = Field(
        ...,
        description="Contact information including email, phone, and links."
    )
    demographics: Demographics = Field(
        ...,
        description="Demographic information including current location and work authorization."
    )


# --- Professional Profile Section Models ---

class Preferences(BaseModel):
    role: str = Field(
        ...,
        description="Desired position, with first letter capitalized"
    )
    employment_types: list[EmploymentType] = Field(
        default_factory=lambda: employment_type_values,
        description="Preferred employment types such as full-time, part-time, contract; "
                    "example: [\"full-time\", \"part-time\"]"
    )
    work_modes: list[WorkMode] = Field(
        default_factory=lambda: work_mode_values,
        description="preferred work modes such as remote, onsite, hybrid; "
                    "example: [\"remote\", \"onsite\"]"
    )
    salary: str | None = Field(
        ...,
        description="exact salary text"
    )


class ProfessionalProfile(BaseModel):
    summary: str | None = Field(
        ...,
        description="exact summary text"
    )
    preferences: Preferences = Field(
        ...,
        description="Job preferences including role, employment types, locations, and salary."
    )


# --- Employment History Section Models ---

class EmploymentDuration(BaseModel):
    date_format: str = Field(
        ...,
        description="original date format"
    )
    start: str = Field(
        None,
        pattern=DATE_MMYYYY_REGEX,
        description="start month and year in MM.YYYY format OR just year in YYYY format if month not specified; "
                    "must not be null"
    )
    end: str = Field(
        None,
        pattern=DATE_MMYYYY_OR_CURRENT_REGEX,
        description="end month and year in MM.YYYY format or just year in YYYY format if month not specified, "
                    "'current' if still working; must not be null"
    )
    duration_months: int = Field(
        ...,
        ge=0,
        description="exact number of months as integer >= 0, if 'current time' or alike is mentioned, calculate till current date"
    )


class EmploymentHistoryItem(BaseModel):
    company: str = Field(
        ...,
        description="exact company name"
    )
    company_url: HttpUrl | None = Field(
        None,
        description="company website url"
    )
    position: str = Field(
        ...,
        description="verbatim job title"
    )
    employment_type: EmploymentType = Field(
        default=EmploymentType.FULL_TIME,
        description=f"employment type - exactly one of: {employment_type_values}; "
                    f"by default - full-time"
    )
    work_mode: WorkMode = Field(
        default=WorkMode.ONSITE,
        description=f"work mode - exactly one of: {work_mode_values}; "
                    f"by default - onsite"
    )
    duration: EmploymentDuration = Field(
        ...,
        description="Duration details including date format, start, end, and duration in months."
    )
    location: Location = Field(
        ...,
        description="Job location with city and country"
    )
    key_points: list[str] = Field(
        ...,
        description="Verbatim responsibility/achievement without leading bullet points or separators"
    )
    tech_stack: list[str] = Field(
        ...,
        description="Extract exact technology names, preserving original capitalization, and append versions directly to the name as a single string."
    )


# --- Projects Section Model ---

class Project(BaseModel):
    title: str = Field(
        ...,
        description="exact title"
    )
    url: HttpUrl | None = Field(
        None,
        description="if mentioned, exact url else null"
    )
    tech_stack: list[str] = Field(
        ...,
        description="Extract exact technology names, preserving original capitalization, and append versions directly to the name as a single string."
    )
    key_points: list[str] = Field(
        ...,
        description="Exact verbatim text without leading bullet points or separators"
    )


# --- Education Section Models ---


class EducationItem(BaseModel):
    institution: str = Field(
        ...,
        description="exact name (only include accredited institutions)"
    )
    qualification: str | None = Field(
        ...,
        description="academic degree (e.g., Bachelor, Master; do not include field details; "
                    "if no degree mentioned - that's not education; put it into courses)"
    )
    study_field: str = Field(
        ...,
        description="exact study field (e.g., Chemistry, Computer Science)"
    )
    location: Location | None = Field(
        ...,
        description="Location details with city, state, and country"
    )
    start: str | None = Field(
        None,
        description="MM.YYYY (e.g., 08.2020) or null if not specified",
        pattern=DATE_MMYYYY_REGEX,
    )
    end: Optional[str] = Field(
        None,
        description="MM.YYYY (e.g., 08.2020), 'current', or null if not specified",
        pattern=DATE_MMYYYY_OR_CURRENT_REGEX,
    )
    status: EducationStatus = Field(
        ...,
        description=f"Exactly one of: {edu_status_values}"
    )
    coursework: list[str] | None = Field(
        ...,
        description="exact course work details"
    )
    extras: list[str] | None = Field(
        ...,
        description="verbatim achievements, courses, GPA, etc."
    )


# --- Courses Section Model ---

class Course(BaseModel):
    name: str = Field(
        ...,
        description="exact course name"
    )
    organization: str = Field(
        ...,
        description="exact organization name"
    )
    year: int | None = Field(
        None,
        description="YYYY (integer) or null if not specified"
    )
    course_url: HttpUrl | None = Field(
        None,
        description="url to course or null"
    )
    certificate_url: HttpUrl | None = Field(
        None,
        description="url to completion certificate or null"
    )


# --- Certifications Section Model ---

class Certification(BaseModel):
    name: str = Field(
        ...,
        description="exact name"
    )
    issue_org: str | None = Field(
        None,
        description="exact name or null"
    )
    issue_year: int | None = Field(
        ...,
        description="Issue year in YYYY (integer) or null"
    )
    certificate_link: HttpUrl | None = Field(
        None,
        description="url or null"
    )


# --- Language Proficiency Section Models ---

class ProficiencyLevel(BaseModel):
    self_assessed: str = Field(
        ...,
        description="verbatim level"
    )
    cefr: str = Field(
        pattern=r'^(A1|A2|B1|B2|C1|C2|Native)$',
        description="Language knowledge level in CEFR, one of: A1|A2|B1|B2|C1|C2|Native"
    )


class LanguageProficiencyItem(BaseModel):
    language: str = Field(
        ...,
        description="exact name"
    )
    level: ProficiencyLevel = Field(
        ...,
        description="Language proficiency details with self-assessed level and CEFR equivalent."
    )


# --- Validation Metadata Section Models ---

class Anomaly(BaseModel):
    text_fragment: str = Field(
        ...,
        description="exact text"
    )
    issue: str = Field(
        ...,
        description="description"
    )
    resolution: str = Field(
        ...,
        description="action taken"
    )


class ValidationMetadata(BaseModel):
    text_characters_processed: int = Field(
        ...,
        description="Number of text characters processed"
    )
    links_processed: int = Field(
        ...,
        description="Number of links processed"
    )
    anomalies: List[Anomaly] = Field(
        ...,
        description="List of anomalies with text fragment, issue description, and resolution"
    )


# --- Awards Section Model ---

class AwardType(str, Enum):
    HACKATHON = "hackathon"
    COMPETITION = "competition"
    RECOGNITION = "recognition"
    SCHOLARSHIP = "scholarship"
    OTHER = "other"


award_type_values = [type for type in AwardType]


class Award(BaseModel):
    name: str = Field(
        ...,
        description="Exact name of the award/achievement"
    )
    award_type: AwardType = Field(
        ...,
        description=f"Type of award - exactly one of: {award_type_values}"
    )
    organization: str = Field(
        ...,
        description="Organization/event that issued the award"
    )
    year: int | None = Field(
        None,
        description="Year received (YYYY as integer) or null if not specified"
    )
    position: str | None = Field(
        None,
        description="Position/ranking achieved (e.g., '1st place', 'Finalist') or null if not applicable"
    )
    description: str | None = Field(
        None,
        description="Brief description of the award or achievement"
    )
    url: HttpUrl | None = Field(
        None,
        description="URL to award verification or event page"
    )


# --- Scientific Contributions Section Models ---

class PublicationType(str, Enum):
    JOURNAL_ARTICLE = "journal_article"
    CONFERENCE_PAPER = "conference_paper"
    PATENT = "patent"
    THESIS = "thesis"
    TECHNICAL_REPORT = "technical_report"
    OTHER = "other"


publication_type_values = [type for type in PublicationType]


class ScientificContribution(BaseModel):
    title: str = Field(
        ...,
        description="Exact title of the publication"
    )
    publication_type: PublicationType = Field(
        ...,
        description=f"Type of publication - exactly one of: {publication_type_values}"
    )
    year: int | None = Field(
        None,
        description="Year published (YYYY as integer) or null if not specified"
    )
    venue: str | None = Field(
        None,
        description="Journal name, conference, or publisher"
    )
    doi: str | None = Field(
        None,
        description="Digital Object Identifier (DOI) if available"
    )
    url: HttpUrl | None = Field(
        None,
        description="URL to publication or null"
    )
    description: str | None = Field(
        None,
        description="Brief description if provided"
    )


# --- Top-Level Resume Structure Model ---

class ResumeStructure(BaseModel):
    personal_info: PersonalInfo = Field(
        ...,
        description="Personal information section containing name, resume language, contact, and demographics."
    )
    professional_profile: ProfessionalProfile = Field(
        ...,
        description="Professional profile including summary and job preferences."
    )
    skills: List[str] = Field(
        ...,
        description="List of exact skill names"
    )
    employment_history: List[EmploymentHistoryItem] = Field(
        ...,
        description="List of employment history items with company, position, duration, and related details."
    )
    projects: List[Project] | None = Field(
        None,
        description="List of projects. If no qualifying projects are mentioned, set to null."
    )
    education: List[EducationItem] | None = Field(
        ...,
        description="List of educational background items."
    )
    courses: List[Course] | None = Field(
        ...,
        description="List of courses completed. May be null if nothing is specified."
    )
    certifications: List[Certification] | None = Field(
        ...,
        description="List of certifications with issue details. May be null if nothing is specified."
    )
    language_proficiency: List[LanguageProficiencyItem] | None = Field(
        ...,
        description="List of language proficiencies with levels and certifications. "
                    "May be null if nothing is specified."
    )
    awards: List[Award] | None = Field(
        None,
        description="List of awards, hackathons, competitions, and other achievements. May be null if nothing is specified."
    )
    scientific_contributions: List[ScientificContribution] | None = Field(
        None,
        description="Scientific and research contributions including publications, patents, and research profiles. May be null if nothing is specified."
    )
    validation_metadata: ValidationMetadata = Field(
        ...,
        description="Metadata for validation including text characters processed, links processed, and any anomalies."
    )


# ------

# Define Pydantic models for section correction responses
class CorrectionValuePair(BaseModel):
    before: Any = Field(description="The original value that was corrected")
    after: Any = Field(description="The new value after correction")


class Correction(BaseModel):
    field: str = Field(description="The path to the field that was corrected")
    issue: str = Field(description="Description of the issue that required correction")
    action: str = Field(description="Type of correction action taken")
    values: CorrectionValuePair = Field(description="The before and after values")


class SectionResponse(BaseModel):
    corrections: List[Correction] = Field(default_factory=list,
                                          description="List of corrections made to the section")
    fixed_section: dict = Field(description="The corrected section data")


class ReviewItem(BaseModel):
    """Structured review item with three levels of recommendations"""
    MUST: Optional[str] = Field(None, description="Critical issues that must be addressed")
    SHOULD: Optional[str] = Field(None, description="Recommendations that should be considered")
    ADVISE: Optional[str] = Field(None, description="Optional advice for improvement")


class ReviewResponse(BaseModel):
    """Complete review response containing all resume sections"""
    personal_info: Optional[ReviewItem] = None
    professional_profile: Optional[ReviewItem] = None
    skills: Optional[ReviewItem] = None
    employment_history: Optional[ReviewItem] = None
    projects: Optional[ReviewItem] = None
    education: Optional[ReviewItem] = None
    courses: Optional[ReviewItem] = None
    certifications: Optional[ReviewItem] = None
    language_proficiency: Optional[ReviewItem] = None
    awards: Optional[ReviewItem] = None
    scientific_contributions: Optional[ReviewItem] = None
