from enum import StrEnum

from pydantic import BaseModel, Field, model_validator


class EmbeddingVector(BaseModel):
    vector: list[float]
    text: str
    source: str
    context: str | None = None
    name: str | None = None
    email: str | None = None
    # Searchable metadata fields
    skills: list[str] = Field(default_factory=list)
    technologies: list[str] = Field(default_factory=list)
    companies: list[str] = Field(default_factory=list)
    role: str | None = None
    location: str | None = None
    years_experience: int = 0


class WorkMode(StrEnum):
    ONSITE = "onsite"
    HYBRID = "hybrid"
    REMOTE = "remote"


class EmploymentType(StrEnum):
    FULL_TIME = "full-time"
    PART_TIME = "part-time"
    CONTRACT = "contract"


class EducationStatus(StrEnum):
    COMPLETED = "completed"
    ONGOING = "ongoing"
    INCOMPLETE = "incomplete"


class AwardType(StrEnum):
    HACKATHON = "hackathon"
    COMPETITION = "competition"
    RECOGNITION = "recognition"
    SCHOLARSHIP = "scholarship"
    OTHER = "other"


class PublicationType(StrEnum):
    JOURNAL_ARTICLE = "journal_article"
    CONFERENCE_PAPER = "conference_paper"
    PATENT = "patent"
    THESIS = "thesis"
    TECHNICAL_REPORT = "technical_report"
    OTHER = "other"


class Location(BaseModel):
    city: str | None = None
    state: str | None = None
    country: str | None = None


class ContactLinks(BaseModel):
    telegram: str | None = None
    linkedin: str | None = None
    github: str | None = None
    other_links: dict[str, str] | None = None


class Contact(BaseModel):
    email: str
    phone: str | None = None
    links: ContactLinks | None = None


class WorkAuthorization(BaseModel):
    citizenship: str | None = None
    work_permit: bool | None = None
    visa_sponsorship_required: bool | None = None


class Demographics(BaseModel):
    current_location: Location | None = None
    work_authorization: WorkAuthorization | None = None


class PersonalInfo(BaseModel):
    name: str
    resume_lang: str
    contact: Contact
    demographics: Demographics | None = None

    @model_validator(mode="before")
    @classmethod
    def accept_legacy_demographics(cls, v: dict):
        if isinstance(v, dict) and ("current_location" in v or "work_authorization" in v):
            demo = v.get("demographics") or {}
            if "current_location" in v and "current_location" not in demo:
                demo["current_location"] = v.pop("current_location")
            if "work_authorization" in v and "work_authorization" not in demo:
                demo["work_authorization"] = v.pop("work_authorization")
            v["demographics"] = demo
        if isinstance(v, dict) and "links" in v.get("contact", {}):
            links = v["contact"].pop("links")
            v["contact"]["links"] = links
        return v


class JobPreferences(BaseModel):
    role: str
    employment_types: list[EmploymentType] = Field(default_factory=list)
    work_modes: list[WorkMode] = Field(default_factory=list)
    salary: str | None = None


class CompanyInfo(BaseModel):
    name: str
    url: str | None = None


class EmploymentDuration(BaseModel):
    date_format: str
    start: str
    end: str
    duration_months: int


class KeyPoint(BaseModel):
    text: str


class Technology(BaseModel):
    name: str


class Skill(BaseModel):
    name: str


class EmploymentHistoryItem(BaseModel):
    position: str
    employment_type: EmploymentType = EmploymentType.FULL_TIME
    work_mode: WorkMode = WorkMode.ONSITE
    company: CompanyInfo | None = None
    duration: EmploymentDuration
    location: Location | None = None
    key_points: list[KeyPoint] = Field(default_factory=list)
    technologies: list[Technology] = Field(default_factory=list)

    @model_validator(mode="before")
    @classmethod
    def accept_legacy_employment(cls, v: dict):
        if "company" in v and isinstance(v["company"], str):
            v["company"] = {"name": v["company"]}
        if "tech_stack" in v and "technologies" not in v:
            v["technologies"] = v.pop("tech_stack")
        if "start_date" in v or "end_date" in v or "date_format" in v or "duration_months" in v:
            v["duration"] = {
                "date_format": v.pop("date_format", "MM.YYYY"),
                "start": v.pop("start_date", ""),
                "end": v.pop("end_date", ""),
                "duration_months": v.pop("duration_months", 0),
            }
        if "key_points" in v:
            v["key_points"] = [kp if isinstance(kp, dict) else {"text": kp} for kp in v["key_points"]]
        if "technologies" in v:
            v["technologies"] = [t if isinstance(t, dict) else {"name": t} for t in v["technologies"]]
        return v


