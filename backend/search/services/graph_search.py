import logging
from dataclasses import asdict

from django.conf import settings
from neo4j import GraphDatabase

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
        self.driver = GraphDatabase.driver(
            settings.NEO4J_URI,
            auth=(settings.NEO4J_USERNAME, settings.NEO4J_PASSWORD),
            max_connection_lifetime=3600,
            max_connection_pool_size=50,
            connection_acquisition_timeout=60,
        )
        logger.info("Connected to Neo4j at %s", settings.NEO4J_URI)

    def search(
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
            })
            AND ($technologies IS NULL OR $technologies = [] OR EXISTS {
                MATCH (resume)-[:HAS_EMPLOYMENT_HISTORY|HAS_PROJECT]->(entity)
                WHERE EXISTS {
                    MATCH (entity)-[:USES_TECHNOLOGY]->(t:TechnologyNode)
                    WHERE t.name IN $technologies
                }
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

        WITH resume
        CALL {
            WITH resume
            MATCH (resume)-[:HAS_PERSONAL_INFO]->(p:PersonalInfoNode)-[:HAS_CONTACT]->(contact:ContactNode)
            OPTIONAL MATCH (resume)-[:HAS_PROFESSIONAL_PROFILE]->(prof:ProfessionalProfileNode)
            WITH p, contact, prof, [(resume)-[:HAS_SKILL]->(s:SkillNode) | s.name] AS skills
            WITH p, contact, prof, skills,
                 [(resume)-[:HAS_EMPLOYMENT_HISTORY]->(job:EmploymentHistoryItemNode) |
                  job {
                    .*,
                    company: [(job)-[:WORKED_AT]->(c:CompanyInfoNode) | c.name][0],
                    duration_months: [(job)-[:HAS_DURATION]->(d:EmploymentDurationNode) | d.duration_months][0]
                  }
                 ] AS experiences
            WITH p, contact, prof, skills, experiences,
                 [(resume)-[:HAS_EDUCATION]->(edu:EducationItemNode) |
                  edu {
                    .*,
                    institution: [(edu)-[:ATTENDED]->(inst:InstitutionInfoNode) | inst.name][0]
                  }
                 ] AS education
            OPTIONAL MATCH (resume)-[:HAS_PERSONAL_INFO]->(:PersonalInfoNode)
                          -[:HAS_DEMOGRAPHICS]->(:DemographicsNode)
                          -[:HAS_LOCATION]->(loc:LocationNode)
            OPTIONAL MATCH (resume)-[:HAS_PROFESSIONAL_PROFILE]->(:ProfessionalProfileNode)
                          -[:HAS_PREFERENCES]->(pref:PreferencesNode)
            WITH p, contact, prof, skills, experiences, education,
                 toInteger(ROUND(REDUCE(total = 0, exp IN experiences | total + COALESCE(exp.duration_months, 0)) / 12.0)) AS years_experience,
                 loc {.*} AS location,
                 pref.role AS desired_role
            RETURN p.name AS name, contact.email AS email, prof.summary AS summary, skills, experiences, education, years_experience, location, desired_role
        }

        WITH resume, name, email, summary, skills, experiences, education, years_experience, location, desired_role,
             CASE WHEN $years_experience IS NULL THEN 1 ELSE CASE WHEN years_experience >= $years_experience THEN 1 ELSE 0 END END AS experience_match
        WHERE experience_match = 1

        RETURN resume.uid AS resume_id, name, email, summary, skills, experiences, education,
               years_experience, location, desired_role,
               (size(skills) * 0.2 + years_experience * 0.1) AS score
        ORDER BY score DESC
        LIMIT $limit
        """

        with self.driver.session() as session:
            result = session.run(query, {**asdict(filters), "limit": limit})
            records_data = result.data()

            results = [ResumeSearchResult(**record) for record in records_data]

            logger.info("Graph search returned %s results", len(results))
            return results

    def get_resumes_by_ids(self, resume_ids: list[str]) -> list[ResumeSearchResult]:
        """
        Batch fetch complete resume data for given IDs.
        Returns ResumeSearchResult objects with all available fields.
        """
        if not resume_ids:
            return []

        query = """
        MATCH (resume:ResumeNode)
        WHERE resume.uid IN $resume_ids
        CALL {
            WITH resume
            MATCH (resume)-[:HAS_PERSONAL_INFO]->(p:PersonalInfoNode)-[:HAS_CONTACT]->(contact:ContactNode)
            OPTIONAL MATCH (resume)-[:HAS_PROFESSIONAL_PROFILE]->(prof:ProfessionalProfileNode)
            WITH p, contact, prof, [(resume)-[:HAS_SKILL]->(s:SkillNode) | s.name] AS skills
            WITH p, contact, prof, skills,
                 [(resume)-[:HAS_EMPLOYMENT_HISTORY]->(job:EmploymentHistoryItemNode) |
                  job {
                    .*,
                    company: [(job)-[:WORKED_AT]->(c:CompanyInfoNode) | c.name][0],
                    duration_months: [(job)-[:HAS_DURATION]->(d:EmploymentDurationNode) | d.duration_months][0]
                  }
                 ] AS experiences
            WITH p, contact, prof, skills, experiences,
                 [(resume)-[:HAS_EDUCATION]->(edu:EducationItemNode) |
                  edu {
                    .*,
                    institution: [(edu)-[:ATTENDED]->(inst:InstitutionInfoNode) | inst.name][0]
                  }
                 ] AS education,
                 toInteger(ROUND(REDUCE(total = 0, exp IN experiences | total + COALESCE(exp.duration_months, 0)) / 12.0)) AS years_experience
            OPTIONAL MATCH (resume)-[:HAS_PERSONAL_INFO]->(:PersonalInfoNode)
                          -[:HAS_DEMOGRAPHICS]->(:DemographicsNode)
                          -[:HAS_LOCATION]->(loc:LocationNode)
            OPTIONAL MATCH (resume)-[:HAS_PROFESSIONAL_PROFILE]->(:ProfessionalProfileNode)
                          -[:HAS_PREFERENCES]->(pref:PreferencesNode)
            RETURN p.name AS name, contact.email AS email, prof.summary AS summary, skills, experiences, education, years_experience,
                   loc {.*} AS location, pref.role AS desired_role
        }
        RETURN resume.uid AS resume_id, name, email, summary, skills, experiences, education, years_experience, location, desired_role,
               1.0 AS score
        """

        with self.driver.session() as session:
            result = session.run(query, {"resume_ids": resume_ids})
            records_data = result.data()

            results = [ResumeSearchResult(**record) for record in records_data]

            logger.info("Fetched %s resumes by IDs", len(results))
            return results

    def get_filter_options(self) -> FilterOptionsResult:
        query = """
        CALL {
            MATCH (s:SkillNode)<-[:HAS_SKILL]-(resume:ResumeNode)
            WITH s.name AS value, count(DISTINCT resume) AS count
            WHERE count > 0
            WITH value, count
            ORDER BY count DESC, value ASC
            LIMIT 100
            RETURN 'skills' AS category, collect({value: value, count: count}) AS items
            UNION
            MATCH (t:TechnologyNode)<-[:USES_TECHNOLOGY]-()<-[:HAS_EMPLOYMENT_HISTORY|HAS_PROJECT]-(resume:ResumeNode)
            WITH t.name AS value, count(DISTINCT resume) AS count
            WHERE count > 0
            WITH value, count
            ORDER BY count DESC, value ASC
            LIMIT 100
            RETURN 'technologies' AS category, collect({value: value, count: count}) AS items
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
        }
        RETURN category, items
        """

        with self.driver.session() as session:
            result = session.run(query)
            records = result.data()

            # Build kwargs dict from records
            kwargs = {
                record["category"]: [FilterOption(value=item["value"], count=item["count"]) for item in record["items"]]
                for record in records
            }

            return FilterOptionsResult(**kwargs)
