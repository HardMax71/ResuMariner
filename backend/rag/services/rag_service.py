import hashlib
import json
import logging
import time

from django.conf import settings
from django.core.cache import cache
from pydantic_ai.usage import RunUsage

from core.domain import Resume
from core.domain.rag import (
    CandidateComparison,
    InterviewQuestionSet,
    JobMatchExplanation,
    SeniorityLevel,
)
from core.metrics import (
    RAG_CACHE_HIT_COUNT,
    RAG_CACHE_MISS_COUNT,
    RAG_GENERATION_COUNT,
    RAG_GENERATION_DURATION,
    RAG_TOKEN_USAGE,
)
from core.services.graph_db_service import GraphDBService
from core.services.vector_db_service import VectorDBService
from processor.services.llm_service import LLMService

logger = logging.getLogger(__name__)


class RAGService:
    def __init__(self, graph_db: GraphDBService, vector_db: VectorDBService) -> None:
        self.graph_db = graph_db
        self.vector_db = vector_db

    async def explain_match(self, resume_uid: str, job_description: str) -> JobMatchExplanation:
        start_time = time.time()
        feature = "explain_match"

        cache_key = self._make_cache_key(feature, uid=resume_uid, job_desc=job_description)
        cached = cache.get(cache_key)
        if cached:
            RAG_CACHE_HIT_COUNT.labels(feature=feature).inc()
            logger.info("RAG cache hit for %s", feature)
            return JobMatchExplanation.model_validate(cached)

        RAG_CACHE_MISS_COUNT.labels(feature=feature).inc()

        resume = await self.graph_db.get_resume(resume_uid)
        if not resume:
            raise ValueError(f"Resume {resume_uid} not found")

        context = self._assemble_match_context(resume, job_description)

        llm = LLMService(
            system_prompt=self._get_match_explanation_system_prompt(), output_type=JobMatchExplanation, mode="text"
        )

        result = await llm.run(context, temperature=0.3)
        self._track_usage(feature, result.usage())

        duration = time.time() - start_time
        RAG_GENERATION_COUNT.labels(feature=feature, status="success").inc()
        RAG_GENERATION_DURATION.labels(feature=feature).observe(duration)

        cache.set(cache_key, result.output.model_dump(), timeout=settings.RAG_CACHE_EXPLAIN_MATCH_TTL)

        logger.info("Generated match explanation for resume %s in %.2fs", resume_uid, duration)

        return result.output

    async def compare_candidates(
        self, candidate_uids: list[str], criteria: list[str] | None = None, job_context: str | None = None
    ) -> CandidateComparison:
        if len(candidate_uids) < 2:
            raise ValueError("Need at least 2 candidates for comparison")
        if len(candidate_uids) > 5:
            raise ValueError("Maximum 5 candidates for comparison")

        start_time = time.time()
        feature = "compare_candidates"

        cache_key = self._make_cache_key(
            feature, uids=sorted(candidate_uids), criteria=criteria, job_context=job_context
        )
        cached = cache.get(cache_key)
        if cached:
            RAG_CACHE_HIT_COUNT.labels(feature=feature).inc()
            return CandidateComparison.model_validate(cached)

        RAG_CACHE_MISS_COUNT.labels(feature=feature).inc()

        resumes = await self.graph_db.get_resumes(candidate_uids)
        if len(resumes) != len(candidate_uids):
            missing = set(candidate_uids) - set(resumes.keys())
            raise ValueError(f"Resumes not found: {missing}")

        comparisons = self._compute_candidate_overlaps(list(resumes.values()))

        context = self._assemble_comparison_context(
            resumes=list(resumes.values()), comparisons=comparisons, criteria=criteria, job_context=job_context
        )

        llm = LLMService(
            system_prompt=self._get_comparison_system_prompt(), output_type=CandidateComparison, mode="text"
        )

        result = await llm.run(context, temperature=0.4)
        self._track_usage(feature, result.usage())

        duration = time.time() - start_time
        RAG_GENERATION_COUNT.labels(feature=feature, status="success").inc()
        RAG_GENERATION_DURATION.labels(feature=feature).observe(duration)

        cache.set(cache_key, result.output.model_dump(), timeout=settings.RAG_CACHE_COMPARE_TTL)

        logger.info("Generated comparison for %d candidates in %.2fs", len(candidate_uids), duration)

        return result.output

    async def generate_interview_questions(
        self,
        candidate_uid: str,
        interview_type: str = "technical",
        role_context: str | None = None,
        focus_areas: list[str] | None = None,
    ) -> InterviewQuestionSet:
        start_time = time.time()
        feature = "interview_questions"

        cache_key = self._make_cache_key(
            feature, uid=candidate_uid, type=interview_type, role=role_context, focus=focus_areas
        )
        cached = cache.get(cache_key)
        if cached:
            RAG_CACHE_HIT_COUNT.labels(feature=feature).inc()
            return InterviewQuestionSet.model_validate(cached)

        RAG_CACHE_MISS_COUNT.labels(feature=feature).inc()

        resume = await self.graph_db.get_resume(candidate_uid)
        if not resume:
            raise ValueError(f"Resume {candidate_uid} not found")

        seniority = self._infer_seniority(resume)
        complex_projects = self._identify_complex_projects(resume)
        skill_depth = self._estimate_skill_depth(resume)

        context = self._assemble_interview_context(
            resume=resume,
            seniority=seniority,
            complex_projects=complex_projects,
            skill_depth=skill_depth,
            interview_type=interview_type,
            role_context=role_context,
            focus_areas=focus_areas,
        )

        llm = LLMService(
            system_prompt=self._get_interview_questions_system_prompt(interview_type),
            output_type=InterviewQuestionSet,
            mode="text",
        )

        result = await llm.run(context, temperature=0.5)
        self._track_usage(feature, result.usage())

        duration = time.time() - start_time
        RAG_GENERATION_COUNT.labels(feature=feature, status="success").inc()
        RAG_GENERATION_DURATION.labels(feature=feature).observe(duration)

        cache.set(cache_key, result.output.model_dump(), timeout=settings.RAG_CACHE_INTERVIEW_TTL)

        logger.info("Generated interview questions for %s in %.2fs", candidate_uid, duration)

        return result.output

    def _get_match_explanation_system_prompt(self) -> str:
        return """You are a senior technical recruiter with 15 years of experience evaluating candidate-job fit.

Analyze the provided resume and job requirements to generate a structured match assessment.

**Your Task:**
1. Calculate an overall match_score (0.0-1.0) based on skills, experience, domain fit
2. Categorize as strong_fit (0.80+), moderate_fit (0.60-0.79), or weak_fit (<0.60)
3. Identify 1-5 key strengths, ordered by relevance
4. Note 0-5 concerns, ordered by severity
5. Write a 2-3 sentence executive summary
6. Suggest 3 key discussion points for interview

**Guidelines:**
- Be specific: Reference actual years, technologies, companies from resume
- Be objective: Base assessment on concrete data, not speculation
- Be actionable: Concerns should include mitigation strategies when possible
- Focus on fit: Not just "is candidate good?" but "is candidate right for THIS role?"

Return structured JobMatchExplanation following the schema."""

    def _get_comparison_system_prompt(self) -> str:
        return """You are an experienced hiring manager making final candidate decisions.

Compare the provided candidates across multiple dimensions to help stakeholders make informed hiring choices.

**Your Task:**
1. Score each candidate (0-10) across: technical_skills, experience_level, domain_expertise, cultural_indicators
2. Calculate overall_score as weighted average
3. Compare candidates across 4-8 key dimensions
   - For EACH dimension, you MUST create a DimensionComparison following this EXACT format:

   CORRECT FORMAT EXAMPLE:
   ```json
   {
     "dimension": "React Expertise",
     "candidates": {
       "2bf27a35-d4d1-4df3-8e3f-ba79075aa99e": "Expert-level React skills: 5+ years with Next.js, TypeScript, performance optimization",
       "244a047a-b2b6-439f-a508-57bc1cb7552a": "Limited React exposure, primarily backend Python/NLP focus"
     },
     "winner": "2bf27a35-d4d1-4df3-8e3f-ba79075aa99e",
     "analysis": "Clear advantage to first candidate in React ecosystem mastery"
   }
   ```

   CRITICAL RULES FOR 'candidates' FIELD:
   - KEYS: Use the EXACT UUID strings you see in the candidate context (the long format like "2bf27a35-d4d1-4df3-8e3f-ba79075aa99e")
   - VALUES: Write descriptive assessment text about their ability in this dimension
   - NEVER use "Candidate 1", "Candidate 2", or candidate names as keys
   - NEVER put UIDs in the values - only put assessment text in values

4. Provide scenario-based recommendations (immediate impact, long-term growth, etc.)
5. Note risks/concerns for each candidate as a list of RiskAssessment objects (uid + risk summary)
6. Rank candidates by overall_score

**Guidelines:**
- Be objective: Base assessments on resume data, not assumptions
- Be balanced: Every candidate has strengths and concerns
- Be specific: Reference actual projects, companies, skills
- Be fair: Don't over-penalize career gaps or non-traditional paths
- Focus on differentiation: Highlight what makes each candidate unique
- CRITICAL: Use the exact UID strings provided in the candidate context (the long UUID format), NOT "Candidate 1", NOT names, ONLY the actual UIDs

Return structured CandidateComparison following the schema."""

    def _get_interview_questions_system_prompt(self, interview_type: str) -> str:
        return f"""You are an experienced technical interviewer preparing for a {interview_type} interview.

Generate 6-12 tailored interview questions based on the candidate's actual resume.

**Your Task:**
1. Create questions that reference candidate's real experience (projects, companies, technologies)
2. Cover different categories: technical deep dive, behavioral, project architecture, problem-solving
3. Adjust difficulty to candidate's seniority level
4. Provide follow-up questions for each main question
5. Note red flags and good answer indicators
6. Estimate time for each question

**Question Quality Criteria:**
- **Specific:** "You worked with Redis at CompanyX..." not "Tell me about Redis"
- **Probing:** Questions that reveal depth of understanding
- **Fair:** Appropriate for candidate's level (don't ask Staff+ questions to junior devs)
- **Actionable:** Interviewer knows what to listen for

**Coverage:**
- 40% technical deep dive on claimed expertise
- 30% behavioral/situational based on career trajectory
- 20% project architecture/design decisions
- 10% problem-solving/system design

Return structured InterviewQuestionSet following the schema."""

    def _assemble_match_context(self, resume: Resume, job_description: str) -> str:
        return f"""
CANDIDATE PROFILE:
Name: {resume.personal_info.name}
Email: {resume.personal_info.contact.email}
Total Experience: {self._calculate_total_years(resume)} years
Current Role: {resume.employment_history[0].position if resume.employment_history else "N/A"}
Current Company: {resume.employment_history[0].company.name if resume.employment_history and resume.employment_history[0].company else "N/A"}

SKILLS: {", ".join(skill.name for skill in resume.skills[:20]) if resume.skills else "None listed"}

RECENT EXPERIENCE:
{self._format_recent_experience(resume.employment_history[:3])}

EDUCATION:
{self._format_education(resume.education[:2]) if resume.education else "None listed"}

---

JOB DESCRIPTION:
{job_description}
"""

    def _assemble_comparison_context(
        self, resumes: list[Resume], comparisons: dict, criteria: list[str] | None, job_context: str | None
    ) -> str:
        candidates_text = "\n\n".join(
            [
                f"""CANDIDATE {i + 1}: {r.personal_info.name}
UID: {r.uid}
Experience: {self._calculate_total_years(r)} years
Current Role: {r.employment_history[0].position if r.employment_history else "N/A"}
Current Company: {r.employment_history[0].company.name if r.employment_history and r.employment_history[0].company else "N/A"}
Top Skills: {", ".join(skill.name for skill in r.skills[:10])}
Education: {r.education[0].qualification + " in " + r.education[0].field if r.education and r.education[0].qualification else "N/A"}

Recent Experience:
{self._format_recent_experience(r.employment_history[:2])}"""
                for i, r in enumerate(resumes)
            ]
        )

        return f"""
{candidates_text}

---

COMPARISON CRITERIA:
{", ".join(criteria) if criteria else "General technical fit, experience level, domain expertise, cultural indicators"}

JOB CONTEXT:
{job_context or "Compare candidates generally across technical and soft skills"}

---

SKILL OVERLAP ANALYSIS:
{self._format_comparison_overlaps(comparisons)}
"""

    def _assemble_interview_context(
        self,
        resume: Resume,
        seniority: SeniorityLevel,
        complex_projects: list[str],
        skill_depth: dict,
        interview_type: str,
        role_context: str | None,
        focus_areas: list[str] | None,
    ) -> str:
        return f"""
CANDIDATE PROFILE:
Name: {resume.personal_info.name}
UID: {resume.uid}
Seniority Level: {seniority.value}
Total Experience: {self._calculate_total_years(resume)} years

EMPLOYMENT HISTORY:
{self._format_recent_experience(resume.employment_history)}

NOTABLE PROJECTS:
{chr(10).join(complex_projects) if complex_projects else "No complex projects explicitly listed"}

SKILL DEPTH ANALYSIS:
{self._format_skill_depth(skill_depth)}

EDUCATION:
{self._format_education(resume.education)}

---

INTERVIEW TYPE: {interview_type}
ROLE CONTEXT: {role_context or "General technical interview"}
FOCUS AREAS: {", ".join(focus_areas) if focus_areas else "Cover candidate strengths and verify experience depth"}
"""

    def _compute_candidate_overlaps(self, resumes: list[Resume]) -> dict:
        all_skills = [{skill.name.lower() for skill in r.skills} for r in resumes]

        common_skills = set.intersection(*all_skills) if all_skills else set()
        unique_skills = {resumes[i].uid: all_skills[i] - common_skills for i in range(len(resumes))}

        return {"common_skills": list(common_skills), "unique_skills": unique_skills}

    def _format_comparison_overlaps(self, comparisons: dict) -> str:
        lines = [f"Common Skills: {', '.join(comparisons.get('common_skills', []))}"]

        unique = comparisons.get("unique_skills", {})
        for uid, skills in unique.items():
            lines.append(f"Unique to {uid}: {', '.join(list(skills)[:5])}")

        return "\n".join(lines)

    def _identify_complex_projects(self, resume: Resume) -> list[str]:
        projects = []
        for proj in resume.projects[:3]:
            desc = f"- {proj.title}: {', '.join(s.name for s in proj.skills[:5])}"
            if proj.key_points:
                desc += f" | {proj.key_points[0].text[:100]}"
            projects.append(desc)
        return projects

    def _estimate_skill_depth(self, resume: Resume) -> dict:
        skill_counts: dict[str, int] = {}

        for skill in resume.skills:
            skill_counts[skill.name] = skill_counts.get(skill.name, 0) + 1

        for emp in resume.employment_history:
            for skill in emp.skills:
                skill_counts[skill.name] = skill_counts.get(skill.name, 0) + 1

        sorted_skills = sorted(skill_counts.items(), key=lambda x: x[1], reverse=True)
        return {"top_skills": dict(sorted_skills[:10])}

    def _format_skill_depth(self, skill_depth: dict) -> str:
        top = skill_depth.get("top_skills", {})
        if not top:
            return "No skill depth data available"

        return ", ".join([f"{skill} (appears {count}x)" for skill, count in top.items()])

    def _format_recent_experience(self, employment: list) -> str:
        if not employment:
            return "No employment history"

        lines = []
        for emp in employment:
            company = emp.company.name if emp.company else "Unknown"
            duration = f"{emp.duration.start} - {emp.duration.end or 'Present'}"
            lines.append(f"- {emp.position} at {company} ({duration})")
            if emp.key_points:
                lines.append(f"  {emp.key_points[0].text[:100]}")

        return "\n".join(lines)

    def _format_education(self, education: list) -> str:
        if not education:
            return "No education listed"

        lines = []
        for edu in education:
            qual = edu.qualification or "Degree"
            inst = edu.institution.name
            lines.append(f"- {qual} in {edu.field} from {inst}")

        return "\n".join(lines)

    def _make_cache_key(self, feature: str, **params) -> str:
        uid = params.get("uid")
        uids = params.get("uids")

        sorted_params = sorted(params.items())
        param_str = json.dumps(sorted_params, sort_keys=True, default=str)
        param_hash = hashlib.sha256(param_str.encode()).hexdigest()[:16]

        if uid:
            return f"rag:{feature}:uids:{uid}:{param_hash}"
        elif uids:
            uids_str = ",".join(sorted(uids))
            return f"rag:{feature}:uids:{uids_str}:{param_hash}"
        else:
            return f"rag:{feature}:{param_hash}"

    def _calculate_total_years(self, resume: Resume) -> int:
        if not resume.employment_history:
            return 0
        total_months = sum(emp.duration.duration_months for emp in resume.employment_history)
        return total_months // 12

    def _infer_seniority(self, resume: Resume) -> SeniorityLevel:
        years = self._calculate_total_years(resume)
        if years <= 2:
            return SeniorityLevel.JUNIOR
        elif years <= 5:
            return SeniorityLevel.MID_LEVEL
        elif years <= 10:
            return SeniorityLevel.SENIOR
        else:
            return SeniorityLevel.STAFF_PLUS

    def _track_usage(self, feature: str, usage: RunUsage) -> None:
        input_tokens = usage.input_tokens
        output_tokens = usage.output_tokens

        RAG_TOKEN_USAGE.labels(feature=feature, token_type="input").inc(input_tokens)
        RAG_TOKEN_USAGE.labels(feature=feature, token_type="output").inc(output_tokens)
