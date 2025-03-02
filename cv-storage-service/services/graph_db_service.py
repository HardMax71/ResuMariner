import logging
import uuid
from typing import Dict, List, Any, Optional

from neo4j import GraphDatabase, exceptions
from utils.errors import GraphDBError, DatabaseConnectionError

logger = logging.getLogger(__name__)


class GraphDBService:
    """Service for storing and retrieving CV data in Neo4j"""

    def __init__(self, uri: str, username: str, password: str):
        """Initialize the graph database service

        Args:
            uri: Neo4j connection URI
            username: Neo4j username
            password: Neo4j password
        """
        try:
            self.driver = GraphDatabase.driver(uri, auth=(username, password))
            self._initialize_db()
            logger.info(f"Connected to Neo4j at {uri}")
        except exceptions.ServiceUnavailable as e:
            logger.error(f"Failed to connect to Neo4j: {str(e)}")
            raise DatabaseConnectionError(f"Neo4j connection failed: {str(e)}")
        except Exception as e:
            logger.error(f"Neo4j initialization error: {str(e)}")
            raise DatabaseConnectionError(f"Neo4j initialization failed: {str(e)}")

    def _initialize_db(self) -> None:
        """Initialize database with constraints and indexes"""
        try:
            with self.driver.session() as session:
                # Create constraint on Person.email
                session.run(
                    "CREATE CONSTRAINT person_email IF NOT EXISTS "
                    "FOR (p:Person) REQUIRE p.email IS UNIQUE"
                )

                # Create constraint on CV.id
                session.run(
                    "CREATE CONSTRAINT cv_id IF NOT EXISTS "
                    "FOR (cv:CV) REQUIRE cv.id IS UNIQUE"
                )

                # Create index on Skill
                session.run(
                    "CREATE INDEX skill_name IF NOT EXISTS "
                    "FOR (s:Skill) ON (s.name)"
                )

                # Create index on Technology
                session.run(
                    "CREATE INDEX tech_name IF NOT EXISTS "
                    "FOR (t:Technology) ON (t.name)"
                )

                # Create index on Company
                session.run(
                    "CREATE INDEX company_name IF NOT EXISTS "
                    "FOR (c:Company) ON (c.name)"
                )

                logger.info("Neo4j constraints and indexes initialized")
        except Exception as e:
            logger.error(f"Error initializing Neo4j schema: {str(e)}")
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

            with self.driver.session() as session:
                # If person exists, delete their existing CVs to avoid duplicates
                if existing_person and existing_person.get("cv_ids"):
                    for existing_cv_id in existing_person["cv_ids"]:
                        try:
                            self.delete_cv(existing_cv_id)
                            logger.info(f"Deleted existing CV {existing_cv_id} for {email}")
                        except Exception as e:
                            logger.warning(f"Error deleting existing CV {existing_cv_id}: {str(e)}")

                # Create Person and CV nodes (MERGE will ensure no duplicate Person nodes)
                self._create_person_and_cv(session, cv_id, cv_data)
                logger.info(f"{'Updated' if existing_person else 'Created'} person and CV nodes for {cv_id}")

                # Continue with creating relationships
                if cv_data.get("skills"):
                    self._create_skills(session, cv_id, cv_data)

                if cv_data.get("employment_history"):
                    self._create_employment_history(session, cv_id, cv_data)

                if cv_data.get("education"):
                    self._create_education(session, cv_id, cv_data)

                if cv_data.get("projects"):
                    self._create_projects(session, cv_id, cv_data)

                if cv_data.get("language_proficiency"):
                    self._create_languages(session, cv_id, cv_data)

                if cv_data.get("certifications"):
                    self._create_certifications(session, cv_id, cv_data)

                if cv_data.get("awards"):
                    self._create_awards(session, cv_id, cv_data)

                if cv_data.get("scientific_contributions"):
                    self._create_scientific_contributions(session, cv_id, cv_data)

            return cv_id
        except GraphDBError:
            raise
        except Exception as e:
            logger.error(f"Error storing CV: {str(e)}")
            raise GraphDBError(f"Failed to store CV data: {str(e)}")

    def _create_person_and_cv(self, session, cv_id: str, cv_data: Dict[str, Any]) -> None:
        """Create Person and CV nodes"""
        personal_info = cv_data.get("personal_info", {})
        name = personal_info.get("name", "Unknown")
        email = personal_info.get("contact", {}).get("email", f"unknown_{cv_id}@example.com")

        # Extract location data
        location = personal_info.get("demographics", {}).get("current_location", {})
        city = location.get("city")
        state = location.get("state")
        country = location.get("country")

        # Extract professional profile
        professional_profile = cv_data.get("professional_profile", {})
        summary = professional_profile.get("summary", "")

        # Extract preferences
        preferences = professional_profile.get("preferences", {})
        role = preferences.get("role", "")
        salary = preferences.get("salary")

        # Create more detailed person node with all available info
        person_props = {
            "email": email,
            "name": name
        }

        if city:
            person_props["city"] = city
        if state:
            person_props["state"] = state
        if country:
            person_props["country"] = country

        # Make CV node properties
        cv_props = {
            "id": cv_id,
            "created_at": "datetime()",  # Neo4j function, executed in Cypher
            "summary": summary,
            "desired_role": role
        }

        if salary:
            cv_props["salary_expectation"] = salary

        # Build the query dynamically based on available properties
        person_props_str = ", ".join([f"p.{k} = ${k}" for k in person_props.keys()])
        cv_props_str = ", ".join([f"cv.{k} = ${k}" for k in cv_props.keys() if k != "created_at"])

        # Create nodes with all properties
        query = f"""
        MERGE (p:Person {{email: $email}})
        SET {person_props_str}
        CREATE (cv:CV {{id: $id, created_at: datetime()}})
        SET {cv_props_str}
        CREATE (p)-[:HAS_CV]->(cv)
        """

        # Combine all parameters and add cv_id explicitly
        params = {**person_props, **cv_props, "cv_id": cv_id}

        try:
            result = session.run(query, params)
            # Check if operation succeeded
            summary = result.consume()
            if summary.counters.nodes_created == 0:
                logger.warning(f"No nodes created for CV {cv_id}")
        except Exception as e:
            logger.error(f"Error creating person and CV nodes: {str(e)}")
            raise GraphDBError(f"Failed to create base CV record: {str(e)}")

    def _create_skills(self, session, cv_id: str, cv_data: Dict[str, Any]) -> None:
        """Create Skill nodes and relationships"""
        skills = cv_data.get("skills", [])

        if not skills:
            return

        skills_created = 0
        try:
            for skill in skills:
                if not skill:  # Skip empty skills
                    continue

                result = session.run(
                    """
                    MATCH (p:Person)-[:HAS_CV]->(cv:CV)
                    WHERE cv.id = $cv_id
                    MERGE (s:Skill {name: $skill})
                    MERGE (p)-[:HAS_SKILL]->(s)
                    """,
                    cv_id=cv_id,
                    skill=skill
                )
                # Check if operation succeeded
                summary = result.consume()
                if summary.counters.relationships_created > 0:
                    skills_created += 1

            logger.debug(f"Created {skills_created} skill relationships for CV {cv_id}")
        except Exception as e:
            logger.error(f"Error creating skills: {str(e)}")
            # Continue execution, don't fail the entire CV storage

    def _create_employment_history(self, session, cv_id: str, cv_data: Dict[str, Any]) -> None:
        """Create employment history with key points"""
        jobs = cv_data.get("employment_history", [])

        if not jobs:
            return

        created_count = 0
        for job in jobs:
            try:
                company = job.get("company", "Unknown")
                position = job.get("position", "Unknown")
                start_date = job.get("duration", {}).get("start", "Unknown")
                end_date = job.get("duration", {}).get("end", "current")
                duration_months = job.get("duration", {}).get("duration_months", 0)

                # Location details - handle None case
                location = job.get("location") or {}
                city = location.get("city")
                state = location.get("state")
                country = location.get("country")

                location_props = {}
                if city:
                    location_props["city"] = city
                if state:
                    location_props["state"] = state
                if country:
                    location_props["country"] = country

                location_str = ", ".join(f"{k}: ${k}_loc" for k in location_props.keys())
                location_params = {f"{k}_loc": v for k, v in location_props.items()}

                # Create company and position
                result = session.run(
                    f"""
                    MATCH (p:Person)-[:HAS_CV]->(cv:CV)
                    WHERE cv.id = $cv_id
                    MERGE (c:Company {{name: $company}})
                    CREATE (exp:Experience {{
                        position: $position,
                        start_date: $start_date,
                        end_date: $end_date,
                        employment_type: $employment_type,
                        work_mode: $work_mode,
                        duration_months: $duration_months
                        {', ' + location_str if location_props else ''}
                    }})
                    CREATE (p)-[:HAD_EXPERIENCE]->(exp)
                    CREATE (exp)-[:AT_COMPANY]->(c)
                    RETURN elementId(exp) AS exp_id
                    """,
                    cv_id=cv_id,
                    company=company,
                    position=position,
                    start_date=start_date,
                    end_date=end_date,
                    employment_type=job.get("employment_type", "full-time"),
                    work_mode=job.get("work_mode", "onsite"),
                    duration_months=duration_months,
                    **location_params
                )

                # Check if we have a valid result
                record = result.single()
                if record is None:
                    logger.warning(f"Failed to create experience for CV {cv_id} at company {company}")
                    continue

                exp_id = record["exp_id"]
                created_count += 1

                # Make sure key_points is a list even if None
                key_points = job.get("key_points") or []
                for idx, point in enumerate(key_points):
                    if not point:  # Skip empty points
                        continue

                    session.run(
                        """
                        MATCH (exp:Experience)
                        WHERE elementId(exp) = $exp_id
                        CREATE (kp:KeyPoint {
                            text: $text,
                            index: $index,
                            source: 'experience'
                        })
                        CREATE (exp)-[:HAS_KEY_POINT]->(kp)
                        """,
                        exp_id=exp_id,
                        text=point,
                        index=idx
                    )

                # Make sure tech_stack is a list even if None
                tech_stack = job.get("tech_stack") or []
                for tech in tech_stack:
                    if not tech:  # Skip empty tech entries
                        continue

                    session.run(
                        """
                        MATCH (exp:Experience)
                        WHERE elementId(exp) = $exp_id
                        MERGE (t:Technology {name: $tech})
                        CREATE (exp)-[:USES_TECHNOLOGY]->(t)
                        """,
                        exp_id=exp_id,
                        tech=tech
                    )

            except Exception as e:
                logger.error(f"Error creating job experience: {str(e)}")
                # Continue with next job

        # Log actual count created
        logger.info(f"Created {created_count} job experiences for CV {cv_id}")

    def _create_education(self, session, cv_id: str, cv_data: Dict[str, Any]) -> None:
        """Create education nodes and relationships"""
        education_items = cv_data.get("education", [])

        if not education_items:
            return

        created_count = 0
        for edu in education_items:
            try:
                institution = edu.get("institution", "Unknown")
                qualification = edu.get("qualification", "Unknown")
                study_field = edu.get("study_field", "Unknown")
                start = edu.get("start")
                end = edu.get("end")
                status = edu.get("status", "completed")

                # Extract location details if available - handle None case
                location = edu.get("location") or {}
                city = location.get("city")
                state = location.get("state")
                country = location.get("country")

                # Build location part of query
                location_props = {}
                if city:
                    location_props["city"] = city
                if state:
                    location_props["state"] = state
                if country:
                    location_props["country"] = country

                location_str = ", ".join(f"{k}: ${k}_loc" for k in location_props.keys())
                location_params = {f"{k}_loc": v for k, v in location_props.items()}

                # Create education node with all details
                result = session.run(
                    f"""
                    MATCH (p:Person)-[:HAS_CV]->(cv:CV)
                    WHERE cv.id = $cv_id
                    MERGE (i:Institution {{name: $institution}})
                    CREATE (e:Education {{
                        qualification: $qualification,
                        field: $study_field,
                        start: $start,
                        end: $end,
                        status: $status
                        {', ' + location_str if location_props else ''}
                    }})
                    CREATE (p)-[:EDUCATED_AT]->(e)
                    CREATE (e)-[:AT_INSTITUTION]->(i)
                    RETURN elementId(e) AS edu_id
                    """,
                    cv_id=cv_id,
                    institution=institution,
                    qualification=qualification,
                    study_field=study_field,
                    start=start,
                    end=end,
                    status=status,
                    **location_params
                )

                # Safety check for result
                record = result.single()
                if record is None:
                    logger.warning(f"No education record created for CV {cv_id} and institution {institution}")
                    continue  # Skip to the next education record

                edu_id = record["edu_id"]
                created_count += 1

                # Make sure coursework and extras are lists even if None
                coursework = edu.get("coursework") or []
                extras = edu.get("extras") or []

                # Add coursework if available
                for idx, course in enumerate(coursework):
                    if not course:  # Skip empty coursework
                        continue

                    session.run(
                        """
                        MATCH (e:Education)
                        WHERE elementId(e) = $edu_id
                        CREATE (c:Coursework {
                            text: $text,
                            index: $index
                        })
                        CREATE (e)-[:INCLUDES_COURSEWORK]->(c)
                        """,
                        edu_id=edu_id,
                        text=course,
                        index=idx
                    )

                # Add extras if available
                for idx, extra in enumerate(extras):
                    if not extra:  # Skip empty extras
                        continue

                    session.run(
                        """
                        MATCH (e:Education)
                        WHERE elementId(e) = $edu_id
                        CREATE (ex:EducationExtra {
                            text: $text,
                            index: $index
                        })
                        CREATE (e)-[:HAS_EXTRA]->(ex)
                        """,
                        edu_id=edu_id,
                        text=extra,
                        index=idx
                    )
            except Exception as e:
                logger.error(f"Error creating education record: {str(e)}")
                # Continue with next education item

        # Log actual count created instead of input list length
        logger.info(f"Created {created_count} education records for CV {cv_id}")

    def _create_projects(self, session, cv_id: str, cv_data: Dict[str, Any]) -> None:
        """Create project nodes and relationships"""
        projects = cv_data.get("projects", [])

        if not projects:
            return

        created_count = 0
        for project in projects:
            try:
                title = project.get("title", "Unknown")
                url = project.get("url")

                result = session.run(
                    """
                    MATCH (p:Person)-[:HAS_CV]->(cv:CV)
                    WHERE cv.id = $cv_id
                    CREATE (proj:Project {
                        title: $title,
                        url: $url
                    })
                    CREATE (p)-[:COMPLETED_PROJECT]->(proj)
                    RETURN elementId(proj) AS proj_id
                    """,
                    cv_id=cv_id,
                    title=title,
                    url=url
                )

                # Check if we have a valid result
                record = result.single()
                if record is None:
                    logger.warning(f"Failed to create project for CV {cv_id} with title {title}")
                    continue

                proj_id = record["proj_id"]
                created_count += 1

                # Make sure key_points is a list even if None
                key_points = project.get("key_points") or []
                for idx, point in enumerate(key_points):
                    if not point:
                        continue

                    session.run(
                        """
                        MATCH (proj:Project)
                        WHERE elementId(proj) = $proj_id
                        CREATE (kp:KeyPoint {
                            text: $text,
                            index: $index,
                            source: 'project'
                        })
                        CREATE (proj)-[:HAS_KEY_POINT]->(kp)
                        """,
                        proj_id=proj_id,
                        text=point,
                        index=idx
                    )

                # Make sure tech_stack is a list even if None
                tech_stack = project.get("tech_stack") or []
                for tech in tech_stack:
                    if not tech:
                        continue

                    session.run(
                        """
                        MATCH (proj:Project)
                        WHERE elementId(proj) = $proj_id
                        MERGE (t:Technology {name: $tech})
                        CREATE (proj)-[:USES_TECHNOLOGY]->(t)
                        """,
                        proj_id=proj_id,
                        tech=tech
                    )
            except Exception as e:
                logger.error(f"Error creating project: {str(e)}")
                # Continue with next project

        # Log actual count created
        logger.info(f"Created {created_count} projects for CV {cv_id}")

    def _create_languages(self, session, cv_id: str, cv_data: Dict[str, Any]) -> None:
        """Create language proficiency nodes and relationships"""
        languages = cv_data.get("language_proficiency", [])

        if not languages:
            return

        for lang in languages:
            try:
                language = lang.get("language", "Unknown")
                level = lang.get("level", {})
                self_assessed = level.get("self_assessed", "Unknown")
                cefr = level.get("cefr", "Unknown")

                session.run(
                    """
                    MATCH (p:Person)-[:HAS_CV]->(cv:CV)
                    WHERE cv.id = $cv_id
                    MERGE (l:Language {name: $language})
                    CREATE (p)-[:SPEAKS {
                        self_assessed: $self_assessed,
                        cefr: $cefr
                    }]->(l)
                    """,
                    cv_id=cv_id,
                    language=language,
                    self_assessed=self_assessed,
                    cefr=cefr
                )
            except Exception as e:
                logger.error(f"Error creating language proficiency: {str(e)}")
                # Continue with next language, don't fail entire CV storage

    def _create_certifications(self, session, cv_id: str, cv_data: Dict[str, Any]) -> None:
        """Create certification nodes and relationships"""
        certifications = cv_data.get("certifications", [])

        if not certifications:
            return

        for cert in certifications:
            try:
                # Ensure certification name is not None or empty
                name = cert.get("name")
                if not name:
                    name = "Untitled Certification"

                issue_org = cert.get("issue_org")
                issue_year = cert.get("issue_year")
                certificate_link = cert.get("certificate_link")

                session.run(
                    """
                    MATCH (p:Person)-[:HAS_CV]->(cv:CV)
                    WHERE cv.id = $cv_id
                    CREATE (c:Certification {
                        name: $name,
                        issue_org: $issue_org,
                        issue_year: $issue_year,
                        certificate_link: $certificate_link
                    })
                    CREATE (p)-[:HAS_CERTIFICATION]->(c)
                    """,
                    cv_id=cv_id,
                    name=name,
                    issue_org=issue_org,
                    issue_year=issue_year,
                    certificate_link=certificate_link
                )
            except Exception as e:
                logger.error(f"Error creating certification: {str(e)}")
                # Continue with next certification, don't fail entire CV storage

    def _create_awards(self, session, cv_id: str, cv_data: Dict[str, Any]) -> None:
        """Create award nodes and relationships"""
        awards = cv_data.get("awards", [])

        if not awards:
            return

        for award in awards:
            try:
                name = award.get("name", "Unknown Award")
                award_type = award.get("award_type", "other")
                organization = award.get("organization", "Unknown")
                year = award.get("year")
                position = award.get("position")
                description = award.get("description")
                url = award.get("url")

                session.run(
                    """
                    MATCH (p:Person)-[:HAS_CV]->(cv:CV)
                    WHERE cv.id = $cv_id
                    CREATE (a:Award {
                        name: $name,
                        award_type: $award_type,
                        organization: $organization,
                        year: $year,
                        position: $position,
                        description: $description,
                        url: $url
                    })
                    CREATE (p)-[:RECEIVED_AWARD]->(a)
                    """,
                    cv_id=cv_id,
                    name=name,
                    award_type=award_type,
                    organization=organization,
                    year=year,
                    position=position,
                    description=description,
                    url=url
                )
            except Exception as e:
                logger.error(f"Error creating award: {str(e)}")
                # Continue with next award, don't fail entire CV storage

    def _create_scientific_contributions(self, session, cv_id: str, cv_data: Dict[str, Any]) -> None:
        """Create scientific contribution nodes and relationships"""
        contributions: list[dict] | dict = cv_data.get("scientific_contributions", [])

        # Handle both single item and list
        if not contributions:
            return

        # Convert single item to list if needed
        if not isinstance(contributions, list):
            contributions = [contributions]

        for contribution in contributions:
            try:
                title = contribution.get("title", "Unknown Contribution")
                publication_type = contribution.get("publication_type", "other")
                year = contribution.get("year")
                venue = contribution.get("venue")
                doi = contribution.get("doi")
                url = contribution.get("url")
                description = contribution.get("description")

                session.run(
                    """
                    MATCH (p:Person)-[:HAS_CV]->(cv:CV)
                    WHERE cv.id = $cv_id
                    CREATE (sc:ScientificContribution {
                        title: $title,
                        publication_type: $publication_type,
                        year: $year,
                        venue: $venue,
                        doi: $doi,
                        url: $url,
                        description: $description
                    })
                    CREATE (p)-[:AUTHORED]->(sc)
                    """,
                    cv_id=cv_id,
                    title=title,
                    publication_type=publication_type,
                    year=year,
                    venue=venue,
                    doi=doi,
                    url=url,
                    description=description
                )
            except Exception as e:
                logger.error(f"Error creating scientific contribution: {str(e)}")
                # Continue with next contribution, don't fail entire CV storage

    def get_cv_details(self, cv_ids: List[str]) -> Dict[str, Dict[str, Any]]:
        """Get basic details for a list of CVs

        Args:
            cv_ids: List of CV IDs to retrieve

        Returns:
            Dictionary mapping CV IDs to CV details
        """
        result = {}

        try:
            with self.driver.session() as session:
                records = session.run(
                    """
                    MATCH (p:Person)-[:HAS_CV]->(cv:CV)
                    WHERE cv.id IN $cv_ids
                    OPTIONAL MATCH (p)-[:HAD_EXPERIENCE]->(exp)-[:AT_COMPANY]->(c:Company)
                    WITH p, cv, COLLECT(DISTINCT {company: c.name, position: exp.position}) AS experiences
                    OPTIONAL MATCH (p)-[:HAS_SKILL]->(s:Skill)
                    WITH p, cv, experiences, COLLECT(DISTINCT s.name) AS skills
                    RETURN 
                        cv.id AS cv_id,
                        p.name AS name,
                        p.email AS email,
                        p.city AS city,
                        p.country AS country,
                        cv.summary AS summary,
                        cv.desired_role AS desired_role,
                        experiences,
                        skills
                    """,
                    cv_ids=cv_ids
                )

                for record in records:
                    cv_id = record["cv_id"]
                    result[cv_id] = {
                        "name": record["name"],
                        "email": record["email"],
                        "city": record["city"],
                        "country": record["country"],
                        "summary": record["summary"],
                        "desired_role": record["desired_role"],
                        "experiences": record["experiences"],
                        "skills": record["skills"]
                    }

            return result
        except Exception as e:
            logger.error(f"Error retrieving CV details: {str(e)}")
            raise GraphDBError(f"Failed to retrieve CV details: {str(e)}")

    def find_existing_person(self, email: str, name: str = None, phone: str = None) -> Optional[Dict[str, Any]]:
        """Find an existing person and their CV based on contact information

        Args:
            email: Person's email (primary identifier)
            name: Person's name (optional, for additional matching)
            phone: Person's phone number (optional, for additional matching)

        Returns:
            Dictionary with person details and CV IDs if found, None otherwise
        """
        try:
            with self.driver.session() as session:
                # Start with email match (required unique field)
                query = """
                MATCH (p:Person {email: $email})
                OPTIONAL MATCH (p)-[:HAS_CV]->(cv:CV)
                RETURN p.email AS email, p.name AS name, p.phone AS phone,
                       COLLECT(cv.id) AS cv_ids
                """

                result = session.run(query, email=email)
                record = result.single()

                if record and record["email"]:
                    return {
                        "email": record["email"],
                        "name": record["name"],
                        "phone": record["phone"],
                        "cv_ids": record["cv_ids"]
                    }

                return None
        except Exception as e:
            logger.error(f"Error finding existing person: {str(e)}")
            return None

    def delete_cv(self, cv_id: str) -> bool:
        """Delete a CV and all related nodes

        Args:
            cv_id: CV ID to delete

        Returns:
            True if successful, False otherwise
        """
        try:
            with self.driver.session() as session:
                # Use a cascading delete approach
                session.run(
                    """
                    MATCH (cv:CV {id: $cv_id})
                    OPTIONAL MATCH (p:Person)-[:HAS_CV]->(cv)
                    OPTIONAL MATCH (p)-[r1:HAD_EXPERIENCE]->(exp)
                    OPTIONAL MATCH (exp)-[r2:AT_COMPANY]->(c:Company)
                    OPTIONAL MATCH (exp)-[r3:HAS_KEY_POINT]->(kp:KeyPoint)
                    OPTIONAL MATCH (exp)-[r4:USES_TECHNOLOGY]->(t:Technology)
                    OPTIONAL MATCH (p)-[r5:COMPLETED_PROJECT]->(proj:Project)
                    OPTIONAL MATCH (proj)-[r6:HAS_KEY_POINT]->(pkp:KeyPoint)
                    OPTIONAL MATCH (proj)-[r7:USES_TECHNOLOGY]->(pt:Technology)
                    OPTIONAL MATCH (p)-[r8:EDUCATED_AT]->(e:Education)
                    OPTIONAL MATCH (e)-[r9:AT_INSTITUTION]->(i:Institution)
                    OPTIONAL MATCH (p)-[r10:SPEAKS]->(l:Language)
                    OPTIONAL MATCH (p)-[r11:HAS_CERTIFICATION]->(cert:Certification)

                    DETACH DELETE exp, kp, proj, pkp, e, cert

                    WITH cv, p
                    DETACH DELETE cv

                    // Keep person node but remove the CV relationship
                    """,
                    cv_id=cv_id
                )

                logger.info(f"Deleted CV {cv_id} and related nodes")
                return True

        except Exception as e:
            logger.error(f"Error deleting CV {cv_id}: {str(e)}")
            raise GraphDBError(f"Failed to delete CV: {str(e)}")
