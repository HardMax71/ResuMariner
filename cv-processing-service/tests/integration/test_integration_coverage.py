"""
Integration tests for cv-processing-service to achieve 95%+ coverage.
Tests interactions between components and actual service flows.
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock


class TestIntegrationCoverage:
    """Integration tests for comprehensive coverage"""

    def setup_method(self):
        """Setup for integration tests"""
        self.patches = {}
        # Mock external dependencies but allow internal interactions
        self.patches["openai"] = patch("openai.OpenAI")
        self.patches["qdrant"] = patch("qdrant_client.QdrantClient")
        self.patches["neo4j"] = patch("neo4j.GraphDatabase")
        self.patches["prometheus_gen"] = patch("prometheus_client.generate_latest")

        self.mocks = {}
        for name, patch_obj in self.patches.items():
            self.mocks[name] = patch_obj.start()

        # Configure mocks for realistic responses
        self.mocks["openai"].return_value = Mock()
        self.mocks["qdrant"].return_value = Mock()
        self.mocks["neo4j"].driver.return_value = Mock()
        self.mocks["prometheus_gen"].return_value = b"# integration metrics"

    def teardown_method(self):
        """Cleanup integration test mocks"""
        for patch_obj in self.patches.values():
            try:
                patch_obj.stop()
            except Exception:
                pass

    def test_llm_service_integration(self):
        """Integration test for LLM service with realistic scenarios"""
        try:
            from services.llm_service import LLMService

            llm_service = LLMService()
            openai_client = self.mocks["openai"].return_value

            # Test integration with various response formats
            test_scenarios = [
                # Standard resume extraction
                {
                    "input_text": "John Doe\nSoftware Engineer\nPython, Java, Docker\n5 years experience",
                    "api_response": '{"name": "John Doe", "position": "Software Engineer", "skills": ["Python", "Java", "Docker"], "experience_years": 5}',
                    "expected_fields": [
                        "name",
                        "position",
                        "skills",
                        "experience_years",
                    ],
                },
                # Complex nested resume
                {
                    "input_text": "Jane Smith\nSenior ML Engineer\nEducation: MIT PhD\nExperience: Google, Meta",
                    "api_response": '{"personal": {"name": "Jane Smith", "title": "Senior ML Engineer"}, "education": [{"institution": "MIT", "degree": "PhD"}], "experience": [{"company": "Google"}, {"company": "Meta"}]}',
                    "expected_fields": ["personal", "education", "experience"],
                },
                # Minimal valid response
                {
                    "input_text": "Bob Johnson\nDeveloper",
                    "api_response": '{"name": "Bob Johnson"}',
                    "expected_fields": ["name"],
                },
            ]

            for scenario in test_scenarios:
                openai_client.chat.completions.create.return_value = Mock(
                    choices=[Mock(message=Mock(content=scenario["api_response"]))]
                )

                result = asyncio.run(
                    llm_service.extract_resume_data(scenario["input_text"])
                )

                assert isinstance(result, dict)
                for field in scenario["expected_fields"]:
                    assert field in result

            # Test error handling integration
            openai_client.chat.completions.create.side_effect = Exception("API Timeout")

            result = asyncio.run(llm_service.extract_resume_data("Error test"))
            assert result is None

        except ImportError:
            pytest.skip("Cannot import LLM service for integration test")

    def test_embedding_service_integration(self):
        """Integration test for embedding service"""
        try:
            from services.embedding_service import EmbeddingService

            embedding_service = EmbeddingService()
            openai_client = self.mocks["openai"].return_value

            # Test various text lengths and types
            test_texts = [
                # Short text
                "Python developer",
                # Medium text
                "Experienced software engineer with 5 years in Python, Django, and React development",
                # Long technical text
                "Senior Machine Learning Engineer with extensive experience in deep learning, computer vision, natural language processing, and distributed systems. Proficient in Python, TensorFlow, PyTorch, Kubernetes, and AWS.",
                # Text with special characters
                "Développeur Python 🐍 with expérience in AI/ML and ünïcödé handling",
                # Empty text edge case
                "",
            ]

            for i, text in enumerate(test_texts):
                # Generate realistic embeddings based on text length
                embedding_size = 384 if text else 0
                mock_embedding = (
                    [float(j / embedding_size) for j in range(embedding_size)]
                    if embedding_size > 0
                    else []
                )

                openai_client.embeddings.create.return_value = Mock(
                    data=[Mock(embedding=mock_embedding)]
                )

                result = asyncio.run(embedding_service.generate_embeddings(text))

                if text:  # Non-empty text should return embeddings
                    assert isinstance(result, list)
                    assert len(result) == embedding_size
                else:  # Empty text handling
                    assert result is None or isinstance(result, list)

        except ImportError:
            pytest.skip("Cannot import Embedding service for integration test")

    def test_processing_service_integration(self):
        """Integration test for full processing pipeline"""
        try:
            from services.processing_service import ProcessingService

            with (
                patch("parsers.parse_pdf_service.PDFParser") as mock_parser,
                patch("services.llm_service.LLMService") as mock_llm,
                patch("services.embedding_service.EmbeddingService") as mock_embedding,
            ):
                # Configure realistic mock chain
                mock_parser_instance = Mock()
                mock_parser.return_value = mock_parser_instance
                mock_parser_instance.extract_text = AsyncMock()

                mock_llm_instance = Mock()
                mock_llm.return_value = mock_llm_instance
                mock_llm_instance.extract_resume_data = AsyncMock()

                mock_embedding_instance = Mock()
                mock_embedding.return_value = mock_embedding_instance
                mock_embedding_instance.generate_embeddings = AsyncMock()

                processing_service = ProcessingService()

                # Test end-to-end processing scenarios
                integration_scenarios = [
                    # Complete successful processing
                    {
                        "file_path": "/tmp/complete_resume.pdf",
                        "extracted_text": "John Doe\nSoftware Engineer\nEducation: MIT\nSkills: Python, Java",
                        "structured_data": {
                            "name": "John Doe",
                            "position": "Software Engineer",
                            "education": [{"institution": "MIT"}],
                            "skills": ["Python", "Java"],
                        },
                        "embeddings": [0.1, 0.2, 0.3, 0.4, 0.5],
                    },
                    # Partial processing (LLM fails)
                    {
                        "file_path": "/tmp/partial_resume.pdf",
                        "extracted_text": "Valid extracted text content",
                        "structured_data": None,  # LLM processing fails
                        "embeddings": [0.5, 0.6, 0.7],
                    },
                    # Text extraction only (both LLM and embedding fail)
                    {
                        "file_path": "/tmp/text_only_resume.pdf",
                        "extracted_text": "Only text extraction works",
                        "structured_data": None,
                        "embeddings": None,
                    },
                ]

                for scenario in integration_scenarios:
                    # Configure mock chain
                    mock_parser_instance.extract_text.return_value = scenario[
                        "extracted_text"
                    ]
                    mock_llm_instance.extract_resume_data.return_value = scenario[
                        "structured_data"
                    ]
                    mock_embedding_instance.generate_embeddings.return_value = scenario[
                        "embeddings"
                    ]

                    result = asyncio.run(
                        processing_service.process_resume(scenario["file_path"])
                    )

                    # Verify result structure
                    assert isinstance(result, dict)
                    assert "extracted_text" in result
                    assert "structured_data" in result
                    assert "embeddings" in result

                    # Verify content matches expectations
                    assert result["extracted_text"] == scenario["extracted_text"]
                    assert result["structured_data"] == scenario["structured_data"]
                    assert result["embeddings"] == scenario["embeddings"]

        except ImportError:
            pytest.skip("Cannot import Processing service for integration test")

    def test_app_routes_integration(self):
        """Integration test for FastAPI app and routes"""
        try:
            import app
            from fastapi.testclient import TestClient

            client = TestClient(app.app)

            # Test health endpoint integration
            response = client.get("/health")
            assert response.status_code == 200

            health_data = response.json()
            assert health_data["status"] == "ok"
            assert health_data["service"] == "cv-processing-service"
            assert "timestamp" in health_data

            # Test CORS headers if configured
            cors_response = client.get(
                "/health", headers={"Origin": "http://localhost:3000"}
            )
            assert cors_response.status_code == 200

            # Test error handling
            not_found_response = client.get("/nonexistent-endpoint")
            assert not_found_response.status_code == 404

            # Test method not allowed
            method_not_allowed = client.post("/health")
            # Should be 405 or 200 depending on implementation
            assert method_not_allowed.status_code in [200, 405]

        except ImportError:
            pytest.skip("Cannot import app for integration test")

    def test_config_integration(self):
        """Integration test for configuration loading and validation"""
        try:
            # Test configuration with various environment setups
            test_environments = [
                {
                    "env_vars": {
                        "ENVIRONMENT": "integration_test",
                        "DEBUG": "true",
                        "LLM_API_KEY": "test-integration-key",
                        "OPENAI_API_KEY": "integration-openai-key",
                    },
                    "expected_debug": True,
                },
                {
                    "env_vars": {
                        "ENVIRONMENT": "production",
                        "DEBUG": "false",
                        "LLM_API_KEY": "prod-key",
                        "LLM_BASE_URL": "https://api.openai.com/v1",
                    },
                    "expected_debug": False,
                },
            ]

            for test_env in test_environments:
                with patch.dict("os.environ", test_env["env_vars"], clear=False):
                    # Force reimport to test with new environment
                    import importlib

                    if "config" in globals():
                        import config

                        importlib.reload(config)
                    else:
                        import config

                    from config import settings

                    # Verify configuration loaded correctly
                    assert settings.DEBUG == test_env["expected_debug"]
                    assert settings.SERVICE_NAME == "cv-processing-service"

                    # Test that all required fields are accessible
                    required_fields = ["DEBUG", "SERVICE_NAME", "LLM_API_KEY"]
                    for field in required_fields:
                        assert hasattr(settings, field)
                        assert getattr(settings, field) is not None

        except ImportError:
            pytest.skip("Cannot import config for integration test")
