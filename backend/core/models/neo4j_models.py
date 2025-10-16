from datetime import datetime
from enum import Enum

from neomodel import (
    ArrayProperty,
    BooleanProperty,
    DateTimeProperty,
    IntegerProperty,
    JSONProperty,
    StringProperty,
)
from neomodel.async_.core import AsyncStructuredNode
from neomodel.async_.relationship_manager import AsyncRelationshipTo


class WorkMode(Enum):
    ONSITE = "onsite"
    HYBRID = "hybrid"
    REMOTE = "remote"


class EmploymentType(Enum):
    FULL_TIME = "full-time"
    PART_TIME = "part-time"
    CONTRACT = "contract"


class EducationStatus(Enum):
    COMPLETED = "completed"
    ONGOING = "ongoing"
    INCOMPLETE = "incomplete"


class AwardType(Enum):
    HACKATHON = "hackathon"
    COMPETITION = "competition"
    RECOGNITION = "recognition"
    SCHOLARSHIP = "scholarship"
    OTHER = "other"


class PublicationType(Enum):
    JOURNAL_ARTICLE = "journal_article"
    CONFERENCE_PAPER = "conference_paper"
    PATENT = "patent"
    THESIS = "thesis"
    TECHNICAL_REPORT = "technical_report"
    OTHER = "other"


WORK_MODE_CHOICES = {e.value: e.value for e in WorkMode}
EMPLOYMENT_TYPE_CHOICES = {e.value: e.value for e in EmploymentType}
EDUCATION_STATUS_CHOICES = {e.value: e.value for e in EducationStatus}
AWARD_TYPE_CHOICES = {e.value: e.value for e in AwardType}
PUBLICATION_TYPE_CHOICES = {e.value: e.value for e in PublicationType}


class LanguageNode(AsyncStructuredNode):
    name = StringProperty(required=True, unique_index=True)


class LanguageProficiencyNode(AsyncStructuredNode):
    self_assessed = StringProperty(required=True)
    cefr = StringProperty(required=True)
    language = AsyncRelationshipTo("LanguageNode", "OF_LANGUAGE")


class LocationNode(AsyncStructuredNode):
    city = StringProperty()
    state = StringProperty()
    country = StringProperty()


class ContactLinksNode(AsyncStructuredNode):
    telegram = StringProperty()
    linkedin = StringProperty()
    github = StringProperty()
    other_links = JSONProperty()


class ContactNode(AsyncStructuredNode):
    email = StringProperty(required=True, unique_index=True)
    phone = StringProperty()
    links = AsyncRelationshipTo("ContactLinksNode", "HAS_LINKS")


class WorkAuthorizationNode(AsyncStructuredNode):
    citizenship = StringProperty()
    work_permit = BooleanProperty()
    visa_sponsorship_required = BooleanProperty()


class DemographicsNode(AsyncStructuredNode):
    current_location = AsyncRelationshipTo("LocationNode", "HAS_LOCATION")
    work_authorization = AsyncRelationshipTo("WorkAuthorizationNode", "HAS_WORK_AUTHORIZATION")


class PersonalInfoNode(AsyncStructuredNode):
    name = StringProperty(required=True)
    resume_lang = StringProperty(required=True)
    contact = AsyncRelationshipTo("ContactNode", "HAS_CONTACT")
    demographics = AsyncRelationshipTo("DemographicsNode", "HAS_DEMOGRAPHICS")


class PreferencesNode(AsyncStructuredNode):
    role = StringProperty(required=True)
    employment_types = ArrayProperty(base_property=StringProperty(choices=EMPLOYMENT_TYPE_CHOICES))
    work_modes = ArrayProperty(base_property=StringProperty(choices=WORK_MODE_CHOICES))
    salary = StringProperty()


class ProfessionalProfileNode(AsyncStructuredNode):
    summary = StringProperty()
    preferences = AsyncRelationshipTo("PreferencesNode", "HAS_PREFERENCES")


class EmploymentDurationNode(AsyncStructuredNode):
    start = StringProperty(required=True)  # Format: YYYY.MM
    end = StringProperty()  # Format: YYYY.MM or None for ongoing
    duration_months = IntegerProperty(required=True)


class CompanyInfoNode(AsyncStructuredNode):
    name = StringProperty(required=True, unique_index=True)
    url = StringProperty()


class KeyPointInfoNode(AsyncStructuredNode):
    text = StringProperty(required=True)


