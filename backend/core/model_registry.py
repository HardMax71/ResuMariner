import logging

from pydantic_neomodel_dict import Converter

from core.domain import (
    Award,
    Certification,
    CompanyInfo,
    Contact,
    ContactLinks,
    Course,
    Coursework,
    Demographics,
    EducationExtra,
    EducationItem,
    EmploymentDuration,
    EmploymentHistoryItem,
    InstitutionInfo,
    KeyPoint,
    Language,
    LanguageProficiency,
    Location,
    PersonalInfo,
    Preferences,
    ProfessionalProfile,
    Project,
    Resume,
    ScientificContribution,
    Skill,
    WorkAuthorization,
)
from storage.neo4j_models import (
    AwardNode,
    CertificationNode,
    CompanyInfoNode,
    ContactLinksNode,
    ContactNode,
    CourseNode,
    CourseworkNode,
    DemographicsNode,
    EducationExtraNode,
    EducationItemNode,
    EmploymentDurationNode,
    EmploymentHistoryItemNode,
    InstitutionInfoNode,
    KeyPointInfoNode,
    LanguageNode,
    LanguageProficiencyNode,
    LocationNode,
    PersonalInfoNode,
    PreferencesNode,
    ProfessionalProfileNode,
    ProjectNode,
    ResumeNode,
    ScientificContributionNode,
    SkillNode,
    WorkAuthorizationNode,
)

logger = logging.getLogger(__name__)


class ModelRegistry:
    _initialized: bool = False

    @classmethod
    def initialize(cls) -> None:
        if cls._initialized:
            return

        pairs = [
            (Resume, ResumeNode),
            (PersonalInfo, PersonalInfoNode),
            (Contact, ContactNode),
            (ContactLinks, ContactLinksNode),
            (Demographics, DemographicsNode),
            (WorkAuthorization, WorkAuthorizationNode),
            (Location, LocationNode),
            (ProfessionalProfile, ProfessionalProfileNode),
            (Preferences, PreferencesNode),
            (EmploymentHistoryItem, EmploymentHistoryItemNode),
            (EmploymentDuration, EmploymentDurationNode),
            (CompanyInfo, CompanyInfoNode),
            (KeyPoint, KeyPointInfoNode),
            (Skill, SkillNode),
            (Project, ProjectNode),
            (InstitutionInfo, InstitutionInfoNode),
            (Coursework, CourseworkNode),
            (EducationExtra, EducationExtraNode),
            (EducationItem, EducationItemNode),
            (Course, CourseNode),
            (Certification, CertificationNode),
            (Award, AwardNode),
            (ScientificContribution, ScientificContributionNode),
            (Language, LanguageNode),
            (LanguageProficiency, LanguageProficiencyNode),
        ]
        for p, o in pairs:
            Converter.register_models(p, o)  # type: ignore[arg-type]

        cls._initialized = True
