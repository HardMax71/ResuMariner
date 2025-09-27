from datetime import datetime
from enum import Enum

from neomodel import (
    ArrayProperty,
    BooleanProperty,
    DateTimeProperty,
    IntegerProperty,
    JSONProperty,
    RelationshipTo,
    StringProperty,
    StructuredNode,
)


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


class LanguageNode(StructuredNode):
    name = StringProperty(required=True, unique_index=True)


class LanguageProficiencyNode(StructuredNode):
    self_assessed = StringProperty(required=True)
    cefr = StringProperty(required=True)
    language = RelationshipTo("LanguageNode", "OF_LANGUAGE")


class LocationNode(StructuredNode):
    city = StringProperty()
    state = StringProperty()
    country = StringProperty()


class ContactLinksNode(StructuredNode):
    telegram = StringProperty()
    linkedin = StringProperty()
    github = StringProperty()
    other_links = JSONProperty()


class ContactNode(StructuredNode):
    email = StringProperty(required=True, unique_index=True)
    phone = StringProperty()
    links = RelationshipTo("ContactLinksNode", "HAS_LINKS")


class WorkAuthorizationNode(StructuredNode):
    citizenship = StringProperty()
    work_permit = BooleanProperty()
    visa_sponsorship_required = BooleanProperty()


class DemographicsNode(StructuredNode):
    current_location = RelationshipTo("LocationNode", "HAS_LOCATION")
    work_authorization = RelationshipTo(
        "WorkAuthorizationNode", "HAS_WORK_AUTHORIZATION"
    )


class PersonalInfoNode(StructuredNode):
    name = StringProperty(required=True)
    resume_lang = StringProperty(required=True)
    contact = RelationshipTo("ContactNode", "HAS_CONTACT")
    demographics = RelationshipTo("DemographicsNode", "HAS_DEMOGRAPHICS")


class PreferencesNode(StructuredNode):
    role = StringProperty(required=True)
    employment_types = ArrayProperty(
        base_property=StringProperty(choices=EMPLOYMENT_TYPE_CHOICES)
    )
    work_modes = ArrayProperty(base_property=StringProperty(choices=WORK_MODE_CHOICES))
    salary = StringProperty()


class ProfessionalProfileNode(StructuredNode):
    summary = StringProperty()
    preferences = RelationshipTo("PreferencesNode", "HAS_PREFERENCES")


class EmploymentDurationNode(StructuredNode):
    date_format = StringProperty(required=True)
    start = StringProperty(required=True)
    end = StringProperty(required=True)
    duration_months = IntegerProperty(required=True)


class CompanyInfoNode(StructuredNode):
    name = StringProperty(required=True, unique_index=True)
    url = StringProperty()


class KeyPointInfoNode(StructuredNode):
    text = StringProperty(required=True)


class TechnologyNode(StructuredNode):
    name = StringProperty(required=True, unique_index=True)


class EmploymentHistoryItemNode(StructuredNode):
    position = StringProperty(required=True)
    employment_type = StringProperty(required=True, choices=EMPLOYMENT_TYPE_CHOICES)
    work_mode = StringProperty(required=True, choices=WORK_MODE_CHOICES)
    technologies = RelationshipTo("TechnologyNode", "USES_TECHNOLOGY")

    company = RelationshipTo("CompanyInfoNode", "WORKED_AT")
    duration = RelationshipTo("EmploymentDurationNode", "HAS_DURATION")
    location = RelationshipTo("LocationNode", "LOCATED_AT")
    key_points = RelationshipTo("KeyPointInfoNode", "HAS_KEY_POINT")


class ProjectNode(StructuredNode):
    title = StringProperty(required=True)
    url = StringProperty()
    technologies = RelationshipTo("TechnologyNode", "USES_TECHNOLOGY")
    key_points = RelationshipTo("KeyPointInfoNode", "HAS_KEY_POINT")


class InstitutionInfoNode(StructuredNode):
    name = StringProperty(required=True, unique_index=True)


class CourseworkNode(StructuredNode):
    text = StringProperty(required=True)


class EducationExtraNode(StructuredNode):
    text = StringProperty(required=True)


class EducationItemNode(StructuredNode):
    qualification = StringProperty()
    field = StringProperty(required=True)
    start = StringProperty()
    end = StringProperty()
    status = StringProperty(required=True, choices=EDUCATION_STATUS_CHOICES)
    coursework = RelationshipTo("CourseworkNode", "INCLUDES_COURSEWORK")
    extras = RelationshipTo("EducationExtraNode", "HAS_EXTRA")

    institution = RelationshipTo("InstitutionInfoNode", "ATTENDED")
    location = RelationshipTo("LocationNode", "LOCATED_AT")


class CourseNode(StructuredNode):
    name = StringProperty(required=True)
    organization = StringProperty(required=True)
    year = IntegerProperty()
    course_url = StringProperty()
    certificate_url = StringProperty()


class CertificationNode(StructuredNode):
    name = StringProperty(required=True)
    issue_org = StringProperty()
    issue_year = IntegerProperty()
    certificate_link = StringProperty()


class AwardNode(StructuredNode):
    name = StringProperty(required=True)
    award_type = StringProperty(required=True, choices=AWARD_TYPE_CHOICES)
    organization = StringProperty(required=True)
    year = IntegerProperty()
    position = StringProperty()
    description = StringProperty()
    url = StringProperty()


class ScientificContributionNode(StructuredNode):
    title = StringProperty(required=True)
    publication_type = StringProperty(required=True, choices=PUBLICATION_TYPE_CHOICES)
    year = IntegerProperty()
    venue = StringProperty()
    doi = StringProperty()
    url = StringProperty()
    description = StringProperty()


class SkillNode(StructuredNode):
    name = StringProperty(required=True, unique_index=True)


class ResumeNode(StructuredNode):
    uid = StringProperty(required=True, unique_index=True)
    created_at = DateTimeProperty(default=datetime.now)
    updated_at = DateTimeProperty(default=datetime.now)

    personal_info = RelationshipTo("PersonalInfoNode", "HAS_PERSONAL_INFO")
    professional_profile = RelationshipTo(
        "ProfessionalProfileNode", "HAS_PROFESSIONAL_PROFILE"
    )
    skills = RelationshipTo("SkillNode", "HAS_SKILL")
    employment_history = RelationshipTo(
        "EmploymentHistoryItemNode", "HAS_EMPLOYMENT_HISTORY"
    )
    projects = RelationshipTo("ProjectNode", "HAS_PROJECT")
    education = RelationshipTo("EducationItemNode", "HAS_EDUCATION")
    courses = RelationshipTo("CourseNode", "HAS_COURSE")
    certifications = RelationshipTo("CertificationNode", "HAS_CERTIFICATION")
    awards = RelationshipTo("AwardNode", "HAS_AWARD")
    scientific_contributions = RelationshipTo(
        "ScientificContributionNode", "HAS_SCIENTIFIC_CONTRIBUTION"
    )
    language_proficiency = RelationshipTo(
        "LanguageProficiencyNode", "HAS_LANGUAGE_PROFICIENCY"
    )
