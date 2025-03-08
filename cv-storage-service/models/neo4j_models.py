from datetime import datetime
from enum import Enum

from neomodel import (
    StringProperty, IntegerProperty, DateTimeProperty, BooleanProperty,
    JSONProperty, RelationshipTo, RelationshipFrom, StructuredNode, StructuredRel, ZeroOrOne, ZeroOrMore, One
)


# Enum classes for model constraints
class WorkMode(str, Enum):  # Changed to str, Enum for compatibility
    ONSITE = "onsite"
    HYBRID = "hybrid"
    REMOTE = "remote"


class EmploymentType(str, Enum):  # Changed to str, Enum for compatibility
    FULL_TIME = "full-time"
    PART_TIME = "part-time"
    CONTRACT = "contract"


class EducationStatus(str, Enum):  # Changed to str, Enum for compatibility
    COMPLETED = "completed"
    ONGOING = "ongoing"
    INCOMPLETE = "incomplete"


class AwardType(str, Enum):  # Changed to str, Enum for compatibility
    HACKATHON = "hackathon"
    COMPETITION = "competition"
    RECOGNITION = "recognition"
    SCHOLARSHIP = "scholarship"
    OTHER = "other"


class PublicationType(str, Enum):  # Changed to str, Enum for compatibility
    JOURNAL_ARTICLE = "journal_article"
    CONFERENCE_PAPER = "conference_paper"
    PATENT = "patent"
    THESIS = "thesis"
    TECHNICAL_REPORT = "technical_report"
    OTHER = "other"


# Define choices for properties as dictionaries (required by neomodel)
WORK_MODE_CHOICES = {
    WorkMode.ONSITE.value: WorkMode.ONSITE.value,
    WorkMode.HYBRID.value: WorkMode.HYBRID.value,
    WorkMode.REMOTE.value: WorkMode.REMOTE.value
}

EMPLOYMENT_TYPE_CHOICES = {
    EmploymentType.FULL_TIME.value: EmploymentType.FULL_TIME.value,
    EmploymentType.PART_TIME.value: EmploymentType.PART_TIME.value,
    EmploymentType.CONTRACT.value: EmploymentType.CONTRACT.value
}

EDUCATION_STATUS_CHOICES = {
    EducationStatus.COMPLETED.value: EducationStatus.COMPLETED.value,
    EducationStatus.ONGOING.value: EducationStatus.ONGOING.value,
    EducationStatus.INCOMPLETE.value: EducationStatus.INCOMPLETE.value
}

AWARD_TYPE_CHOICES = {
    AwardType.HACKATHON.value: AwardType.HACKATHON.value,
    AwardType.COMPETITION.value: AwardType.COMPETITION.value,
    AwardType.RECOGNITION.value: AwardType.RECOGNITION.value,
    AwardType.SCHOLARSHIP.value: AwardType.SCHOLARSHIP.value,
    AwardType.OTHER.value: AwardType.OTHER.value
}

PUBLICATION_TYPE_CHOICES = {
    PublicationType.JOURNAL_ARTICLE.value: PublicationType.JOURNAL_ARTICLE.value,
    PublicationType.CONFERENCE_PAPER.value: PublicationType.CONFERENCE_PAPER.value,
    PublicationType.PATENT.value: PublicationType.PATENT.value,
    PublicationType.THESIS.value: PublicationType.THESIS.value,
    PublicationType.TECHNICAL_REPORT.value: PublicationType.TECHNICAL_REPORT.value,
    PublicationType.OTHER.value: PublicationType.OTHER.value
}


# Relationship models
class BaseRelationship(StructuredRel):
    """Base relationship with common properties"""
    created_at = DateTimeProperty(default=datetime.now)


class HasSkillRel(BaseRelationship):
    """Relationship for a person's skill"""
    pass


class HasCourseRel(BaseRelationship):
    """Relationship for courses"""
    level = StringProperty()
    start_date = DateTimeProperty()
    end_date = DateTimeProperty()


class SpeaksLanguageRel(BaseRelationship):
    """Relationship for language proficiency"""
    self_assessed = StringProperty(required=True)
    cefr = StringProperty(required=True)


class HasExperienceRel(BaseRelationship):
    """Relationship for employment history"""
    pass


class CompletedProjectRel(BaseRelationship):
    """Relationship for projects"""
    pass


class EducatedAtRel(BaseRelationship):
    """Relationship for education"""
    pass


class HasCertificationRel(BaseRelationship):
    """Relationship for certifications"""
    pass


class ReceivedAwardRel(BaseRelationship):
    """Relationship for awards"""
    pass


