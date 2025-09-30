import logging

from django.conf import settings
from neomodel import config, db, install_all_labels
from pydantic_neomodel_dict import Converter

from core.domain import Resume
from core.model_registry import ModelRegistry
from storage.neo4j_models import ResumeNode

logger = logging.getLogger(__name__)


class GraphDBService:
    """
    Service for interacting with Neo4j using Pydantic models.
    Uses pydantic-neomodel-dict for automatic conversion.
    """

    def __init__(self) -> None:
        self._configure_neo4j()
        ModelRegistry.initialize()
        logger.info("GraphDBService initialized with model registry")

    def _configure_neo4j(self) -> None:
        host = settings.NEO4J_URI.replace("bolt://", "")
        connection_url = f"bolt://{settings.NEO4J_USERNAME}:{settings.NEO4J_PASSWORD}@{host}"
        config.DATABASE_URL = connection_url
        config.DRIVER_CONFIG = {
            "max_connection_lifetime": settings.NEO4J_MAX_CONNECTION_LIFETIME,
            "max_connection_pool_size": settings.NEO4J_MAX_CONNECTION_POOL_SIZE,
            "connection_timeout": settings.NEO4J_CONNECTION_TIMEOUT,
            "encrypted": False,
            "trust": "TRUST_ALL_CERTIFICATES",
        }
        install_all_labels()
        logger.info("Connected to Neo4j at %s", settings.NEO4J_URI)

    def upsert_resume(self, resume: Resume) -> bool:
        try:
            # Get email if available
            email = None
            if resume.personal_info and resume.personal_info.contact:
                email = resume.personal_info.contact.email

            # If we have an email, check for existing resume by email
            if email:
                query = """
                MATCH (r:ResumeNode)-[:HAS_PERSONAL_INFO]->(:PersonalInfoNode)-[:HAS_CONTACT]->(c:ContactNode {email: $email})
                RETURN r.uid as uid
                LIMIT 1
                """
                results, _ = db.cypher_query(query, {"email": email})

                if results:
                    existing_uid = results[0][0]
                    existing_node = ResumeNode.nodes.get_or_none(uid=existing_uid)
                    if existing_node:
                        logger.info("Found existing resume for email %s, updating", email)
                        self.delete_resume_cascade(existing_node)
                        # Use the same uid for consistency
                        resume = resume.model_copy(update={"uid": existing_uid})

            # Convert and save the resume
            resume_node: ResumeNode | None = Converter.to_ogm(resume)
            if resume_node is None:
                logger.error("Error with creating resume node for %s", resume.uid)
                return False

            logger.info("Successfully stored resume %s in Neo4j", resume_node.uid)
            return True

        except Exception as e:
            logger.error("Failed to upsert resume %s: %s", resume.uid, e)
            return False

    def get_resume(self, resume_id: str) -> Resume | None:
        resume_node = ResumeNode.nodes.get_or_none(uid=resume_id)
        if not resume_node:
            return None
        return Converter.to_pydantic(resume_node)  # type: ignore

    def get_resumes(self, resume_ids: list[str]) -> dict[str, Resume]:
        """Return Resume objects keyed by resume_id for the given IDs."""
        result: dict[str, Resume] = {}
        for resume_id in resume_ids:
            resume = self.get_resume(resume_id)
            if resume is not None:
                result[resume_id] = resume
        return result

    def delete_resume(self, resume_id: str) -> bool:
        resume_node = ResumeNode.nodes.get_or_none(uid=resume_id)
        if not resume_node:
            logger.debug("Resume not found for deletion")
            return False

        self.delete_resume_cascade(resume_node)
        logger.info("Deleted resume: %s", resume_node.uid)
        return True

    def delete_resume_cascade(self, resume_node: ResumeNode) -> None:
        query = """
        MATCH (resume:ResumeNode {uid: $uid})
        OPTIONAL MATCH (resume)-[r1]->(n1)
        OPTIONAL MATCH (n1)-[r2]->(n2)
        OPTIONAL MATCH (n2)-[r3]->(n3)

        WITH resume, collect(DISTINCT n1) as nodes1,
             collect(DISTINCT n2) as nodes2,
             collect(DISTINCT n3) as nodes3

        FOREACH (n IN nodes3 | DETACH DELETE n)
        FOREACH (n IN nodes2 | DETACH DELETE n)
        FOREACH (n IN nodes1 | DETACH DELETE n)
        DETACH DELETE resume
        """
        db.cypher_query(query, {"uid": resume_node.uid})
