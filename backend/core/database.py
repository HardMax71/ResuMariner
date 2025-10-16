import logging

from django.conf import settings
from pydantic_neomodel_dict import AsyncConverter
from qdrant_client import AsyncQdrantClient

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
from core.models.neo4j_models import (
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
from core.services.graph_db_service import GraphDBService
from core.services.vector_db_service import VectorDBService

logger = logging.getLogger(__name__)

CONVERTER = AsyncConverter()
MODEL_PAIRS = [
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

for pydantic_model, neo_model in MODEL_PAIRS:
    CONVERTER.register_models(pydantic_model, neo_model)  # type: ignore[arg-type]

logger.info("Registered %d Pydantic-Neomodel model pairs at module load", len(MODEL_PAIRS))

QDRANT_CLIENT = AsyncQdrantClient(
    host=settings.QDRANT_HOST,
    port=settings.QDRANT_PORT,
    timeout=settings.QDRANT_TIMEOUT,
    prefer_grpc=settings.QDRANT_PREFER_GRPC,
)


def create_graph_service() -> "GraphDBService":
    return GraphDBService(CONVERTER)


def create_vector_service() -> "VectorDBService":
    return VectorDBService(QDRANT_CLIENT)