class AuthoredRel(BaseRelationship):
    """Relationship for scientific contributions"""
    pass


# Node models
class Person(StructuredNode):
    """
    Person node representing an individual with a CV

    This is the central node that connects to all other nodes in the graph.
    """
    # Basic information
    email = StringProperty(unique_index=True, required=True)
    name = StringProperty(index=True, required=True)
    phone = StringProperty(index=True)

    # Location information
    city = StringProperty(index=True)
    state = StringProperty()
    country = StringProperty(index=True)

    # Professional links
    github_url = StringProperty()
    linkedin_url = StringProperty()
    telegram_url = StringProperty()
    other_links = JSONProperty()  # Store other links as JSON

    # Work authorization
    citizenship = StringProperty()
    work_permit = BooleanProperty()
    visa_sponsorship_required = BooleanProperty()

    # Relationships - CV data
    cv = RelationshipTo('CV', 'HAS_CV', cardinality=ZeroOrMore)
    skills = RelationshipTo('Skill', 'HAS_SKILL', model=HasSkillRel)
    experiences = RelationshipTo('Experience', 'HAD_EXPERIENCE', model=HasExperienceRel)
    projects = RelationshipTo('Project', 'COMPLETED_PROJECT', model=CompletedProjectRel)
    education = RelationshipTo('Education', 'EDUCATED_AT', model=EducatedAtRel)
    languages = RelationshipTo('Language', 'SPEAKS', model=SpeaksLanguageRel)
    certifications = RelationshipTo('Certification', 'HAS_CERTIFICATION', model=HasCertificationRel)
    awards = RelationshipTo('Award', 'RECEIVED_AWARD', model=ReceivedAwardRel)
    scientific_contributions = RelationshipTo('ScientificContribution', 'AUTHORED', model=AuthoredRel)

    @classmethod
    def get_or_create(cls, email, **properties):
        """Get existing person or create a new one if not found"""
        try:
            # First try to find by email
            person = cls.nodes.get(email=email)

            # Update properties if provided
            if properties:
                for key, value in properties.items():
                    setattr(person, key, value)
                person.save()

            return person, False
        except cls.DoesNotExist:
            # Create new person if not found
            person = cls(email=email, **properties)
            person.save()
            return person, True


class CV(StructuredNode):
    """
    CV node representing a person's curriculum vitae

    This node contains overall CV information and connects to a person.
    """
    # Use a UUID as string for the ID, but avoid using 'id' which conflicts with neomodel
    cv_id = StringProperty(unique_index=True, required=True)
    created_at = DateTimeProperty(default=datetime.now)
    updated_at = DateTimeProperty(default=datetime.now)
    summary = StringProperty()
    desired_role = StringProperty(index=True)
    salary_expectation = StringProperty()
    resume_lang = StringProperty(default="en")  # ISO 639-1 language code

    # Relationships
    person = RelationshipFrom('Person', 'HAS_CV', cardinality=One)

    def before_save(self):
        """Update the 'updated_at' timestamp before saving the node"""
        self.updated_at = datetime.now()


class Skill(StructuredNode):
    """
    Skill node representing a single skill or competency
    """
    name = StringProperty(unique_index=True, required=True)

    # Relationships
    persons = RelationshipFrom('Person', 'HAS_SKILL', model=HasSkillRel)


class Technology(StructuredNode):
    """
    Technology node representing a specific technology or tool
    """
    name = StringProperty(unique_index=True, required=True)

    # Relationships
    experiences = RelationshipFrom('Experience', 'USES_TECHNOLOGY')
    projects = RelationshipFrom('Project', 'USES_TECHNOLOGY')


class Company(StructuredNode):
    """
    Company node representing an organization where a person has worked
    """
    name = StringProperty(unique_index=True, required=True)

    # Relationships
    experiences = RelationshipFrom('Experience', 'AT_COMPANY')


class Experience(StructuredNode):
    """
    Experience node representing a job or work experience
    """
    position = StringProperty(required=True, index=True)
    start_date = StringProperty()
    end_date = StringProperty()
    duration_months = IntegerProperty(default=0)
    employment_type = StringProperty(choices=EMPLOYMENT_TYPE_CHOICES, index=True)
    work_mode = StringProperty(choices=WORK_MODE_CHOICES, index=True)

    # Location details
    city = StringProperty()
    state = StringProperty()
    country = StringProperty()

    # Relationships
    person = RelationshipFrom('Person', 'HAD_EXPERIENCE', cardinality=One)
    company = RelationshipTo('Company', 'AT_COMPANY', cardinality=One)
    key_points = RelationshipTo('KeyPoint', 'HAS_KEY_POINT')
    technologies = RelationshipTo('Technology', 'USES_TECHNOLOGY')


