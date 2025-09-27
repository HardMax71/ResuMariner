"""Integration-style tests for core domain models and file utilities."""

from __future__ import annotations

from pathlib import Path

from django.test import TestCase

from core.domain import (
    CompanyInfo,
    Contact,
    EmploymentDuration,
    EmploymentHistoryItem,
    EmploymentType,
    KeyPoint,
    Location,
    PersonalInfo,
    Preferences,
    ProfessionalProfile,
    Resume,
    ResumeSearchResult,
    SearchFilters,
    SearchRequest,
    SearchType,
    Skill,
    Technology,
    VectorHit,
    WorkMode,
)
from core.file_types import ALLOWED_EXTENSIONS, ParserType, get_parser_type, validate_file_signature

TEST_PDF = Path(__file__).resolve().parent.parent / "test_inputs" / "Max_Azatian_CV.pdf"


class ResumeDomainModelTests(TestCase):
    """Validate behaviour of the core resume domain models."""

    def setUp(self) -> None:
        personal_info = PersonalInfo(
            name="Max Azatian",
            resume_lang="English",
            contact=Contact(email="max.azatian@example.com", phone="+374 12 34 56"),
        )
        preferences = Preferences(
            role="Backend Engineer",
            employment_types=[EmploymentType.FULL_TIME],
            work_modes=[WorkMode.REMOTE],
            salary="120000 USD",
        )
        profile = ProfessionalProfile(
            summary="Senior Python developer with production Django experience.",
            preferences=preferences,
        )
        skills = [Skill(name="Python"), Skill(name="Django")]
        company = CompanyInfo(name="AI Labs")
        duration = EmploymentDuration(
            date_format="MM.YYYY",
            start="01.2020",
            end="07.2023",
            duration_months=42,
        )
        location = Location(city="Yerevan", country="Armenia")
        key_points = [
            KeyPoint(text="Led development of resume matching pipeline"),
            KeyPoint(text="Shipped embeddings search service at scale"),
        ]
        technologies = [
            Technology(name="Django"),
            Technology(name="PostgreSQL"),
        ]
        history_payload = {
            "position": "Senior Backend Engineer",
            "employment_type": EmploymentType.FULL_TIME.value,
            "work_mode": WorkMode.REMOTE.value,
            "company": company.model_dump(mode="json"),
            "duration": duration.model_dump(mode="json"),
            "location": location.model_dump(mode="json"),
            "key_points": [kp.model_dump(mode="json") for kp in key_points],
            "technologies": [tech.model_dump(mode="json") for tech in technologies],
        }
        history_item = EmploymentHistoryItem.model_validate(history_payload)

        resume_payload = {
            "uid": "test-resume-001",
            "personal_info": personal_info.model_dump(mode="json"),
            "professional_profile": profile.model_dump(mode="json"),
            "skills": [skill.model_dump(mode="json") for skill in skills],
            "employment_history": [history_item.model_dump(mode="json")],
        }

        self.resume = Resume.model_validate(resume_payload)

    def test_resume_serialization_includes_nested_fields(self) -> None:
        payload = self.resume.model_dump(mode="json")

        self.assertEqual(payload["personal_info"]["contact"]["email"], "max.azatian@example.com")
        self.assertEqual(payload["skills"], [{"name": "Python"}, {"name": "Django"}])

        history_entry = payload["employment_history"][0]
        self.assertEqual(history_entry["company"]["name"], "AI Labs")
        self.assertEqual(history_entry["duration"]["duration_months"], 42)
        self.assertEqual(history_entry["technologies"][0]["name"], "Django")

        profile = payload["professional_profile"]
        self.assertEqual(profile["preferences"]["role"], "Backend Engineer")
        self.assertEqual(profile["preferences"]["employment_types"], [EmploymentType.FULL_TIME.value])

    def test_resume_helper_methods(self) -> None:
        self.assertAlmostEqual(self.resume.years_of_experience(), 3.5)
        self.assertTrue(self.resume.has_skill("python"))
        self.assertFalse(self.resume.has_skill("Go"))
        self.assertEqual(self.resume.get_technologies(), {"Django", "PostgreSQL"})


class SearchModelBehaviourTests(TestCase):
    """Ensure search-related domain helpers provide consistent ordering and data."""

    def test_resume_search_result_from_matches_prefers_highest_score(self) -> None:
        hits = [
            VectorHit(resume_id="res-1", text="Python", score=0.72, source="skills"),
            VectorHit(resume_id="res-1", text="Django", score=0.94, source="experience"),
            VectorHit(resume_id="res-1", text="GraphQL", score=0.65, source="experience"),
        ]

        result = ResumeSearchResult.from_matches("res-1", hits)

        self.assertEqual(result.resume_id, "res-1")
        self.assertEqual(result.score, 0.94)
        self.assertEqual([hit.text for hit in result.matches], ["Django", "Python", "GraphQL"])

    def test_search_request_holds_filters_and_limits(self) -> None:
        filters = SearchFilters(skills=["Python"], role="Backend Engineer", location="Yerevan")
        request = SearchRequest(
            search_type=SearchType.SEMANTIC,
            filters=filters,
            query="experienced python developer",
            limit=5,
            min_score=0.35,
            max_matches_per_result=3,
        )

        self.assertEqual(request.search_type, SearchType.SEMANTIC)
        self.assertEqual(request.filters.skills, ["Python"])
        self.assertEqual(request.query, "experienced python developer")
        self.assertEqual(request.limit, 5)
        self.assertEqual(request.max_matches_per_result, 3)


class FileTypeValidationTests(TestCase):
    """Validate file signature and parser detection using the bundled sample PDF."""

    def test_pdf_signature_matches_expected_bytes(self) -> None:
        pdf_bytes = TEST_PDF.read_bytes()

        self.assertIn(".pdf", ALLOWED_EXTENSIONS)
        self.assertTrue(validate_file_signature(".pdf", pdf_bytes))
        self.assertFalse(validate_file_signature(".pdf", pdf_bytes[8:]))

    def test_parser_type_detection(self) -> None:
        self.assertEqual(get_parser_type(".pdf"), ParserType.PDF)
        self.assertEqual(get_parser_type(".png"), ParserType.IMAGE)
        self.assertIsNone(get_parser_type(".txt"))
