import logging
import uuid
from typing import Dict, List, Any, Optional

from models.neo4j_models import (
    CVNode,
    PersonalInfoNode,
    ProfessionalProfileNode,
    SkillNode,
    EmploymentHistoryItemNode,
    ProjectNode,
    EducationItemNode,
    CourseNode,
    CertificationNode,
    LanguageProficiencyNode,
    AwardNode,
    ScientificContributionNode,
)
from neomodel import config, install_all_labels, db
from utils.errors import GraphDBError, DatabaseConnectionError

from pydantic_neomodel_dict import Converter

logger = logging.getLogger(__name__)


class GraphDBService:
    """
    A simplified GraphDB service for storing and retrieving CV data.

    Assumes the incoming data is a validated dump of a ResumeStructure instance.
    Conversion between dicts and neomodel OGM models is handled via Converter.
    No nested transactions are started.
    """

    def __init__(self, uri: str, username: str, password: str):
        try:
            config.DATABASE_URL = f"bolt://{username}:{password}@{uri.replace('bolt://', '')}"
            install_all_labels()

            logger.info(f"Connected to Neo4j at {uri}")
        except Exception as e:
            logger.error(f"Failed to connect to Neo4j: {e}", exc_info=True)
            raise DatabaseConnectionError(f"Neo4j connection failed: {e}")

    def find_existing_cv_by_email(self, email: str) -> Optional[CVNode]:
        """Find an existing CV by email via its connected Contact node."""
        try:
            query = """
            MATCH (cv:CVNode)-[:HAS_PERSONAL_INFO]->(p:PersonalInfoNode)-[:HAS_CONTACT]->(c:ContactNode)
            WHERE c.email = $email
            RETURN cv
            """
            results, _ = db.cypher_query(query, {"email": email})
            if results:
                # Inflate the raw Neo4j Node to a CVNode instance
                return [CVNode.inflate(row[0]) for row in results]
            return None
        except Exception as e:
            logger.error(f"Error finding CV for email {email}: {e}", exc_info=True)
            return None

    def delete_cv_by_email(self, email: str) -> bool:
        """Delete all CVs and related nodes for a given email."""
        try:
            # Execute a Cypher query that finds and deletes all CVs with this email
            query = """
            MATCH (cv:CVNode)-[:HAS_PERSONAL_INFO]->(p:PersonalInfoNode)-[:HAS_CONTACT]->(c:ContactNode)
            WHERE c.email = $email

            // Find everything connected to the CV up to 4 levels deep
            OPTIONAL MATCH (cv)-[r1]->(n1)
            OPTIONAL MATCH (n1)-[r2]->(n2)
            OPTIONAL MATCH (n2)-[r3]->(n3)
            OPTIONAL MATCH (n3)-[r4]->(n4)

            // Check if nodes have other incoming relationships
            WITH 
                cv,
                n1, NOT EXISTS { MATCH (n1)<-[r]-(other) WHERE other <> cv } as n1_delete,
                n2, NOT EXISTS { MATCH (n2)<-[r]-(other) WHERE other <> n1 } as n2_delete,
                n3, NOT EXISTS { MATCH (n3)<-[r]-(other) WHERE other <> n2 } as n3_delete,
                n4, NOT EXISTS { MATCH (n4)<-[r]-(other) WHERE other <> n3 } as n4_delete

            // Delete the CV nodes first
            DETACH DELETE cv

            // Delete related nodes if they don't have other relationships
            WITH n1, n1_delete, n2, n2_delete, n3, n3_delete, n4, n4_delete
            WHERE n1 IS NOT NULL AND n1_delete = true
            DETACH DELETE n1

            WITH n2, n2_delete, n3, n3_delete, n4, n4_delete
            WHERE n2 IS NOT NULL AND n2_delete = true
            DETACH DELETE n2

            WITH n3, n3_delete, n4, n4_delete
            WHERE n3 IS NOT NULL AND n3_delete = true
            DETACH DELETE n3

            WITH n4, n4_delete
            WHERE n4 IS NOT NULL AND n4_delete = true
            DETACH DELETE n4
            """

            result, _ = db.cypher_query(query, {"email": email})
            logger.info(f"Deleted all CVs for email {email}")
            return True

        except Exception as e:
            logger.error(f"Error deleting CVs for email {email}: {e}", exc_info=True)
            raise GraphDBError(f"Failed to delete CVs for email {email}: {e}")

    @db.transaction
    def store_cv(self, cv_data: Dict[str, Any], job_id: Optional[str] = None) -> str:
        """
        Store a CV from a ResumeStructure model dump.

        This method converts each section of cv_data into its corresponding OGM node
        and connects them to a new CVNode. If a CV for the same email already exists,
        it is first deleted.
        """
        cv_id = job_id or str(uuid.uuid4())
        try:
            email = cv_data["personal_info"]["contact"]["email"]

            # Delete any existing CV for this email.
            existing_cvs = self.find_existing_cv_by_email(email)
            if existing_cvs:
                for existing_cv in existing_cvs:
                    self.delete_cv_by_email(email)
                    logger.info(f"Deleted existing CV with ID {existing_cv.uid} for email {email}")

            # Convert sections to OGM nodes.
            personal_info = Converter.dict_to_ogm(cv_data["personal_info"], PersonalInfoNode)
            professional_profile = Converter.dict_to_ogm(cv_data["professional_profile"], ProfessionalProfileNode)

            # Create a new CV node; additional properties (e.g. timestamps) may be set via defaults.
            cv_fields = {"uid": cv_id}
            cv_node = Converter.dict_to_ogm(cv_fields, CVNode)

            # Connect the sections to the CV.
            cv_node.personal_info.connect(personal_info)
            cv_node.professional_profile.connect(professional_profile)

            # Process skills.
            for skill_name in cv_data.get("skills", []) or []:
                skill_node = Converter.dict_to_ogm(skill_name, SkillNode)
                cv_node.skills.connect(skill_node)

            # Process employment history.
            for job in cv_data.get("employment_history", []) or []:
                exp = Converter.dict_to_ogm(job, EmploymentHistoryItemNode)
                cv_node.employment_history.connect(exp)

            # Process projects.
            for proj in cv_data.get("projects", []) or []:
                project = Converter.dict_to_ogm(proj, ProjectNode)
                cv_node.projects.connect(project)

            # Process education.
            for edu in cv_data.get("education", []) or []:
                education = Converter.dict_to_ogm(edu, EducationItemNode)
                cv_node.education.connect(education)

            # Process courses.
            for course_data in cv_data.get("courses", []) or []:
                course_node = Converter.dict_to_ogm(course_data, CourseNode)
                cv_node.courses.connect(course_node)

            # Process certifications.
            for cert_data in cv_data.get("certifications", []) or []:
                cert_node = Converter.dict_to_ogm(cert_data, CertificationNode)
                cv_node.certifications.connect(cert_node)

            # Process language proficiency.
            for lang in cv_data.get("language_proficiency", []) or []:
                lang_prof_node = Converter.dict_to_ogm(lang, LanguageProficiencyNode)
                cv_node.language_proficiency.connect(lang_prof_node)

            # Process awards.
            for award in cv_data.get("awards", []) or []:
                award_node = Converter.dict_to_ogm(award, AwardNode)
                cv_node.awards.connect(award_node)

            # Process scientific contributions.
            sci_contrib = cv_data.get("scientific_contributions")
            if sci_contrib:
                contrib = Converter.dict_to_ogm(sci_contrib, ScientificContributionNode)
                cv_node.scientific_contributions.connect(contrib)

            cv_node.save()
            logger.info(f"Stored CV with ID {cv_id} for email {email}")
            return cv_id

        except Exception as e:
            logger.error(f"Error storing CV: {e}", exc_info=True)
            raise GraphDBError(f"Failed to store CV data: {e}")

    def get_cv_details(self, cv_ids: List[str]) -> Dict[str, Dict[str, Any]]:
        """
        Retrieve basic details for a list of CVs.

        Returns a dictionary keyed by CV ID containing summary details.
        """
        result = {}
        try:
            for cv_id in cv_ids:
                try:
                    cv = CVNode.nodes.get(uid=cv_id)
                    # Navigate the relationships to retrieve PersonalInfo.
                    pinfo = cv.personal_info.single()
                    pinfo_dict = Converter.ogm_to_dict(pinfo, include_relationships=False)
                    cv_dict = Converter.ogm_to_dict(cv, include_relationships=False)
                    skills = [skill.name for skill in cv.skills.all()]
                    # Email is stored in the connected Contact node (via PersonalInfo).
                    contact = pinfo_dict.get("contact", {})
                    result[cv_id] = {
                        "name": pinfo_dict.get("name"),
                        "email": contact.get("email"),
                        "summary": cv_dict.get("summary"),
                        "desired_role": cv_dict.get("desired_role"),
                        "skills": skills
                    }
                except Exception as inner_e:
                    logger.warning(f"Error retrieving details for CV {cv_id}: {inner_e}")
            return result
        except Exception as e:
            logger.error(f"Error retrieving CV details: {e}", exc_info=True)
            raise GraphDBError(f"Failed to retrieve CV details: {e}")
