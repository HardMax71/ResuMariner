import logging

from django.conf import settings
from neomodel import adb
from pydantic_neomodel_dict import AsyncConverter

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


class GraphDBService:
    _configured: bool = False
    _converter: AsyncConverter | None = None
    _instance: "GraphDBService | None" = None

    def __init__(self, converter: AsyncConverter) -> None:
        self.converter = converter

    @classmethod
    async def configure(cls) -> None:
        if cls._configured:
            return

        host = settings.NEO4J_URI.replace("bolt://", "")
        connection_url = f"bolt://{settings.NEO4J_USERNAME}:{settings.NEO4J_PASSWORD}@{host}"

        await adb.set_connection(url=connection_url)
        await adb.install_all_labels()

        converter = AsyncConverter()

        model_pairs = [
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

        for pydantic_model, ogm_model in model_pairs:
            converter.register_models(pydantic_model, ogm_model)  # type: ignore[arg-type]

        cls._converter = converter
        cls._configured = True
        logger.info("GraphDBService configured with Neo4j at %s", settings.NEO4J_URI)

    @classmethod
    async def get_instance(cls) -> "GraphDBService":
        if not cls._configured or cls._converter is None:
            await cls.configure()

        assert cls._converter is not None
        if cls._instance is None:
            cls._instance = cls(cls._converter)

        return cls._instance

    async def upsert_resume(self, resume: Resume) -> bool:
        try:
            email = None
            if resume.personal_info and resume.personal_info.contact:
                email = resume.personal_info.contact.email

            if email:
                query = """
                MATCH (r:ResumeNode)-[:HAS_PERSONAL_INFO]->(:PersonalInfoNode)-[:HAS_CONTACT]->(c:ContactNode {email: $email})
                RETURN r.uid as uid
                LIMIT 1
                """
                results, _ = await adb.cypher_query(query, {"email": email})

                if results:
                    existing_uid = results[0][0]
                    existing_node = await ResumeNode.nodes.get_or_none(uid=existing_uid)
                    if existing_node:
                        logger.info("Found existing resume for email %s, updating", email)
                        await self.delete_resume_cascade(existing_node)
                        resume = resume.model_copy(update={"uid": existing_uid})

            resume_node = await self.converter.to_ogm(resume)
            if resume_node is None:
                logger.error("Error creating resume node for %s", resume.uid)
                return False

            logger.info("Successfully stored resume %s in Neo4j", resume_node.uid)
            return True

        except Exception as e:
            logger.error("Failed to upsert resume %s: %s", resume.uid, e)
            return False

    async def get_resume(self, resume_id: str) -> Resume | None:
        resume_node = await ResumeNode.nodes.get_or_none(uid=resume_id)
        if not resume_node:
            return None
        return await self.converter.to_pydantic(resume_node)  # type: ignore[return-value]

    async def get_resumes(self, resume_ids: list[str]) -> dict[str, Resume]:
        if not resume_ids:
            return {}

        resume_nodes = [node async for node in ResumeNode.nodes.filter(uid__in=resume_ids)]

        result: dict[str, Resume] = {}
        for node in resume_nodes:
            resume = await self.converter.to_pydantic(node)
            if resume is not None and isinstance(resume, Resume) and resume.uid:
                result[resume.uid] = resume

        return result

    async def delete_resume(self, resume_id: str) -> bool:
        resume_node = await ResumeNode.nodes.get_or_none(uid=resume_id)
        if not resume_node:
            logger.debug("Resume not found for deletion")
            return False

        await self.delete_resume_cascade(resume_node)
        logger.info("Deleted resume: %s", resume_node.uid)
        return True

    async def delete_resume_cascade(self, resume_node: ResumeNode) -> None:
        query = """
        MATCH (resume:ResumeNode {uid: $uid})

        OPTIONAL MATCH (resume)-[:HAS_PERSONAL_INFO]->(pi:PersonalInfoNode)
        OPTIONAL MATCH (pi)-[:HAS_CONTACT]->(c:ContactNode)
        OPTIONAL MATCH (c)-[:HAS_LINKS]->(cl:ContactLinksNode)
        OPTIONAL MATCH (pi)-[:HAS_DEMOGRAPHICS]->(d:DemographicsNode)
        OPTIONAL MATCH (d)-[:HAS_LOCATION]->(dl:LocationNode)
        OPTIONAL MATCH (d)-[:HAS_WORK_AUTHORIZATION]->(wa:WorkAuthorizationNode)

        OPTIONAL MATCH (resume)-[:HAS_PROFESSIONAL_PROFILE]->(pp:ProfessionalProfileNode)
        OPTIONAL MATCH (pp)-[:HAS_PREFERENCES]->(pref:PreferencesNode)

        OPTIONAL MATCH (resume)-[:HAS_EMPLOYMENT_HISTORY]->(eh:EmploymentHistoryItemNode)
        OPTIONAL MATCH (eh)-[:HAS_DURATION]->(dur:EmploymentDurationNode)
        OPTIONAL MATCH (eh)-[:LOCATED_AT]->(eloc:LocationNode)
        OPTIONAL MATCH (eh)-[:HAS_KEY_POINT]->(kp:KeyPointInfoNode)

        OPTIONAL MATCH (resume)-[:HAS_PROJECT]->(proj:ProjectNode)
        OPTIONAL MATCH (proj)-[:HAS_KEY_POINT]->(pkp:KeyPointInfoNode)

        OPTIONAL MATCH (resume)-[:HAS_EDUCATION]->(edu:EducationItemNode)
        OPTIONAL MATCH (edu)-[:INCLUDES_COURSEWORK]->(cw:CourseworkNode)
        OPTIONAL MATCH (edu)-[:HAS_EXTRA]->(ex:EducationExtraNode)
        OPTIONAL MATCH (edu)-[:LOCATED_AT]->(eduloc:LocationNode)

        OPTIONAL MATCH (resume)-[:HAS_COURSE]->(course:CourseNode)
        OPTIONAL MATCH (resume)-[:HAS_CERTIFICATION]->(cert:CertificationNode)
        OPTIONAL MATCH (resume)-[:HAS_AWARD]->(award:AwardNode)
        OPTIONAL MATCH (resume)-[:HAS_SCIENTIFIC_CONTRIBUTION]->(sc:ScientificContributionNode)

        OPTIONAL MATCH (resume)-[:HAS_LANGUAGE_PROFICIENCY]->(lp:LanguageProficiencyNode)

        DETACH DELETE lp, sc, award, cert, course
        DETACH DELETE ex, cw, eduloc, edu
        DETACH DELETE pkp, proj
        DETACH DELETE kp, eloc, dur, eh
        DETACH DELETE pref, pp
        DETACH DELETE wa, dl, d, cl, c, pi
        DETACH DELETE resume
        """
        await adb.cypher_query(query, {"uid": resume_node.uid})
