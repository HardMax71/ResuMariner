import logging

from neomodel import adb
from pydantic_neomodel_dict import AsyncConverter

from core.domain import Resume
from core.models.neo4j_models import ResumeNode

logger = logging.getLogger(__name__)


class GraphDBService:
    """Neo4j graph database operations for resume storage and retrieval."""

    def __init__(self, converter: AsyncConverter) -> None:
        self.converter = converter

    async def upsert_resume(self, resume: Resume) -> bool:
        """Create or update resume in Neo4j graph."""
        try:
            # Check if resume exists
            existing_node = await ResumeNode.nodes.get_or_none(uid=resume.uid)
            if existing_node:
                logger.debug("Updating existing resume %s", resume.uid)
                # Delete in its own transaction
                async with adb.write_transaction:
                    await self.delete_resume_cascade(existing_node)

            # Create new resume - converter handles its own transaction
            resume_node = await self.converter.to_ogm(resume)
            if resume_node is None:
                raise RuntimeError(f"Failed to create resume node for {resume.uid}")

            logger.info("Stored resume in Neo4j: %s", resume.uid)
            return True

        except Exception as e:
            logger.error("Failed to upsert resume %s: %s", resume.uid, e)
            return False

    async def get_resume(self, uid: str) -> Resume | None:
        """Get resume by uid from Neo4j."""
        async with adb.read_transaction:
            resume_node = await ResumeNode.nodes.get_or_none(uid=uid)
            if not resume_node:
                return None
            return await self.converter.to_pydantic(resume_node)  # type: ignore[return-value]

    async def get_resumes(self, uids: list[str]) -> dict[str, Resume]:
        """Batch fetch resumes by uids from Neo4j."""
        if not uids:
            return {}

        async with adb.read_transaction:
            resume_nodes = [node async for node in ResumeNode.nodes.filter(uid__in=uids)]

            result: dict[str, Resume] = {}
            for node in resume_nodes:
                resume = await self.converter.to_pydantic(node)
                if resume is not None and resume.uid:  # type: ignore[attr-defined]
                    result[resume.uid] = resume  # type: ignore[attr-defined,assignment]

            return result

    async def delete_resume(self, uid: str) -> bool:
        """Delete resume and all related nodes from Neo4j."""
        try:
            async with adb.write_transaction:
                resume_node = await ResumeNode.nodes.get_or_none(uid=uid)
                if not resume_node:
                    logger.debug("Resume not found for deletion: %s", uid)
                    return False

                await self.delete_resume_cascade(resume_node)
                logger.info("Deleted resume from Neo4j: %s", resume_node.uid)
            return True

        except Exception as e:
            logger.error("Failed to delete resume %s: %s", uid, e)
            return False

    async def get_resume_by_email(self, email: str) -> Resume | None:
        """Find resume by email address."""
        async with adb.read_transaction:
            query = """
            MATCH (r:ResumeNode)-[:HAS_PERSONAL_INFO]->(pi:PersonalInfoNode)-[:HAS_CONTACT]->(c:ContactNode)
            WHERE c.email = $email
            RETURN r
            LIMIT 1
            """
            results, _ = await adb.cypher_query(query, {"email": email.lower()})

            if not results:
                return None

            resume_node = results[0][0]
            return await self.converter.to_pydantic(resume_node)  # type: ignore[return-value]

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