class EmploymentHistoryItemNode(AsyncStructuredNode):
    position = StringProperty(required=True)
    employment_type = StringProperty(required=True, choices=EMPLOYMENT_TYPE_CHOICES)
    work_mode = StringProperty(required=True, choices=WORK_MODE_CHOICES)
    skills = AsyncRelationshipTo("SkillNode", "HAS_SKILL")

    company = AsyncRelationshipTo("CompanyInfoNode", "WORKED_AT")
    duration = AsyncRelationshipTo("EmploymentDurationNode", "HAS_DURATION")
    location = AsyncRelationshipTo("LocationNode", "LOCATED_AT")
    key_points = AsyncRelationshipTo("KeyPointInfoNode", "HAS_KEY_POINT")


class ProjectNode(AsyncStructuredNode):
    title = StringProperty(required=True)
    url = StringProperty()
    skills = AsyncRelationshipTo("SkillNode", "HAS_SKILL")
    key_points = AsyncRelationshipTo("KeyPointInfoNode", "HAS_KEY_POINT")


class InstitutionInfoNode(AsyncStructuredNode):
    name = StringProperty(required=True, unique_index=True)


class CourseworkNode(AsyncStructuredNode):
    text = StringProperty(required=True)


class EducationExtraNode(AsyncStructuredNode):
    text = StringProperty(required=True)


class EducationItemNode(AsyncStructuredNode):
    qualification = StringProperty()
    field = StringProperty(required=True)
    start = StringProperty()  # Format: YYYY.MM
    end = StringProperty()  # Format: YYYY.MM or None for in-progress
    status = StringProperty(required=True, choices=EDUCATION_STATUS_CHOICES)
    coursework = AsyncRelationshipTo("CourseworkNode", "INCLUDES_COURSEWORK")
    extras = AsyncRelationshipTo("EducationExtraNode", "HAS_EXTRA")

    institution = AsyncRelationshipTo("InstitutionInfoNode", "ATTENDED")
    location = AsyncRelationshipTo("LocationNode", "LOCATED_AT")


class CourseNode(AsyncStructuredNode):
    name = StringProperty(required=True)
    organization = StringProperty(required=True)
    year = IntegerProperty()
    course_url = StringProperty()
    certificate_url = StringProperty()


class CertificationNode(AsyncStructuredNode):
    name = StringProperty(required=True)
    issue_org = StringProperty()
    issue_year = IntegerProperty()
    certificate_link = StringProperty()


class AwardNode(AsyncStructuredNode):
    name = StringProperty(required=True)
    award_type = StringProperty(required=True, choices=AWARD_TYPE_CHOICES)
    organization = StringProperty(required=True)
    year = IntegerProperty()
    position = StringProperty()
    description = StringProperty()
    url = StringProperty()


class ScientificContributionNode(AsyncStructuredNode):
    title = StringProperty(required=True)
    publication_type = StringProperty(required=True, choices=PUBLICATION_TYPE_CHOICES)
    year = IntegerProperty()
    venue = StringProperty()
    doi = StringProperty()
    url = StringProperty()
    description = StringProperty()


class SkillNode(AsyncStructuredNode):
    name = StringProperty(required=True, unique_index=True)


class ResumeNode(AsyncStructuredNode):
    uid = StringProperty(required=True, unique_index=True)
    created_at = DateTimeProperty(default=datetime.now)
    updated_at = DateTimeProperty(default=datetime.now)

    personal_info = AsyncRelationshipTo("PersonalInfoNode", "HAS_PERSONAL_INFO")
    professional_profile = AsyncRelationshipTo("ProfessionalProfileNode", "HAS_PROFESSIONAL_PROFILE")
    skills = AsyncRelationshipTo("SkillNode", "HAS_SKILL")
    employment_history = AsyncRelationshipTo("EmploymentHistoryItemNode", "HAS_EMPLOYMENT_HISTORY")
    projects = AsyncRelationshipTo("ProjectNode", "HAS_PROJECT")
    education = AsyncRelationshipTo("EducationItemNode", "HAS_EDUCATION")
    courses = AsyncRelationshipTo("CourseNode", "HAS_COURSE")
    certifications = AsyncRelationshipTo("CertificationNode", "HAS_CERTIFICATION")
    awards = AsyncRelationshipTo("AwardNode", "HAS_AWARD")
    scientific_contributions = AsyncRelationshipTo("ScientificContributionNode", "HAS_SCIENTIFIC_CONTRIBUTION")
    language_proficiency = AsyncRelationshipTo("LanguageProficiencyNode", "HAS_LANGUAGE_PROFICIENCY")
