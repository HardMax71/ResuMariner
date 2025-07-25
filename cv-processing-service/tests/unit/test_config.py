"""Comprehensive tests for cv-processing-service config.py to achieve 95%+ coverage."""

import pytest
from unittest.mock import patch
from pydantic import ValidationError


class TestSettings:
    """Test cv-processing-service Settings configuration"""

    def test_settings_default_values(self):
        """Test default configuration values"""
        from config import Settings

        with patch.dict("os.environ", {"LLM_API_KEY": "test-key-12345"}, clear=True):
            settings = Settings()

            assert settings.SERVICE_NAME == "cv-processing-service"
            assert settings.DEBUG is False
            assert settings.LOG_LEVEL == "INFO"
            assert settings.PORT == 8001
            assert settings.STORAGE_SERVICE_URL == "http://cv-storage-service:8002"
            assert settings.LLM_PROVIDER == "openai"
            assert settings.LLM_MODEL == "gpt-4o-mini"
            assert settings.PARALLEL_PROCESSING is False
            assert settings.EMBEDDING_MODEL == "all-MiniLM-L6-v2"
            assert settings.MAX_TOKENS_IN_RESUME_TO_PROCESS == 30000
            assert settings.TEMPERATURE == 0.0
            assert settings.REQUEST_TIMEOUT == 180
            assert settings.MAX_RETRIES == 3

    def test_settings_with_environment_variables(self):
        """Test settings with environment variables"""
        from config import Settings

        env_vars = {
            "SERVICE_NAME": "custom-processing-service",
            "DEBUG": "true",
            "LOG_LEVEL": "DEBUG",
            "PORT": "9001",
            "STORAGE_SERVICE_URL": "http://custom-storage:9002",
            "LLM_PROVIDER": "anthropic",
            "LLM_MODEL": "claude-3-haiku",
            "LLM_API_KEY": "custom-api-key-67890",
            "LLM_BASE_URL": "https://custom-llm-api.com",
            "PARALLEL_PROCESSING": "true",
            "EMBEDDING_MODEL": "custom-embedding-model",
            "MAX_TOKENS_IN_RESUME_TO_PROCESS": "50000",
            "TEMPERATURE": "0.5",
            "REQUEST_TIMEOUT": "300",
            "MAX_RETRIES": "5",
        }

        with patch.dict("os.environ", env_vars, clear=True):
            settings = Settings()

            assert settings.SERVICE_NAME == "custom-processing-service"
            assert settings.DEBUG is True
            assert settings.LOG_LEVEL == "DEBUG"
            assert settings.PORT == 9001
            assert settings.STORAGE_SERVICE_URL == "http://custom-storage:9002"
            assert settings.LLM_PROVIDER == "anthropic"
            assert settings.LLM_MODEL == "claude-3-haiku"
            assert settings.LLM_API_KEY == "custom-api-key-67890"
            assert settings.LLM_BASE_URL == "https://custom-llm-api.com"
            assert settings.PARALLEL_PROCESSING is True
            assert settings.EMBEDDING_MODEL == "custom-embedding-model"
            assert settings.MAX_TOKENS_IN_RESUME_TO_PROCESS == 50000
            assert settings.TEMPERATURE == 0.5
            assert settings.REQUEST_TIMEOUT == 300
            assert settings.MAX_RETRIES == 5

    def test_llm_provider_literal_validation(self):
        """Test LLM_PROVIDER accepts only valid values"""
        from config import Settings

        # Valid providers
        for provider in ["openai", "anthropic", "azure"]:
            with patch.dict(
                "os.environ",
                {"LLM_PROVIDER": provider, "LLM_API_KEY": "test-key"},
                clear=True,
            ):
                settings = Settings()
                assert settings.LLM_PROVIDER == provider

    def test_llm_api_key_validation_success(self):
        """Test valid LLM API key validation"""
        from config import Settings

        valid_keys = [
            "valid-api-key-123",
            "sk-1234567890abcdef",
            "  spaced-key-with-whitespace  ",  # Should be stripped
        ]

        for key in valid_keys:
            with patch.dict("os.environ", {"LLM_API_KEY": key}, clear=True):
                settings = Settings()
                assert settings.LLM_API_KEY == key.strip()

    def test_llm_api_key_validation_failure(self):
        """Test invalid LLM API key validation"""
        from config import Settings

        invalid_keys = [
            "",  # Empty string
            "   ",  # Only whitespace
        ]

        for key in invalid_keys:
            with patch.dict("os.environ", {"LLM_API_KEY": key}, clear=True):
                with pytest.raises(ValidationError) as exc_info:
                    Settings()
                assert "LLM_API_KEY is required and cannot be empty" in str(
                    exc_info.value
                )

    def test_llm_api_key_missing(self):
        """Test missing LLM API key raises validation error"""
        from config import Settings

        with patch.dict("os.environ", {}, clear=True):
            with pytest.raises(ValidationError):
                Settings()

    def test_llm_base_url_validation(self):
        """Test LLM_BASE_URL validation"""
        from config import Settings

        # Empty string should become None
        with patch.dict(
            "os.environ", {"LLM_BASE_URL": "", "LLM_API_KEY": "test-key"}, clear=True
        ):
            settings = Settings()
            assert settings.LLM_BASE_URL is None

        # Valid URL should remain
        with patch.dict(
            "os.environ",
            {"LLM_BASE_URL": "https://api.custom.com", "LLM_API_KEY": "test-key"},
            clear=True,
        ):
            settings = Settings()
            assert settings.LLM_BASE_URL == "https://api.custom.com"

        # None/unset should remain None
        with patch.dict("os.environ", {"LLM_API_KEY": "test-key"}, clear=True):
            settings = Settings()
            assert settings.LLM_BASE_URL is None

    def test_field_constraints(self):
        """Test field constraints and validation"""
        from config import Settings

        # Test temperature constraints (0.0 to 2.0)
        valid_temps = ["0.0", "1.0", "2.0", "0.5", "1.5"]
        for temp in valid_temps:
            with patch.dict(
                "os.environ",
                {"TEMPERATURE": temp, "LLM_API_KEY": "test-key"},
                clear=True,
            ):
                settings = Settings()
                assert 0.0 <= settings.TEMPERATURE <= 2.0

        # Test request timeout constraints (30 to 600)
        valid_timeouts = ["30", "180", "600", "300"]
        for timeout in valid_timeouts:
            with patch.dict(
                "os.environ",
                {"REQUEST_TIMEOUT": timeout, "LLM_API_KEY": "test-key"},
                clear=True,
            ):
                settings = Settings()
                assert 30 <= settings.REQUEST_TIMEOUT <= 600

        # Test max retries constraints (1 to 10)
        valid_retries = ["1", "3", "10", "5"]
        for retries in valid_retries:
            with patch.dict(
                "os.environ",
                {"MAX_RETRIES": retries, "LLM_API_KEY": "test-key"},
                clear=True,
            ):
                settings = Settings()
                assert 1 <= settings.MAX_RETRIES <= 10

    def test_config_class_attributes(self):
        """Test Config class attributes"""
        from config import Settings

        config = Settings.Config
        assert config.env_file == ".env"
        assert config.env_file_encoding == "utf-8"
        assert config.case_sensitive is True

    def test_settings_serialization(self):
        """Test settings can be serialized"""
        from config import Settings

        with patch.dict("os.environ", {"LLM_API_KEY": "test-key"}, clear=True):
            settings = Settings()

            # Should be able to convert to dict
            settings_dict = settings.model_dump()
            assert isinstance(settings_dict, dict)
            assert "SERVICE_NAME" in settings_dict
            assert "LLM_API_KEY" in settings_dict

    def test_settings_json_serialization(self):
        """Test settings JSON serialization"""
        from config import Settings

        with patch.dict("os.environ", {"LLM_API_KEY": "test-key"}, clear=True):
            settings = Settings()

            # Should be able to convert to JSON
            json_str = settings.model_dump_json()
            assert isinstance(json_str, str)
            assert "cv-processing-service" in json_str

    def test_field_descriptions(self):
        """Test field descriptions are properly set"""
        from config import Settings

        schema = Settings.model_json_schema()

        # Check that descriptions exist for key fields
        assert "description" in schema["properties"]["STORAGE_SERVICE_URL"]
        assert "description" in schema["properties"]["LLM_API_KEY"]
        assert "description" in schema["properties"]["LLM_BASE_URL"]

    def test_settings_instance_creation(self):
        """Test global settings instance is created"""
        from config import settings

        assert settings is not None
        assert hasattr(settings, "SERVICE_NAME")
        assert hasattr(settings, "LLM_PROVIDER")

    def test_validator_functions_coverage(self):
        """Test validator functions are called"""
        from config import Settings

        # Test that validators are actually called during validation
        with patch.dict(
            "os.environ",
            {"LLM_API_KEY": "  test-key-with-spaces  ", "LLM_BASE_URL": ""},
            clear=True,
        ):
            settings = Settings()

            # Validator should strip the API key
            assert settings.LLM_API_KEY == "test-key-with-spaces"
            # Validator should convert empty string to None
            assert settings.LLM_BASE_URL is None

    def test_all_llm_providers(self):
        """Test all supported LLM providers"""
        from config import Settings

        providers = ["openai", "anthropic", "azure"]

        for provider in providers:
            with patch.dict(
                "os.environ",
                {"LLM_PROVIDER": provider, "LLM_API_KEY": f"test-key-for-{provider}"},
                clear=True,
            ):
                settings = Settings()
                assert settings.LLM_PROVIDER == provider

    def test_boolean_field_parsing(self):
        """Test boolean field parsing from environment"""
        from config import Settings

        # Test various boolean representations
        boolean_tests = [
            ("true", True),
            ("True", True),
            ("TRUE", True),
            ("1", True),
            ("false", False),
            ("False", False),
            ("FALSE", False),
            ("0", False),
        ]

        for env_value, expected in boolean_tests:
            with patch.dict(
                "os.environ",
                {
                    "DEBUG": env_value,
                    "PARALLEL_PROCESSING": env_value,
                    "LLM_API_KEY": "test-key",
                },
                clear=True,
            ):
                settings = Settings()
                assert settings.DEBUG == expected
                assert settings.PARALLEL_PROCESSING == expected
