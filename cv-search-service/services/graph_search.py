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
                match_clauses = ["MATCH (p:Person)-[:HAS_CV]->(cv:CV)"]
                where_clauses = []
                params = {}

                # Skills filter
                if skills and len(skills) > 0:
                    match_clauses.append("MATCH (p)-[:HAS_SKILL]->(s:Skill)")
                    where_clauses.append("s.name IN $skills")
                    params["skills"] = skills

                # Technologies filter
                if technologies and len(technologies) > 0:
                    match_clauses.append("""
                    MATCH (p)-[:HAD_EXPERIENCE|COMPLETED_PROJECT]->(entity)
                    MATCH (entity)-[:USES_TECHNOLOGY]->(t:Technology)
                    """)
                    where_clauses.append("t.name IN $technologies")
                    params["technologies"] = technologies

                # Role filter - fixed to avoid the problematic COLLECT() in WHERE clause
                if role:
                    match_clauses.append("""
                    OPTIONAL MATCH (p)-[:HAD_EXPERIENCE]->(exp_role:Experience)
                    """)
                    where_clauses.append("""
                    (cv.desired_role CONTAINS $role OR 
                     EXISTS {
                        MATCH (p)-[:HAD_EXPERIENCE]->(e)
                        WHERE toLower(e.position) CONTAINS toLower($role)
                     })
                    """)
                    params["role"] = role

                # Company filter
                if company:
                    match_clauses.append("""
                    MATCH (p)-[:HAD_EXPERIENCE]->(exp:Experience)-[:AT_COMPANY]->(c:Company)
                    """)
                    where_clauses.append("c.name CONTAINS $company")
                    params["company"] = company

                # Location filter - fixed to avoid incorrect ANY() with arrays
                if location:
                    location_where = """
                    (p.city CONTAINS $location OR 
                     p.country CONTAINS $location OR 
                     EXISTS {
                        MATCH (p)-[:HAD_EXPERIENCE]->(e)
                        WHERE (e.city IS NOT NULL AND e.city CONTAINS $location) OR
                              (e.country IS NOT NULL AND e.country CONTAINS $location)
                     })
                    """
                    where_clauses.append(location_where)
                    params["location"] = location

                # Years of experience filter
                if years_experience is not None and years_experience > 0:
                    match_clauses.append("""
                    MATCH (p)-[:HAD_EXPERIENCE]->(exp_years:Experience)
                    """)
                    where_clauses.append("""
                    WITH p, cv, sum(exp_years.duration_months) / 12.0 AS total_years
                    WHERE total_years >= $years_experience
                    """)
                    params["years_experience"] = years_experience

                # Combine query parts
                query = "\n".join(match_clauses)
                if where_clauses:
                    query += "\nWHERE " + " AND ".join(where_clauses)

                # Add return statement with complete CV details
                query += """
                WITH DISTINCT p, cv

                // Get work experiences with companies
                OPTIONAL MATCH (p)-[:HAD_EXPERIENCE]->(exp)-[:AT_COMPANY]->(c:Company)
                WITH p, cv, 
                     COLLECT(DISTINCT {
                        company: c.name, 
                        position: exp.position,
                        duration_months: exp.duration_months,
                        start_date: exp.start_date,
                        end_date: exp.end_date,
                        employment_type: exp.employment_type,
                        work_mode: exp.work_mode
                     }) AS experiences

                // Get skills
                OPTIONAL MATCH (p)-[:HAS_SKILL]->(s:Skill)
                WITH p, cv, experiences, COLLECT(DISTINCT s.name) AS skills

                // Get education
                OPTIONAL MATCH (p)-[:EDUCATED_AT]->(e:Education)-[:AT_INSTITUTION]->(i:Institution)
                WITH p, cv, experiences, skills, 
                     COLLECT(DISTINCT {
                        institution: i.name,
                        qualification: e.qualification,
                        field: e.field,
                        start: e.start,
                        end: e.end,
                        status: e.status
                     }) AS education

                // Get location info
                OPTIONAL MATCH (p)-[:HAD_EXPERIENCE]->(exp)
                WITH p, cv, experiences, skills, education,
                     COLLECT(DISTINCT {
                        city: exp.city,
                        country: exp.country
                     }) AS job_locations

                // Calculate experience stats
                WITH p, cv, experiences, skills, education, job_locations,
                     CASE WHEN experiences IS NULL OR size(experiences) = 0 THEN 0
                          ELSE REDUCE(s = 0, exp IN experiences | s + COALESCE(exp.duration_months, 0))
                     END / 12.0 AS years_experience

                // Return the complete result
                RETURN 
                    cv.id AS cv_id,
                    p.name AS name,
                    p.email AS email,
                    cv.summary AS summary,
                    cv.desired_role AS desired_role,
                    p.city AS city,
                    p.country AS country,
                    skills,
                    experiences,
                    education,
                    job_locations,
                    years_experience,
                    1.0 AS score
                ORDER BY years_experience DESC
                LIMIT $limit
                """
                params["limit"] = limit

                # Execute query
                records = session.run(query, params)

                # Process results - keep duration_months as integer
                results = []
                for record in records:
                    # Format the data for the response
                    result = {
                        "cv_id": record["cv_id"],
                        "person_name": record["name"],
                        "email": record["email"],
                        "summary": record.get("summary"),
                        "desired_role": record.get("desired_role"),
                        "location": {
                            "city": record.get("city"),
                            "country": record.get("country")
                        },
                        "experiences": record["experiences"],  # Keep original format with integer duration_months
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
                MATCH (s:Skill)<-[:HAS_SKILL]-(p:Person)
                WITH s.name AS skill, count(DISTINCT p) AS count
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
                MATCH (t:Technology)<-[:USES_TECHNOLOGY]-()<-[:HAD_EXPERIENCE|COMPLETED_PROJECT]-(p:Person)
                WITH t.name AS technology, count(DISTINCT p) AS count
                WHERE count > 0
                RETURN technology, count
                ORDER BY count DESC, technology
                LIMIT 100
                """)

                filter_options["technologies"] = [
                    {"value": record["technology"], "count": record["count"]}
                    for record in tech_result
                ]

                # Get roles with counts (from desired_role and experience positions)
                roles_result = session.run("""
                // Get roles from CV desired_roles
                MATCH (p:Person)-[:HAS_CV]->(cv:CV)
                WHERE cv.desired_role IS NOT NULL
                WITH cv.desired_role AS role, count(DISTINCT p) AS count

                // Combine with roles from experiences
                UNION

                MATCH (p:Person)-[:HAD_EXPERIENCE]->(exp:Experience)
                WHERE exp.position IS NOT NULL
                WITH exp.position AS role, count(DISTINCT p) AS count

                // Return final results
                WITH role, count
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
                MATCH (c:Company)<-[:AT_COMPANY]-(:Experience)<-[:HAD_EXPERIENCE]-(p:Person)
                WITH c.name AS company, count(DISTINCT p) AS count
                WHERE count > 0 AND company <> ""
                RETURN company, count
                ORDER BY count DESC, company
                LIMIT 100
                """)

                filter_options["companies"] = [
                    {"value": record["company"], "count": record["count"]}
                    for record in companies_result
                ]

                # Get locations with counts (cities and countries)
                locations_result = session.run("""
                // Get locations from Person nodes
                MATCH (p:Person)
                WHERE p.city IS NOT NULL OR p.country IS NOT NULL
                WITH COLLECT(DISTINCT {location: p.city, count: count(p)}) + 
                     COLLECT(DISTINCT {location: p.country, count: count(p)}) AS all_locations

                // Filter and sort
                UNWIND all_locations AS loc_data
                WITH loc_data.location AS location, loc_data.count AS count
                WHERE location IS NOT NULL AND location <> ""

                // Combine duplicates
                WITH location, sum(count) AS total_count
                RETURN location, total_count AS count
                ORDER BY count DESC, location
                LIMIT 100
                """)

                filter_options["locations"] = [
                    {"value": record["location"], "count": record["count"]}
                    for record in locations_result
                ]

                # Get experience ranges with counts
                exp_ranges_result = session.run("""
                MATCH (p:Person)-[:HAD_EXPERIENCE]->(exp:Experience)
                WITH p, sum(exp.duration_months) / 12.0 AS years

                // Create experience ranges
                WITH p, years,
                     CASE 
                        WHEN years < 1 THEN "< 1 year"
                        WHEN years >= 1 AND years < 3 THEN "1-3 years"
                        WHEN years >= 3 AND years < 5 THEN "3-5 years"
                        WHEN years >= 5 AND years < 10 THEN "5-10 years"
                        ELSE "10+ years"
                     END AS exp_range,

                     // Also create actual year value for filtering
                     CASE 
                        WHEN years < 1 THEN 0
                        WHEN years >= 1 AND years < 3 THEN 1
                        WHEN years >= 3 AND years < 5 THEN 3
                        WHEN years >= 5 AND years < 10 THEN 5
                        ELSE 10
                     END AS year_value

                // Count people in each range
                WITH exp_range, year_value, count(p) AS count
                RETURN exp_range AS value, year_value AS numeric_value, count
                ORDER BY year_value
                """)

                filter_options["experience_ranges"] = [
                    {"value": record["value"], "numeric_value": record["numeric_value"], "count": record["count"]}
                    for record in exp_ranges_result
                ]

            return filter_options

        except Exception as e:
            logger.error(f"Error retrieving filter options: {str(e)}")
            raise DatabaseError(f"Failed to retrieve filter options: {str(e)}")