class Project(StructuredNode):
    """
    Project node representing a project completed by a person
    """
    title = StringProperty(required=True, index=True)
    url = StringProperty()

    # Relationships
    person = RelationshipFrom('Person', 'COMPLETED_PROJECT', cardinality=One)
    key_points = RelationshipTo('KeyPoint', 'HAS_KEY_POINT')
    technologies = RelationshipTo('Technology', 'USES_TECHNOLOGY')


class KeyPoint(StructuredNode):
    """
    KeyPoint node representing a bullet point or achievement
    """
    text = StringProperty(required=True)
    index = IntegerProperty(default=0)  # For ordering
    source = StringProperty()  # e.g., 'experience' or 'project'

    # Relationships
    experience = RelationshipFrom('Experience', 'HAS_KEY_POINT', cardinality=ZeroOrOne)
    project = RelationshipFrom('Project', 'HAS_KEY_POINT', cardinality=ZeroOrOne)


class Institution(StructuredNode):
    """
    Institution node representing an educational institution
    """
    name = StringProperty(unique_index=True, required=True)

    # Relationships
    educations = RelationshipFrom('Education', 'AT_INSTITUTION')


class Education(StructuredNode):
    """
    Education node representing educational background
    """
    qualification = StringProperty(required=True, index=True)
    field = StringProperty(required=True, index=True)
    start = StringProperty()
    end = StringProperty()
    status = StringProperty(choices=EDUCATION_STATUS_CHOICES)  # Using the dict instead of the Enum

    # Location details
    city = StringProperty()
    state = StringProperty()
    country = StringProperty()

    # Relationships
    person = RelationshipFrom('Person', 'EDUCATED_AT', cardinality=One)
    institution = RelationshipTo('Institution', 'AT_INSTITUTION', cardinality=One)
    coursework = RelationshipTo('Coursework', 'INCLUDES_COURSEWORK')
    extras = RelationshipTo('EducationExtra', 'HAS_EXTRA')


class Coursework(StructuredNode):
    """
    Coursework node representing coursework within an education
    """
    text = StringProperty(required=True)
    index = IntegerProperty(default=0)  # For ordering

    # Relationships
    education = RelationshipFrom('Education', 'INCLUDES_COURSEWORK', cardinality=One)


class EducationExtra(StructuredNode):
    """
    EducationExtra node representing additional educational achievements
    """
    text = StringProperty(required=True)
    index = IntegerProperty(default=0)  # For ordering

    # Relationships
    education = RelationshipFrom('Education', 'HAS_EXTRA', cardinality=One)


class Language(StructuredNode):
    """
    Language node representing a spoken language
    """
    name = StringProperty(unique_index=True, required=True)

    # Relationships
    persons = RelationshipFrom('Person', 'SPEAKS', model=SpeaksLanguageRel)


class Certification(StructuredNode):
    """
    Certification node representing a professional certification
    """
    name = StringProperty(required=True, index=True)
    issue_org = StringProperty()
    issue_year = IntegerProperty()
    certificate_link = StringProperty()

    # Relationships
    person = RelationshipFrom('Person', 'HAS_CERTIFICATION', cardinality=One)


class Award(StructuredNode):
    """
    Award node representing an award or achievement
    """
    name = StringProperty(required=True, index=True)
    award_type = StringProperty(choices=AWARD_TYPE_CHOICES)  # Using the dict instead of the Enum
    organization = StringProperty()
    year = IntegerProperty()
    position = StringProperty()
    description = StringProperty()
    url = StringProperty()

    # Relationships
    person = RelationshipFrom('Person', 'RECEIVED_AWARD', cardinality=One)


class ScientificContribution(StructuredNode):
    """
    ScientificContribution node representing a scientific publication or contribution
    """
    title = StringProperty(required=True, index=True)
    publication_type = StringProperty(choices=PUBLICATION_TYPE_CHOICES)  # Using the dict instead of the Enum
    year = IntegerProperty()
    venue = StringProperty()
    doi = StringProperty()
    url = StringProperty()
    description = StringProperty()

    # Relationships
    person = RelationshipFrom('Person', 'AUTHORED', cardinality=One)


class Course(StructuredNode):
    """
    Course node representing an individual course taken
    """
    name = StringProperty(required=True, index=True)
    organization = StringProperty(required=True)
    year = IntegerProperty()
    course_url = StringProperty()
    certificate_url = StringProperty()

    # Relationships
    person = RelationshipFrom('Person', 'COMPLETED_COURSE', cardinality=One)
