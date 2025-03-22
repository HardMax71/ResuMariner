import logging
from typing import List, Dict, Any, Optional

from config import settings
from neo4j import GraphDatabase, exceptions
from utils.errors import DatabaseError

logger = logging.getLogger(__name__)


class GraphSearchService:
    """Service for graph-based search in Neo4j"""

    def __init__(self):
        """Initialize the graph search service"""
        try:
            self.driver = GraphDatabase.driver(
                settings.NEO4J_URI,
                auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD)
            )
            logger.info(f"Connected to Neo4j at {settings.NEO4J_URI}")
        except exceptions.ServiceUnavailable as e:
            logger.error(f"Failed to connect to Neo4j: {str(e)}")
            raise DatabaseError(f"Graph database connection failed: {str(e)}")

    def search(self,
               skills: Optional[List[str]] = None,
               technologies: Optional[List[str]] = None,
               role: Optional[str] = None,
               company: Optional[str] = None,
               location: Optional[str] = None,
               years_experience: Optional[int] = None,
               limit: int = 10) -> List[Dict[str, Any]]:
        """Search for CVs using graph query with multiple filters

        Args:
            skills: List of skills to search for
            technologies: List of technologies to search for
            role: Desired role to search for
            company: Company to search for
            location: Location to search for (city or country)
            years_experience: Minimum years of experience required
            limit: Maximum number of results to return

        Returns:
            List of matching CV data
        """
        try:
            with self.driver.session() as session:
                # Build dynamic query based on provided filters
                match_clauses = ["MATCH (cv:CVNode)"]
                where_clauses = []
                params: Dict[str, Any] = {}

                # Skills filter
                if skills and len(skills) > 0:
                    match_clauses.append("MATCH (cv)-[:HAS_SKILL]->(s:SkillNode)")
                    where_clauses.append("s.name IN $skills")
                    params["skills"] = skills

                # Technologies filter
                if technologies and len(technologies) > 0:
                    match_clauses.append("""
                    MATCH (cv)-[:HAS_EMPLOYMENT_HISTORY|HAS_PROJECT]->(entity)
                    MATCH (entity)-[:USES_TECHNOLOGY]->(t:TechnologyNode)
                    """)
                    where_clauses.append("t.name IN $technologies")
                    params["technologies"] = technologies

                # Role filter
                if role:
                    match_clauses.append("""
                    MATCH (cv)-[:HAS_PROFESSIONAL_PROFILE]->(pp:ProfessionalProfileNode)
                    -[:HAS_PREFERENCES]->(pref:PreferencesNode)
                    """)
                    where_clauses.append("pref.role CONTAINS $role")
                    params["role"] = role

                # Company filter
                if company:
                    match_clauses.append("""
                    MATCH (cv)-[:HAS_EMPLOYMENT_HISTORY]->(job:EmploymentHistoryItemNode)
                    -[:WORKED_AT]->(c:CompanyInfoNode)
                    """)
                    where_clauses.append("c.name CONTAINS $company")
                    params["company"] = company

                # Location filter
                if location:
                    match_clauses.append("""
                    MATCH (cv)-[:HAS_PERSONAL_INFO]->(p:PersonalInfoNode)
                    -[:HAS_DEMOGRAPHICS]->(d:DemographicsNode)
                    -[:HAS_LOCATION]->(loc:LocationNode)
                    """)
                    location_where = """
                    (loc.city CONTAINS $location OR 
                     loc.country CONTAINS $location)
                    """
                    where_clauses.append(location_where)
                    params["location"] = location

                # Combine query parts
                query = "\n".join(match_clauses)
                if where_clauses:
                    query += "\nWHERE " + " AND ".join(where_clauses)

                # Add return statement with complete CV details
                query += """
                WITH DISTINCT cv

                // Get personal info
                MATCH (cv)-[:HAS_PERSONAL_INFO]->(p:PersonalInfoNode)
                MATCH (p)-[:HAS_CONTACT]->(contact:ContactNode)

                // Get skills
                OPTIONAL MATCH (cv)-[:HAS_SKILL]->(s:SkillNode)
                WITH cv, p, contact, COLLECT(DISTINCT s.name) AS skills

                // Get employment history
                OPTIONAL MATCH (cv)-[:HAS_EMPLOYMENT_HISTORY]->(job:EmploymentHistoryItemNode)
                OPTIONAL MATCH (job)-[:WORKED_AT]->(comp:CompanyInfoNode)
                OPTIONAL MATCH (job)-[:HAS_DURATION]->(dur:EmploymentDurationNode)

                WITH cv, p, contact, skills, 
                     COLLECT(DISTINCT {
                        company: comp.name, 
                        position: job.position,
                        duration_months: dur.duration_months
                     }) AS experiences

                // Get education
                OPTIONAL MATCH (cv)-[:HAS_EDUCATION]->(edu:EducationItemNode)
                OPTIONAL MATCH (edu)-[:ATTENDED]->(inst:InstitutionInfoNode)

                WITH cv, p, contact, skills, experiences,
                     COLLECT(DISTINCT {
                        institution: inst.name,
                        qualification: edu.qualification,
                        field: edu.field,
                        start: edu.start,
                        end: edu.end,
                        status: edu.status
                     }) AS education

                // Calculate experience stats
                WITH cv, p, contact, skills, experiences, education,
                     CASE WHEN experiences IS NULL OR size(experiences) = 0 THEN 0
                          ELSE REDUCE(s = 0, exp IN experiences | s + COALESCE(exp.duration_months, 0))
                     END / 12.0 AS years_experience

                // Return the complete result
                RETURN 
                    cv.uid AS cv_id,
                    p.name AS name,
                    contact.email AS email,
                    skills,
                    experiences,
                    education,
                    years_experience,
                    1.0 AS score
                ORDER BY years_experience DESC
                LIMIT $limit
                """
                params["limit"] = limit

                # Execute query
                records = session.run(query, params)

                # Process results
                results = []
                for record in records:
                    # Format the data for the response
                    result = {
                        "cv_id": record["cv_id"],
                        "person_name": record["name"],
                        "email": record["email"],
                        "experiences": record["experiences"],
                        "skills": record["skills"],
                        "education": record["education"],
                        "years_experience": round(record.get("years_experience", 0), 1),
                        "score": record["score"],
                        "matches": []  # No text matches for graph search
                    }
                    results.append(result)

                logger.info(f"Graph search returned {len(results)} results")
                return results

        except Exception as e:
            logger.error(f"Error in graph search: {str(e)}")
            raise DatabaseError(f"Graph search failed: {str(e)}")

    def get_filter_options(self) -> Dict[str, List[Dict[str, Any]]]:
        """Get available filter options with counts for all filter categories"""
        try:
            filter_options = {}

            with self.driver.session() as session:
                # Get skills with counts
                skills_result = session.run("""
                MATCH (s:SkillNode)<-[:HAS_SKILL]-(cv:CVNode)
                WITH s.name AS skill, count(DISTINCT cv) AS count
                WHERE count > 0
                RETURN skill, count
                ORDER BY count DESC, skill
                LIMIT 100
                """)

                filter_options["skills"] = [
                    {"value": record["skill"], "count": record["count"]}
                    for record in skills_result
                ]

                # Get technologies with counts
                tech_result = session.run("""
                MATCH (t:TechnologyNode)<-[:USES_TECHNOLOGY]-()<-[:HAS_EMPLOYMENT_HISTORY|HAS_PROJECT]-(cv:CVNode)
                WITH t.name AS technology, count(DISTINCT cv) AS count
                WHERE count > 0
                RETURN technology, count
                ORDER BY count DESC, technology
                LIMIT 100
                """)

                filter_options["technologies"] = [
                    {"value": record["technology"], "count": record["count"]}
                    for record in tech_result
                ]

                # Get roles with counts
                roles_result = session.run("""
                MATCH (cv:CVNode)-[:HAS_PROFESSIONAL_PROFILE]->(pp:ProfessionalProfileNode)
                -[:HAS_PREFERENCES]->(pref:PreferencesNode)
                WHERE pref.role IS NOT NULL
                WITH pref.role AS role, count(DISTINCT cv) AS count
                WHERE count > 0 AND role <> ""
                RETURN role, count
                ORDER BY count DESC, role
                LIMIT 50
                """)

                filter_options["roles"] = [
                    {"value": record["role"], "count": record["count"]}
                    for record in roles_result
                ]

                # Get companies with counts
                companies_result = session.run("""
                MATCH (c:CompanyInfoNode)<-[:WORKED_AT]-(job:EmploymentHistoryItemNode)
                <-[:HAS_EMPLOYMENT_HISTORY]-(cv:CVNode)
                WITH c.name AS company, count(DISTINCT cv) AS count
                WHERE count > 0 AND company <> ""
                RETURN company, count
                ORDER BY count DESC, company
                LIMIT 100
                """)

                filter_options["companies"] = [
                    {"value": record["company"], "count": record["count"]}
                    for record in companies_result
                ]

                # Get locations with counts
                locations_result = session.run("""
                MATCH (cv:CVNode)-[:HAS_PERSONAL_INFO]->(:PersonalInfoNode)
                -[:HAS_DEMOGRAPHICS]->(:DemographicsNode)-[:HAS_LOCATION]->(loc:LocationNode)
                WITH COLLECT(DISTINCT {location: loc.city, count: count(cv)}) + 
                     COLLECT(DISTINCT {location: loc.country, count: count(cv)}) AS all_locations
                UNWIND all_locations AS loc_data
                WITH loc_data.location AS location, loc_data.count AS count
                WHERE location IS NOT NULL AND location <> ""
                RETURN location, count
                ORDER BY count DESC, location
                LIMIT 100
                """)

                filter_options["locations"] = [
                    {"value": record["location"], "count": record["count"]}
                    for record in locations_result
                ]

                return filter_options

        except Exception as e:
            logger.error(f"Error retrieving filter options: {str(e)}")
            raise DatabaseError(f"Failed to retrieve filter options: {str(e)}")
