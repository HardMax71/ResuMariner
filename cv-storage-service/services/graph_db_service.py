import logging
import uuid
from typing import Dict, List, Any, Optional

from models.neo4j_models import (
    Person, CV, Skill, Company, Experience, KeyPoint, Technology,
    Project, Institution, Education, Coursework, EducationExtra,
    Language, Certification, Award, ScientificContribution, Course
)
from neomodel import config, db
from utils.errors import GraphDBError, DatabaseConnectionError

logger = logging.getLogger(__name__)


class GraphDBService:
    """
    Service for storing and retrieving CV data in Neo4j using neomodel
    Useful links:
    - Batch operations: https://github.com/neo4j-contrib/neomodel/blob/5bc4213598233172526cd3c59fdfed5745a80130/doc/source/batch.rst#create_or_update
    """

    def __init__(self, uri: str, username: str, password: str):
        """Initialize the graph database service

        Args:
            uri: Neo4j connection URI
            username: Neo4j username
            password: Neo4j password
        """
        try:
            # Configure neomodel
            config.DATABASE_URL = f"bolt://{username}:{password}@{uri.replace('bolt://', '')}"

            # Test the connection
            result, _ = db.cypher_query("MATCH (n) RETURN COUNT(n) AS count LIMIT 1")
            logger.debug(f"Database connection verified, node count: {result[0][0]}")

            self._initialize_db()
            logger.info(f"Connected to Neo4j at {uri}")
        except Exception as e:
            logger.error(f"Failed to connect to Neo4j: {str(e)}")
            raise DatabaseConnectionError(f"Neo4j connection failed: {str(e)}")

    def _initialize_db(self) -> None:
        """Initialize database with constraints and indexes"""
        try:
            # Stupid idea of removing and reinstalling labels comes from:
            # https://github.com/neo4j-contrib/neomodel/issues/539#issuecomment-906157466
            db.remove_all_labels()
            db.install_all_labels()
            logger.info("Neo4j constraints and indexes installed via neomodel")
        except Exception as e:
            logger.error(f"Error initializing Neo4j schema: {str(e)}", exc_info=True)
            raise GraphDBError(f"Failed to initialize Neo4j schema: {str(e)}")

    def store_cv(self, cv_data: Dict[str, Any], job_id: Optional[str] = None) -> str:
        """Store a CV in the graph database, preventing duplicates

        Args:
            cv_data: CV data as dictionary
            job_id: Optional job ID to use (generates new UUID if not provided)

        Returns:
            CV ID in the graph database
        """
        cv_id = job_id or str(uuid.uuid4())

        try:
            # Validate essential data presence
            personal_info = cv_data.get("personal_info", {})
            if not personal_info or not personal_info.get("contact", {}).get("email"):
                logger.error("Missing required personal info in CV data")
                raise GraphDBError("CV data missing required personal information")

            # Extract identifying information
            email = personal_info.get("contact", {}).get("email")
            name = personal_info.get("name", "Unknown")
            phone = personal_info.get("contact", {}).get("phone")

            # Check for existing person with same email (primary identifier)
            existing_person = self.find_existing_person(email, name, phone)

            # If person exists, delete their existing CVs to avoid duplicates
            if existing_person and existing_person.get("cv_ids"):
                for existing_cv_id in existing_person["cv_ids"]:
                    try:
                        self.delete_cv(existing_cv_id)
                        logger.info(f"Deleted existing CV {existing_cv_id} for {email}")
                    except Exception as e:
                        logger.warning(f"Error deleting existing CV {existing_cv_id}: {str(e)}")

            # Create Person and CV nodes
            person, cv = self._create_person_and_cv(cv_id, cv_data)
            logger.info(f"{'Updated' if existing_person else 'Created'} person and CV nodes for {cv_id}")

            # Add relationships and related nodes
            self._add_skills(person, cv_data)
            self._add_employment_history(person, cv_data)
            self._add_education(person, cv_data)
            self._add_projects(person, cv_data)
            self._add_languages(person, cv_data)
            self._add_certifications(person, cv_data)
            self._add_awards(person, cv_data)
            self._add_scientific_contributions(person, cv_data)
            self._add_courses(person, cv_data)

            return cv_id
        except Exception as e:
            logger.error(f"Error storing CV: {str(e)}")
            raise GraphDBError(f"Failed to store CV data: {str(e)}")

    def _create_person_and_cv(self, cv_id: str, cv_data: Dict[str, Any]) -> tuple[Person, CV]:
        """Create Person and CV nodes using neomodel"""
        try:
            personal_info = cv_data.get("personal_info", {})
            name = personal_info.get("name", "Unknown")
            email = personal_info.get("contact", {}).get("email", f"unknown_{cv_id}@example.com")
            phone = personal_info.get("contact", {}).get("phone")

            # Extract contact links
            contact_links = personal_info.get("contact", {}).get("links", {})
            github_url = contact_links.get("github") if contact_links else None
            linkedin_url = contact_links.get("linkedin") if contact_links else None
            telegram_url = contact_links.get("telegram") if contact_links else None
            other_links = contact_links.get("other_links", {}) if contact_links else {}

            # Extract location data
            location = personal_info.get("demographics", {}).get("current_location", {})
            city = location.get("city")
            state = location.get("state")
            country = location.get("country")

            # Extract work authorization
            work_auth = personal_info.get("demographics", {}).get("work_authorization", {})
            citizenship = work_auth.get("citizenship")
            work_permit = work_auth.get("work_permit")
            visa_sponsorship_required = work_auth.get("visa_sponsorship_required")

            # Extract professional profile
            professional_profile = cv_data.get("professional_profile", {})
            summary = professional_profile.get("summary", "")
            preferences = professional_profile.get("preferences", {})
            role = preferences.get("role", "")
            salary = preferences.get("salary")

            # create_or_update returns a list of nodes, so we take the first element
            person = Person.create_or_update({
                "email": email,  # Unique property used for matching
                "name": name,
                "phone": phone,
                "city": city,
                "state": state,
                "country": country,
                "github_url": github_url,
                "linkedin_url": linkedin_url,
                "telegram_url": telegram_url,
                "other_links": other_links,
                "citizenship": citizenship,
                "work_permit": work_permit,
                "visa_sponsorship_required": visa_sponsorship_required
            })[0]

            # Create the CV node
            cv = CV(
                cv_id=cv_id,
                summary=summary,
                desired_role=role,
                salary_expectation=salary,
                resume_lang=personal_info.get("resume_lang", "en")
            ).save()

            # Connect Person to CV
            person.cv.connect(cv)

            return person, cv
        except Exception as e:
            logger.error(f"Error creating person and CV nodes: {str(e)}")
            raise GraphDBError(f"Failed to create base CV record: {str(e)}")

    def _add_skills(self, person: Person, cv_data: Dict[str, Any]) -> None:
        """Add skills to a person using neomodel with create_or_update"""
        skills = cv_data.get("skills", []) or []
        skills_created = 0

        for skill_name in skills:
            try:
                skill = Skill.create_or_update({"name": skill_name})[0]
                if not person.skills.is_connected(skill):
                    person.skills.connect(skill)
                    skills_created += 1
            except Exception as e:
                logger.warning(f"Error creating skill {skill_name}: {str(e)}")

        logger.debug(f"Created {skills_created} skill relationships for person {person.email}")

    def _add_employment_history(self, person: Person, cv_data: Dict[str, Any]) -> None:
        """Add employment history to a person using neomodel with upserting"""
        jobs = cv_data.get("employment_history", []) or []
        created_count = 0

        for job in jobs:
            try:
                company_name = job.get("company", "Unknown")
                position = job.get("position", "Unknown")

                # Get duration details
                duration = job.get("duration", {})
                start_date = duration.get("start", "Unknown")
                end_date = duration.get("end", "current")
                duration_months = duration.get("duration_months", 0)

                # Get location details
                location = job.get("location", {})
                city = location.get("city")
                state = location.get("state")
                country = location.get("country")

                # Get employment type and work mode
                employment_type = job.get("employment_type", "full-time")
                work_mode = job.get("work_mode", "onsite")

                # Create Experience node
                experience = Experience(
                    position=position,
                    start_date=start_date,
                    end_date=end_date,
                    duration_months=duration_months,
                    employment_type=employment_type,
                    work_mode=work_mode,
                    city=city,
                    state=state,
                    country=country
                ).save()

                # Connect Person to Experience
                person.experiences.connect(experience)

                # Upsert Company node using create_or_update (using name as unique identifier)
                company = Company.create_or_update({"name": company_name})[0]
                experience.company.connect(company)

                created_count += 1

                # Add key points (no upsert here as they are typically unique per experience)
                key_points = job.get("key_points", [])
                for idx, point_text in enumerate(key_points):
                    if not point_text:  # Skip empty points
                        continue
                    key_point = KeyPoint(
                        text=point_text,
                        index=idx,
                        source="experience"
                    ).save()
                    experience.key_points.connect(key_point)

                # Upsert technologies using create_or_update (using name as unique identifier)
                tech_stack = job.get("tech_stack", [])
                for tech_name in tech_stack:
                    tech = Technology.create_or_update({"name": tech_name})[0]
                    experience.technologies.connect(tech)

            except Exception as e:
                logger.warning(f"Error creating job experience: {str(e)}")

        logger.info(f"Created {created_count} job experiences for person {person.email}")

    def _add_education(self, person: Person, cv_data: Dict[str, Any]) -> None:
        """Add education to a person using neomodel with upserting for the Institution node"""
        education_items = cv_data.get("education", []) or []
        created_count = 0

        for edu in education_items:
            try:
                institution_name = edu.get("institution", "Unknown")
                qualification = edu.get("qualification", "Unknown")
                study_field = edu.get("study_field", "Unknown")
                start = edu.get("start")
                end = edu.get("end")
                status = edu.get("status", "completed")

                # Get location details
                location = edu.get("location", {})
                city = location.get("city")
                state = location.get("state")
                country = location.get("country")

                # Create Education node
                education = Education(
                    qualification=qualification,
                    field=study_field,
                    start=start,
                    end=end,
                    status=status,
                    city=city,
                    state=state,
                    country=country
                ).save()

                # Connect Person to Education
                person.education.connect(education)

                # Upsert Institution node using create_or_update (using 'name' as unique identifier)
                institution = Institution.create_or_update({"name": institution_name})[0]
                education.institution.connect(institution)

                created_count += 1

                # Add coursework
                coursework_items = edu.get("coursework", []) or []
                for idx, course_text in enumerate(coursework_items):
                    coursework = Coursework(
                        text=course_text,
                        index=idx
                    ).save()
                    education.coursework.connect(coursework)

                # Add extras
                extras_items = edu.get("extras", []) or []
                for idx, extra_text in enumerate(extras_items):
                    extra = EducationExtra(
                        text=extra_text,
                        index=idx
                    ).save()

                    education.extras.connect(extra)

            except Exception as e:
                logger.warning(f"Error creating education record: {str(e)}", exc_info=True)

        logger.info(f"Created {created_count} education records for person {person.email}")

    def _add_projects(self, person: Person, cv_data: Dict[str, Any]) -> None:
        """Add projects to a person using neomodel with upserting"""
        projects_data = cv_data.get("projects", []) or []
        created_count = 0

        for project_data in projects_data:
            try:
                title = project_data.get("title", "Unknown")
                url = project_data.get("url")

                # Upsert Project node using create_or_update, using title and url as unique identifiers
                project = Project.create_or_update({
                    "title": title,
                    "url": url
                })[0]

                # Connect Person to Project if not already connected
                if not person.projects.is_connected(project):
                    person.projects.connect(project)

                created_count += 1

                # Add key points (these are created as new nodes since they're specific to this project)
                key_points = project_data.get("key_points", [])
                for idx, point_text in enumerate(key_points):
                    key_point = KeyPoint(
                        text=point_text,
                        index=idx,
                        source="project"
                    ).save()

                    project.key_points.connect(key_point)

                tech_stack = project_data.get("tech_stack", [])
                for tech_name in tech_stack:
                    tech = Technology.create_or_update({"name": tech_name})[0]
                    if not project.technologies.is_connected(tech):
                        project.technologies.connect(tech)

            except Exception as e:
                logger.warning(f"Error creating project: {str(e)}", exc_info=True)

        logger.info(f"Created {created_count} projects for person {person.email}")

    def _add_languages(self, person: Person, cv_data: Dict[str, Any]) -> None:
        """Add language proficiencies to a person using neomodel with upserting"""
        languages_data = cv_data.get("language_proficiency", []) or []
        languages_created = 0

        for lang_data in languages_data:
            try:
                language_name = lang_data.get("language", "Unknown")
                level_data = lang_data.get("level", {})
                self_assessed = level_data.get("self_assessed", "Unknown")
                cefr = level_data.get("cefr", "Unknown")

                # Upsert Language node using create_or_update (using 'name' as the unique identifier)
                language = Language.create_or_update({"name": language_name})[0]
                person.languages.connect(language, {
                    "self_assessed": self_assessed,
                    "cefr": cefr
                })

                languages_created += 1

            except Exception as e:
                logger.warning(f"Error creating language proficiency: {str(e)}", exc_info=True)

        logger.debug(f"Added {languages_created} language proficiencies to person {person.email}")

    def _add_certifications(self, person: Person, cv_data: Dict[str, Any]) -> None:
        """Add certifications to a person using neomodel"""
        certifications_data = cv_data.get("certifications", []) or []
        created_count = 0

        for cert_data in certifications_data:
            try:
                name = cert_data.get("name")
                issue_org = cert_data.get("issue_org")
                issue_year = cert_data.get("issue_year")
                certificate_link = cert_data.get("certificate_link")

                # Create Certification node
                certification = Certification(
                    name=name,
                    issue_org=issue_org,
                    issue_year=issue_year,
                    certificate_link=certificate_link
                ).save()

                # Connect Person to Certification
                person.certifications.connect(certification)
                created_count += 1

            except Exception as e:
                logger.warning(f"Error creating certification: {str(e)}", exc_info=True)

        logger.debug(f"Added {created_count} certifications to person {person.email}")

    def _add_courses(self, person: Person, cv_data: Dict[str, Any]) -> None:
        """Add courses to a person using neomodel"""
        courses_data = cv_data.get("courses", []) or []
        created_count = 0

        for course_data in courses_data:
            try:
                name = course_data.get("name")
                if not name:
                    continue

                organization = course_data.get("organization", "Unknown")
                year = course_data.get("year")
                course_url = course_data.get("course_url")
                certificate_url = course_data.get("certificate_url")

                # Create Course node
                course = Course(
                    name=name,
                    organization=organization,
                    year=year,
                    course_url=course_url,
                    certificate_url=certificate_url
                ).save()

                # Connect person to course using the relationship
                person.courses.connect(course)
                created_count += 1

            except Exception as e:
                logger.warning(f"Error creating course: {str(e)}", exc_info=True)

        logger.debug(f"Added {created_count} courses to person {person.email}")

    def _add_awards(self, person: Person, cv_data: Dict[str, Any]) -> None:
        """Add awards to a person using neomodel"""
        awards_data = cv_data.get("awards", []) or []
        created_count = 0

        for award_data in awards_data:
            try:
                name = award_data.get("name", "Unknown Award")
                award_type = award_data.get("award_type", "other")
                organization = award_data.get("organization", "Unknown")
                year = award_data.get("year")
                position = award_data.get("position")
                description = award_data.get("description")
                url = award_data.get("url")

                # Create Award node
                award = Award(
                    name=name,
                    award_type=award_type,
                    organization=organization,
                    year=year,
                    position=position,
                    description=description,
                    url=url
                ).save()

                # Connect Person to Award
                person.awards.connect(award)

                created_count += 1

            except Exception as e:
                logger.warning(f"Error creating award: {str(e)}", exc_info=True)

        logger.debug(f"Added {created_count} awards to person {person.email}")

    def _add_scientific_contributions(self, person: Person, cv_data: Dict[str, Any]) -> None:
        """Add scientific contributions to a person using neomodel"""
        contributions_data = cv_data.get("scientific_contributions", []) or []
        created_count = 0

        for contribution_data in contributions_data:
            try:
                title = contribution_data.get("title", "Unknown Contribution")
                publication_type = contribution_data.get("publication_type", "other")
                year = contribution_data.get("year")
                venue = contribution_data.get("venue")
                doi = contribution_data.get("doi")
                url = contribution_data.get("url")
                description = contribution_data.get("description")

                # Create ScientificContribution node
                contribution = ScientificContribution(
                    title=title,
                    publication_type=publication_type,
                    year=year,
                    venue=venue,
                    doi=doi,
                    url=url,
                    description=description
                ).save()
                person.scientific_contributions.connect(contribution)

                created_count += 1

            except Exception as e:
                logger.warning(f"Error creating scientific contribution: {str(e)}", exc_info=True)

        logger.debug(f"Added {created_count} scientific contributions to person {person.email}")

    def find_existing_person(self, email: str, name: str = None, phone: str = None) -> Optional[Dict[str, Any]]:
        """Find an existing person and their CV based on contact information using neomodel

        Args:
            email: Person's email (primary identifier)
            name: Person's name (optional, for additional matching)
            phone: Person's phone number (optional, for additional matching)

        Returns:
            Dictionary with person details and CV IDs if found, None otherwise
        """
        # Create filters with only non-None values in a single expression
        filters = {k: v for k, v in {"email": email, "name": name, "phone": phone}.items() if v is not None}

        person = Person.nodes.filter(**filters).first_or_none()
        if not person:
            return None

        return {
            "email": person.email,
            "name": person.name,
            "phone": person.phone,
            "cv_ids": [cv.cv_id for cv in person.cv.all()]
        }

    def get_cv_details(self, cv_ids: List[str]) -> Dict[str, Dict[str, Any]]:
        """Get basic details for a list of CVs using neomodel

        Args:
            cv_ids: List of CV IDs to retrieve

        Returns:
            Dictionary mapping CV IDs to CV details
        """
        result = {}

        for cv_id in cv_ids:
            cv_node = CV.nodes.filter(cv_id=cv_id).first_or_none()
            if not cv_node:
                logger.warning(f"CV with ID {cv_id} not found")
                continue

            # Get the connected person.
            person = cv_node.person.first()

            # Build experiences list.
            experiences = []
            for exp in person.experiences.all():
                company = exp.company.get()
                experiences.append({
                    "company": company.name,
                    "position": exp.position,
                })
            skills = [skill.name for skill in person.skills.all()]

            result[cv_id] = {
                "name": person.name,
                "email": person.email,
                "city": person.city,
                "country": person.country,
                "summary": cv_node.summary,
                "desired_role": cv_node.desired_role,
                "experiences": experiences,
                "skills": skills
            }

        return result

    def delete_cv(self, cv_id: str) -> bool:
        """Delete a CV and all related nodes using neomodel"""
        cv = CV.nodes.get_or_none(cv_id=cv_id)
        if not cv:
            logger.warning(f"CV with ID {cv_id} not found")
            return False
        try:
            # Delete related nodes and relationships for this person
            # We'll use Cypher for this to handle complex cascading deletion
            db.cypher_query(
                """
                MATCH (cv:CV {cv_id: $cv_id})  
                OPTIONAL MATCH (p:Person)-[:HAS_CV]->(cv)

                // Get all experiences
                OPTIONAL MATCH (p)-[:HAD_EXPERIENCE]->(exp:Experience)
                OPTIONAL MATCH (exp)-[:HAS_KEY_POINT]->(kp:KeyPoint)

                // Get all projects
                OPTIONAL MATCH (p)-[:COMPLETED_PROJECT]->(proj:Project)
                OPTIONAL MATCH (proj)-[:HAS_KEY_POINT]->(pkp:KeyPoint)

                // Get all education records
                OPTIONAL MATCH (p)-[:EDUCATED_AT]->(edu:Education)
                OPTIONAL MATCH (edu)-[:INCLUDES_COURSEWORK]->(cw:Coursework)
                OPTIONAL MATCH (edu)-[:HAS_EXTRA]->(ex:EducationExtra)

                // Get other records
                OPTIONAL MATCH (p)-[:COMPLETED_COURSE]->(course:Course)
                OPTIONAL MATCH (p)-[:HAS_CERTIFICATION]->(cert:Certification)
                OPTIONAL MATCH (p)-[:RECEIVED_AWARD]->(award:Award)
                OPTIONAL MATCH (p)-[:AUTHORED]->(sc:ScientificContribution)

                // Delete all related nodes but NOT the shared ones (Company, Tech, etc.)
                DETACH DELETE exp, kp, proj, pkp, edu, cw, ex, course, cert, award, sc

                // Delete the CV itself, but keep the person
                DETACH DELETE cv
                """,
                {"cv_id": cv_id}  # This now refers to the cv_id property
            )
            logger.info(f"Successfully deleted CV {cv_id} and related nodes")
            return True
        except Exception as e:
            logger.error(f"Error deleting CV {cv_id}: {str(e)}")
            raise GraphDBError(f"Failed to delete CV: {str(e)}")