class Project(BaseModel):
    title: str
    url: str | None = None
    technologies: list[Technology] = Field(default_factory=list)
    key_points: list[KeyPoint] = Field(default_factory=list)

    @model_validator(mode="before")
    @classmethod
    def accept_legacy_project(cls, v: dict):
        if "tech_stack" in v and "technologies" not in v:
            v["technologies"] = v.pop("tech_stack")
        if "technologies" in v:
            v["technologies"] = [t if isinstance(t, dict) else {"name": t} for t in v["technologies"]]
        if "key_points" in v:
            v["key_points"] = [kp if isinstance(kp, dict) else {"text": kp} for kp in v["key_points"]]
        return v


class InstitutionInfo(BaseModel):
    name: str


class Coursework(BaseModel):
    text: str


class EducationExtra(BaseModel):
    text: str


class EducationItem(BaseModel):
    qualification: str | None = None
    field: str
    institution: InstitutionInfo
    location: Location | None = None
    start: str | None = None
    end: str | None = None
    status: EducationStatus
    coursework: list[Coursework] = Field(default_factory=list)
    extras: list[EducationExtra] = Field(default_factory=list)

    @model_validator(mode="before")
    @classmethod
    def accept_legacy_education(cls, v: dict):
        if "institution" in v and isinstance(v["institution"], str):
            v["institution"] = {"name": v["institution"]}
        if "start_date" in v and "start" not in v:
            v["start"] = v.pop("start_date")
        if "end_date" in v and "end" not in v:
            v["end"] = v.pop("end_date")
        if "coursework" in v:
            v["coursework"] = [c if isinstance(c, dict) else {"text": c} for c in v["coursework"]]
        if "extras" in v:
            v["extras"] = [e if isinstance(e, dict) else {"text": e} for e in v["extras"]]
        return v


class Course(BaseModel):
    name: str
    organization: str
    year: int | None = None
    course_url: str | None = None
    certificate_url: str | None = None


class Certification(BaseModel):
    name: str
    issue_org: str | None = None
    issue_year: int | None = None
    certificate_link: str | None = None


class Language(BaseModel):
    name: str


class LanguageProficiency(BaseModel):
    language: Language
    self_assessed: str
    cefr: str

    @model_validator(mode="before")
    @classmethod
    def accept_legacy_language(cls, v: dict):
        if isinstance(v, dict) and isinstance(v.get("language"), str):
            v["language"] = {"name": v["language"]}
        return v


class Award(BaseModel):
    name: str
    award_type: AwardType
    organization: str
    year: int | None = None
    position: str | None = None
    description: str | None = None
    url: str | None = None


class ScientificContribution(BaseModel):
    title: str
    publication_type: PublicationType
    year: int | None = None
    venue: str | None = None
    doi: str | None = None
    url: str | None = None
    description: str | None = None


class Preferences(BaseModel):
    role: str
    employment_types: list[EmploymentType] = Field(default_factory=list)
    work_modes: list[WorkMode] = Field(default_factory=list)
    salary: str | None = None


class ProfessionalProfile(BaseModel):
    summary: str | None = None
    preferences: Preferences | None = None


class Resume(BaseModel):
    uid: str | None = None
    personal_info: PersonalInfo
    professional_profile: ProfessionalProfile | None = None
    skills: list[Skill] = Field(default_factory=list)
    employment_history: list[EmploymentHistoryItem] = Field(default_factory=list)
    projects: list[Project] = Field(default_factory=list)
    education: list[EducationItem] = Field(default_factory=list)
    courses: list[Course] = Field(default_factory=list)
    certifications: list[Certification] = Field(default_factory=list)
    language_proficiency: list[LanguageProficiency] = Field(default_factory=list)
    awards: list[Award] = Field(default_factory=list)
    scientific_contributions: list[ScientificContribution] = Field(default_factory=list)

    @model_validator(mode="before")
    @classmethod
    def accept_legacy_profile(cls, v: dict):
        if "professional_profile" not in v and ("summary" in v or "preferences" in v):
            v["professional_profile"] = {
                "summary": v.pop("summary", None),
                "preferences": v.pop("preferences", None),
            }
        if "skills" in v:
            v["skills"] = [s if isinstance(s, dict) else {"name": s} for s in v["skills"]]
        return v

    def years_of_experience(self) -> float:
        total_months = sum((e.duration.duration_months for e in self.employment_history), 0)
        return round(total_months / 12, 1)

    def has_skill(self, skill: str) -> bool:
        return any(skill.lower() == s.name.lower() for s in self.skills)

    def get_technologies(self) -> set[str]:
        techs: set[str] = set()
        for emp in self.employment_history:
            techs.update(t.name for t in emp.technologies)
        for proj in self.projects:
            techs.update(t.name for t in proj.technologies)
        return techs
