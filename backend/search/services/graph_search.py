import logging
from dataclasses import asdict

from django.conf import settings
from neo4j import AsyncGraphDatabase

from core.domain import FilterOption, FilterOptionsResult, ResumeSearchResult, SearchFilters

logger = logging.getLogger(__name__)

"""
TODO: naming?

For XXQuerySerializer, we have to_internal_value() overridden: it return instance of well-typed obj instead of dict[whatever].
Problem is, it is not always clear, when which serializer returns well-typed instance of obj instead of dict (and vice versa).

Maybe:
- naming?
- some other hints without trashing actual serializers' names?
"""


class GraphSearchService:
    def __init__(self):
        self.driver = AsyncGraphDatabase.driver(
            settings.NEO4J_URI,
            auth=(settings.NEO4J_USERNAME, settings.NEO4J_PASSWORD),
            max_connection_lifetime=3600,
            max_connection_pool_size=50,
            connection_acquisition_timeout=60,
        )
        logger.info("Connected to Neo4j at %s", settings.NEO4J_URI)

    async def search(
        self,
        filters: SearchFilters,
        limit: int = 10,
    ) -> list[ResumeSearchResult]:
        query = """
        MATCH (resume:ResumeNode)
        WHERE
            ($skills IS NULL OR $skills = [] OR EXISTS {
                MATCH (resume)-[:HAS_SKILL]->(s:SkillNode)
                WHERE s.name IN $skills
            } OR EXISTS {
                MATCH (resume)-[:HAS_EMPLOYMENT_HISTORY|HAS_PROJECT]->(entity)-[:HAS_SKILL]->(s:SkillNode)
                WHERE s.name IN $skills
            })
            AND ($role IS NULL OR EXISTS {
                MATCH (resume)-[:HAS_PROFESSIONAL_PROFILE]->(pp:ProfessionalProfileNode)
                      -[:HAS_PREFERENCES]->(pref:PreferencesNode)
                WHERE pref.role CONTAINS $role
            })
            AND ($company IS NULL OR EXISTS {
                MATCH (resume)-[:HAS_EMPLOYMENT_HISTORY]->(job:EmploymentHistoryItemNode)
                      -[:WORKED_AT]->(c:CompanyInfoNode)
                WHERE c.name CONTAINS $company
            })
            AND ($location IS NULL OR EXISTS {
                MATCH (resume)-[:HAS_PERSONAL_INFO]->(:PersonalInfoNode)
                      -[:HAS_DEMOGRAPHICS]->(:DemographicsNode)
                      -[:HAS_LOCATION]->(loc:LocationNode)
                WHERE loc.city CONTAINS $location OR loc.country CONTAINS $location
            })
            AND ($education_level IS NULL OR EXISTS {
                MATCH (resume)-[:HAS_EDUCATION]->(edu:EducationItemNode)
                WHERE edu.qualification CONTAINS $education_level
            })
            AND ($education_status IS NULL OR EXISTS {
                MATCH (resume)-[:HAS_EDUCATION]->(edu:EducationItemNode)
                WHERE edu.status = $education_status
            })

        WITH resume
        MATCH (resume)-[:HAS_PERSONAL_INFO]->(p:PersonalInfoNode)-[:HAS_CONTACT]->(contact:ContactNode)
        OPTIONAL MATCH (resume)-[:HAS_PROFESSIONAL_PROFILE]->(prof:ProfessionalProfileNode)
        WITH resume, p.name AS name, contact.email AS email, prof.summary AS summary

        // Get skills for this specific resume
        OPTIONAL MATCH (resume)-[:HAS_SKILL]->(s:SkillNode)
        WITH resume, name, email, summary, collect(DISTINCT s.name) AS skills

        // Get employment history for this specific resume (sorted newest first)
        OPTIONAL MATCH (resume)-[:HAS_EMPLOYMENT_HISTORY]->(job:EmploymentHistoryItemNode)
        OPTIONAL MATCH (job)-[:WORKED_AT]->(c:CompanyInfoNode)
        OPTIONAL MATCH (job)-[:HAS_DURATION]->(d:EmploymentDurationNode)
        OPTIONAL MATCH (job)-[:HAS_KEY_POINT]->(kp:KeyPointInfoNode)
        WITH resume, name, email, summary, skills, job, c.name AS company_name, d,
             collect(DISTINCT kp.text) AS job_key_points
        ORDER BY d.start DESC
        WITH resume, name, email, summary, skills,
             collect(job {
                .*,
                company: company_name,
                duration_months: d.duration_months,
                start: d.start,
                end: d.end,
                key_points: CASE WHEN size(job_key_points) > 0 THEN job_key_points ELSE [] END
             }) AS experiences

        // Get education for this specific resume (sorted newest first)
        OPTIONAL MATCH (resume)-[:HAS_EDUCATION]->(edu:EducationItemNode)
        OPTIONAL MATCH (edu)-[:ATTENDED]->(inst:InstitutionInfoNode)
        ORDER BY edu.start DESC
        WITH resume, name, email, summary, skills, experiences,
             collect(edu {.*, institution: inst.name}) AS education

        // Calculate years of experience
        WITH resume, name, email, summary, skills, experiences, education,
             toInteger(ROUND(REDUCE(total = 0, exp IN experiences | total + COALESCE(exp.duration_months, 0)) / 12.0)) AS years_experience

        // Get location and preferences
        OPTIONAL MATCH (resume)-[:HAS_PERSONAL_INFO]->(:PersonalInfoNode)
                      -[:HAS_DEMOGRAPHICS]->(:DemographicsNode)
                      -[:HAS_LOCATION]->(loc:LocationNode)
        OPTIONAL MATCH (resume)-[:HAS_PROFESSIONAL_PROFILE]->(:ProfessionalProfileNode)
                      -[:HAS_PREFERENCES]->(pref:PreferencesNode)

        WITH resume, name, email, summary, skills, experiences, education, years_experience,
             loc {.*} AS location, pref.role AS desired_role,
             CASE WHEN $years_experience IS NULL THEN 1 ELSE CASE WHEN years_experience >= $years_experience THEN 1 ELSE 0 END END AS experience_match
        WHERE experience_match = 1

        RETURN resume.uid AS resume_id, name, email, summary, skills, experiences, education,
               years_experience, location, desired_role,
               (size(skills) * 0.2 + years_experience * 0.1) AS score
        ORDER BY score DESC
        LIMIT $limit
        """

        async def run_query(tx):
            result = await tx.run(query, {**asdict(filters), "limit": limit})
            return await result.data()

        async with self.driver.session() as session:
            records_data = await session.execute_read(run_query)

            results = [ResumeSearchResult(**record) for record in records_data]

            logger.info("Graph search returned %s results", len(results))
            return results

    async def get_resumes_by_ids(self, resume_ids: list[str]) -> list[ResumeSearchResult]:
        """
        Batch fetch complete resume data for given IDs.
        Returns ResumeSearchResult objects with all available fields.
        """
        if not resume_ids:
            return []

        query = """
        MATCH (resume:ResumeNode)
        WHERE resume.uid IN $resume_ids
        WITH resume
        MATCH (resume)-[:HAS_PERSONAL_INFO]->(p:PersonalInfoNode)-[:HAS_CONTACT]->(contact:ContactNode)
        OPTIONAL MATCH (resume)-[:HAS_PROFESSIONAL_PROFILE]->(prof:ProfessionalProfileNode)
        WITH resume, p.name AS name, contact.email AS email, prof.summary AS summary

        // Get skills for this specific resume
        OPTIONAL MATCH (resume)-[:HAS_SKILL]->(s:SkillNode)
        WITH resume, name, email, summary, collect(DISTINCT s.name) AS skills

        // Get employment history for this specific resume (sorted newest first)
        OPTIONAL MATCH (resume)-[:HAS_EMPLOYMENT_HISTORY]->(job:EmploymentHistoryItemNode)
        OPTIONAL MATCH (job)-[:WORKED_AT]->(c:CompanyInfoNode)
        OPTIONAL MATCH (job)-[:HAS_DURATION]->(d:EmploymentDurationNode)
        OPTIONAL MATCH (job)-[:HAS_KEY_POINT]->(kp:KeyPointInfoNode)
        WITH resume, name, email, summary, skills, job, c.name AS company_name, d,
             collect(DISTINCT kp.text) AS job_key_points
        ORDER BY d.start DESC
        WITH resume, name, email, summary, skills,
             collect(job {
                .*,
                company: company_name,
                duration_months: d.duration_months,
                start: d.start,
                end: d.end,
                key_points: CASE WHEN size(job_key_points) > 0 THEN job_key_points ELSE [] END
             }) AS experiences

        // Get education for this specific resume (sorted newest first)
        OPTIONAL MATCH (resume)-[:HAS_EDUCATION]->(edu:EducationItemNode)
        OPTIONAL MATCH (edu)-[:ATTENDED]->(inst:InstitutionInfoNode)
        ORDER BY edu.start DESC
        WITH resume, name, email, summary, skills, experiences,
             collect(edu {.*, institution: inst.name}) AS education

        // Calculate years of experience
        WITH resume, name, email, summary, skills, experiences, education,
             toInteger(ROUND(REDUCE(total = 0, exp IN experiences | total + COALESCE(exp.duration_months, 0)) / 12.0)) AS years_experience

        // Get location and preferences
        OPTIONAL MATCH (resume)-[:HAS_PERSONAL_INFO]->(:PersonalInfoNode)
                      -[:HAS_DEMOGRAPHICS]->(:DemographicsNode)
                      -[:HAS_LOCATION]->(loc:LocationNode)
        OPTIONAL MATCH (resume)-[:HAS_PROFESSIONAL_PROFILE]->(:ProfessionalProfileNode)
                      -[:HAS_PREFERENCES]->(pref:PreferencesNode)

        RETURN resume.uid AS resume_id, name, email, summary, skills, experiences, education, years_experience,
               loc {.*} AS location, pref.role AS desired_role, 1.0 AS score
        """

        async def run_query(tx):
            result = await tx.run(query, {"resume_ids": resume_ids})
            return await result.data()

        async with self.driver.session() as session:
            records_data = await session.execute_read(run_query)

            results = [ResumeSearchResult(**record) for record in records_data]

            logger.info("Fetched %s resumes by IDs", len(results))
            return results

    async def get_filter_options(self) -> FilterOptionsResult:
        query = """
        CALL {
            MATCH path = (s:SkillNode)<-[:HAS_SKILL]-(entity)
            WHERE (entity:ResumeNode) OR
                  ((entity:EmploymentHistoryItemNode) AND (entity)<-[:HAS_EMPLOYMENT_HISTORY]-(:ResumeNode)) OR
                  ((entity:ProjectNode) AND (entity)<-[:HAS_PROJECT]-(:ResumeNode))
            WITH s.name AS value,
                 CASE
                   WHEN entity:ResumeNode THEN entity
                   WHEN entity:EmploymentHistoryItemNode THEN head([(entity)<-[:HAS_EMPLOYMENT_HISTORY]-(r:ResumeNode) | r])
                   WHEN entity:ProjectNode THEN head([(entity)<-[:HAS_PROJECT]-(r:ResumeNode) | r])
                 END AS resume
            WITH value, count(DISTINCT resume) AS count
            WHERE count > 0
            ORDER BY count DESC, value ASC
            LIMIT 200
            RETURN 'skills' AS category, collect({value: value, count: count}) AS items
            UNION
            MATCH (resume:ResumeNode)-[:HAS_PROFESSIONAL_PROFILE]->(:ProfessionalProfileNode)-[:HAS_PREFERENCES]->(pref:PreferencesNode)
            WHERE pref.role IS NOT NULL AND pref.role <> ""
            WITH pref.role AS value, count(DISTINCT resume) AS count
            WHERE count > 0
            WITH value, count
            ORDER BY count DESC, value ASC
            LIMIT 50
            RETURN 'roles' AS category, collect({value: value, count: count}) AS items
            UNION
            MATCH (c:CompanyInfoNode)<-[:WORKED_AT]-(:EmploymentHistoryItemNode)<-[:HAS_EMPLOYMENT_HISTORY]-(resume:ResumeNode)
            WHERE c.name IS NOT NULL AND c.name <> ""
            WITH c.name AS value, count(DISTINCT resume) AS count
            WHERE count > 0
            WITH value, count
            ORDER BY count DESC, value ASC
            LIMIT 100
            RETURN 'companies' AS category, collect({value: value, count: count}) AS items
            UNION
            MATCH (resume:ResumeNode)-[:HAS_PERSONAL_INFO]->(:PersonalInfoNode)-[:HAS_DEMOGRAPHICS]->(:DemographicsNode)-[:HAS_LOCATION]->(loc:LocationNode)
            WITH resume, loc
            WHERE (loc.city IS NOT NULL AND loc.city <> "") OR (loc.country IS NOT NULL AND loc.country <> "")
            UNWIND [loc.city, loc.country] AS location
            WITH location, count(DISTINCT resume) AS count
            WHERE location IS NOT NULL AND location <> ""
            WITH location AS value, sum(count) AS count
            WITH value, count
            ORDER BY count DESC, value ASC
            LIMIT 100
            RETURN 'locations' AS category, collect({value: value, count: count}) AS items
            UNION
            MATCH (edu:EducationItemNode)<-[:HAS_EDUCATION]-(resume:ResumeNode)
            WHERE edu.qualification IS NOT NULL AND edu.qualification <> ""
            WITH edu.qualification AS value, resume
            WITH value, count(DISTINCT resume) AS count
            WHERE count > 0
            ORDER BY count DESC, value ASC
            RETURN 'education_levels' AS category, collect({value: value, count: count}) AS items
            UNION
            MATCH (edu:EducationItemNode)<-[:HAS_EDUCATION]-(resume:ResumeNode)
            WHERE edu.status IS NOT NULL AND edu.status <> ""
            WITH edu.status AS value, resume
            WITH value, count(DISTINCT resume) AS count
            WHERE count > 0
            ORDER BY count DESC, value ASC
            RETURN 'education_statuses' AS category, collect({value: value, count: count}) AS items
        }
        RETURN category, items
        """

        async def run_query(tx):
            result = await tx.run(query)
            return await result.data()

        async with self.driver.session() as session:
            records = await session.execute_read(run_query)

            logger.info(f"Filter query returned {len(records)} categories")
            for record in records:
                logger.info(f"Category: {record['category']}, Items: {len(record['items'])}")

            # Build kwargs dict from records
            kwargs = {
                record["category"]: [FilterOption(value=item["value"], count=item["count"]) for item in record["items"]]
                for record in records
            }

            return FilterOptionsResult(**kwargs)

    async def close(self):
        """Close the driver connection"""
        await self.driver.close()
