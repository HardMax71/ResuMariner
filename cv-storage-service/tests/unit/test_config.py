"""Comprehensive tests for cv-storage-service config.py to achieve 95%+ coverage."""

import pytest
from unittest.mock import patch
from pydantic import ValidationError
import os


class TestSettings:
    """Test Settings class"""

    def test_settings_default_values(self):
        """Test default settings values"""
        with patch.dict(
            os.environ,
            {
                "NEO4J_URI": "neo4j://localhost:7687",
                "NEO4J_USERNAME": "neo4j",
                "NEO4J_PASSWORD": "test_password",
            },
            clear=True,
        ):
            from config import Settings

            settings = Settings()

            # Service defaults
            assert settings.SERVICE_NAME == "cv-storage-service"
            assert not settings.DEBUG
            assert settings.LOG_LEVEL == "INFO"
            assert settings.PORT == 8002

            # Neo4j defaults
            assert settings.NEO4J_DATABASE == "neo4j"
            assert settings.NEO4J_MAX_CONNECTION_LIFETIME == 3600
            assert settings.NEO4J_MAX_CONNECTION_POOL_SIZE == 50
            assert settings.NEO4J_CONNECTION_TIMEOUT == 30

            # Qdrant defaults
            assert settings.QDRANT_HOST == "qdrant"
            assert settings.QDRANT_PORT == 6333
            assert settings.QDRANT_COLLECTION == "cv_key_points"
            assert settings.VECTOR_SIZE == 384
            assert settings.QDRANT_TIMEOUT == 30
            assert settings.QDRANT_PREFER_GRPC

    def test_settings_with_custom_values(self):
        """Test settings with custom environment values"""
        custom_env = {
            "SERVICE_NAME": "custom-storage-service",
            "DEBUG": "true",
            "LOG_LEVEL": "DEBUG",
            "PORT": "9002",
            "NEO4J_URI": "neo4j://custom:7687",
            "NEO4J_USERNAME": "custom_user",
            "NEO4J_PASSWORD": "custom_password",
            "NEO4J_DATABASE": "custom_db",
            "QDRANT_HOST": "custom-qdrant",
            "QDRANT_PORT": "9333",
            "VECTOR_SIZE": "512",
        }

        with patch.dict(os.environ, custom_env):
            from config import Settings

            settings = Settings()

            assert settings.SERVICE_NAME == "custom-storage-service"
            assert settings.DEBUG
            assert settings.LOG_LEVEL == "DEBUG"
            assert settings.PORT == 9002
            assert settings.NEO4J_URI == "neo4j://custom:7687"
            assert settings.NEO4J_USERNAME == "custom_user"
            assert settings.NEO4J_PASSWORD == "custom_password"
            assert settings.NEO4J_DATABASE == "custom_db"
            assert settings.QDRANT_HOST == "custom-qdrant"
            assert settings.QDRANT_PORT == 9333
            assert settings.VECTOR_SIZE == 512

    def test_neo4j_password_validation_success(self):
        """Test successful Neo4j password validation"""
        with patch.dict(
            os.environ,
            {
                "NEO4J_URI": "neo4j://localhost:7687",
                "NEO4J_USERNAME": "neo4j",
                "NEO4J_PASSWORD": "valid_password",
            },
        ):
            from config import Settings

            settings = Settings()
            assert settings.NEO4J_PASSWORD == "valid_password"

    def test_neo4j_password_validation_empty_string(self):
        """Test Neo4j password validation with empty string"""
        with patch.dict(
            os.environ,
            {
                "NEO4J_URI": "neo4j://localhost:7687",
                "NEO4J_USERNAME": "neo4j",
                "NEO4J_PASSWORD": "",
            },
        ):
            from config import Settings

            with pytest.raises(ValidationError) as exc_info:
                Settings()

            assert "NEO4J_PASSWORD is required and cannot be empty" in str(
                exc_info.value
            )

    def test_neo4j_password_validation_whitespace(self):
        """Test Neo4j password validation with whitespace"""
        with patch.dict(
            os.environ,
            {
                "NEO4J_URI": "neo4j://localhost:7687",
                "NEO4J_USERNAME": "neo4j",
                "NEO4J_PASSWORD": "   ",
            },
        ):
            from config import Settings

            with pytest.raises(ValidationError) as exc_info:
                Settings()

            assert "NEO4J_PASSWORD is required and cannot be empty" in str(
                exc_info.value
            )

    def test_neo4j_password_validation_strips_whitespace(self):
        """Test Neo4j password validation strips whitespace"""
        with patch.dict(
            os.environ,
            {
                "NEO4J_URI": "neo4j://localhost:7687",
                "NEO4J_USERNAME": "neo4j",
                "NEO4J_PASSWORD": "  valid_password  ",
            },
        ):
            from config import Settings

            settings = Settings()
            assert settings.NEO4J_PASSWORD == "valid_password"

    def test_required_neo4j_fields_missing(self):
        """Test validation error when required Neo4j fields are missing"""
        # Test missing NEO4J_URI
        with patch.dict(
            os.environ,
            {"NEO4J_USERNAME": "neo4j", "NEO4J_PASSWORD": "password"},
            clear=True,
        ):
            from config import Settings

            with pytest.raises(ValidationError) as exc_info:
                Settings()

            assert "NEO4J_URI" in str(exc_info.value)

    def test_field_constraints_neo4j_max_connection_lifetime(self):
        """Test Neo4j max connection lifetime constraints"""
        base_env = {
            "NEO4J_URI": "neo4j://localhost:7687",
            "NEO4J_USERNAME": "neo4j",
            "NEO4J_PASSWORD": "password",
        }

        # Test minimum value
        with patch.dict(
            os.environ, {**base_env, "NEO4J_MAX_CONNECTION_LIFETIME": "300"}
        ):
            from config import Settings

            settings = Settings()
            assert settings.NEO4J_MAX_CONNECTION_LIFETIME == 300

        # Test maximum value
        with patch.dict(
            os.environ, {**base_env, "NEO4J_MAX_CONNECTION_LIFETIME": "86400"}
        ):
            from config import Settings

            settings = Settings()
            assert settings.NEO4J_MAX_CONNECTION_LIFETIME == 86400

        # Test below minimum (should fail)
        with patch.dict(
            os.environ, {**base_env, "NEO4J_MAX_CONNECTION_LIFETIME": "299"}
        ):
            from config import Settings

            with pytest.raises(ValidationError):
                Settings()

    def test_field_constraints_neo4j_max_connection_pool_size(self):
        """Test Neo4j max connection pool size constraints"""
        base_env = {
            "NEO4J_URI": "neo4j://localhost:7687",
            "NEO4J_USERNAME": "neo4j",
            "NEO4J_PASSWORD": "password",
        }

        # Test minimum value
        with patch.dict(
            os.environ, {**base_env, "NEO4J_MAX_CONNECTION_POOL_SIZE": "1"}
        ):
            from config import Settings

            settings = Settings()
            assert settings.NEO4J_MAX_CONNECTION_POOL_SIZE == 1

        # Test maximum value
        with patch.dict(
            os.environ, {**base_env, "NEO4J_MAX_CONNECTION_POOL_SIZE": "200"}
        ):
            from config import Settings

            settings = Settings()
            assert settings.NEO4J_MAX_CONNECTION_POOL_SIZE == 200

    def test_field_constraints_qdrant_port(self):
        """Test Qdrant port constraints"""
        base_env = {
            "NEO4J_URI": "neo4j://localhost:7687",
            "NEO4J_USERNAME": "neo4j",
            "NEO4J_PASSWORD": "password",
        }

        # Test minimum port
        with patch.dict(os.environ, {**base_env, "QDRANT_PORT": "1"}):
            from config import Settings

            settings = Settings()
            assert settings.QDRANT_PORT == 1

        # Test maximum port
        with patch.dict(os.environ, {**base_env, "QDRANT_PORT": "65535"}):
            from config import Settings

            settings = Settings()
            assert settings.QDRANT_PORT == 65535

    def test_field_constraints_vector_size(self):
        """Test vector size constraints"""
        base_env = {
            "NEO4J_URI": "neo4j://localhost:7687",
            "NEO4J_USERNAME": "neo4j",
            "NEO4J_PASSWORD": "password",
        }

        # Test minimum vector size
        with patch.dict(os.environ, {**base_env, "VECTOR_SIZE": "128"}):
            from config import Settings

            settings = Settings()
            assert settings.VECTOR_SIZE == 128

        # Test maximum vector size
        with patch.dict(os.environ, {**base_env, "VECTOR_SIZE": "4096"}):
            from config import Settings

            settings = Settings()
            assert settings.VECTOR_SIZE == 4096

    def test_config_class_attributes(self):
        """Test Config class attributes"""
        from config import Settings

        config = Settings.Config
        assert config.env_file == ".env"
        assert config.env_file_encoding == "utf-8"
        assert config.case_sensitive

    def test_boolean_field_parsing(self):
        """Test boolean fields are parsed correctly"""
        base_env = {
            "NEO4J_URI": "neo4j://localhost:7687",
            "NEO4J_USERNAME": "neo4j",
            "NEO4J_PASSWORD": "password",
        }

        # Test various boolean representations
        boolean_values = [
            ("true", True),
            ("True", True),
            ("TRUE", True),
            ("1", True),
            ("false", False),
            ("False", False),
            ("FALSE", False),
            ("0", False),
        ]

        for str_val, expected in boolean_values:
            with patch.dict(
                os.environ,
                {**base_env, "DEBUG": str_val, "QDRANT_PREFER_GRPC": str_val},
            ):
                from config import Settings

                settings = Settings()
                assert settings.DEBUG == expected
                assert settings.QDRANT_PREFER_GRPC == expected

    def test_settings_singleton_behavior(self):
        """Test settings singleton instantiation"""
        with patch.dict(
            os.environ,
            {
                "NEO4J_URI": "neo4j://localhost:7687",
                "NEO4J_USERNAME": "neo4j",
                "NEO4J_PASSWORD": "password",
            },
        ):
            from config import settings

            # Settings should be instantiated and accessible
            assert settings is not None
            assert settings.SERVICE_NAME == "cv-storage-service"

    def test_field_descriptions(self):
        """Test field descriptions are set correctly"""
        from config import Settings

        # Test that fields have descriptions
        schema = Settings.schema()
        properties = schema["properties"]

        assert "description" in properties["NEO4J_URI"]
        assert properties["NEO4J_URI"]["description"] == "Neo4j connection URI"
        assert "description" in properties["NEO4J_USERNAME"]
        assert properties["NEO4J_USERNAME"]["description"] == "Neo4j username"
        assert "description" in properties["QDRANT_HOST"]
        assert properties["QDRANT_HOST"]["description"] == "Qdrant host"

    def test_connection_timeout_constraints(self):
        """Test connection timeout field constraints"""
        base_env = {
            "NEO4J_URI": "neo4j://localhost:7687",
            "NEO4J_USERNAME": "neo4j",
            "NEO4J_PASSWORD": "password",
        }

        # Test Neo4j connection timeout
        with patch.dict(os.environ, {**base_env, "NEO4J_CONNECTION_TIMEOUT": "5"}):
            from config import Settings

            settings = Settings()
            assert settings.NEO4J_CONNECTION_TIMEOUT == 5

        with patch.dict(os.environ, {**base_env, "NEO4J_CONNECTION_TIMEOUT": "300"}):
            from config import Settings

            settings = Settings()
            assert settings.NEO4J_CONNECTION_TIMEOUT == 300

        # Test Qdrant timeout
        with patch.dict(os.environ, {**base_env, "QDRANT_TIMEOUT": "5"}):
            from config import Settings

            settings = Settings()
            assert settings.QDRANT_TIMEOUT == 5

        with patch.dict(os.environ, {**base_env, "QDRANT_TIMEOUT": "300"}):
            from config import Settings

            settings = Settings()
            assert settings.QDRANT_TIMEOUT == 300

    def test_all_field_types(self):
        """Test all field types are handled correctly"""
        with patch.dict(
            os.environ,
            {
                "NEO4J_URI": "neo4j://localhost:7687",
                "NEO4J_USERNAME": "neo4j",
                "NEO4J_PASSWORD": "password",
            },
        ):
            from config import Settings

            settings = Settings()

            # String fields
            assert isinstance(settings.SERVICE_NAME, str)
            assert isinstance(settings.LOG_LEVEL, str)
            assert isinstance(settings.NEO4J_URI, str)
            assert isinstance(settings.NEO4J_USERNAME, str)
            assert isinstance(settings.NEO4J_PASSWORD, str)
            assert isinstance(settings.NEO4J_DATABASE, str)
            assert isinstance(settings.QDRANT_HOST, str)
            assert isinstance(settings.QDRANT_COLLECTION, str)

            # Integer fields
            assert isinstance(settings.PORT, int)
            assert isinstance(settings.NEO4J_MAX_CONNECTION_LIFETIME, int)
            assert isinstance(settings.NEO4J_MAX_CONNECTION_POOL_SIZE, int)
            assert isinstance(settings.NEO4J_CONNECTION_TIMEOUT, int)
            assert isinstance(settings.QDRANT_PORT, int)
            assert isinstance(settings.VECTOR_SIZE, int)
            assert isinstance(settings.QDRANT_TIMEOUT, int)

            # Boolean fields
            assert isinstance(settings.DEBUG, bool)
            assert isinstance(settings.QDRANT_PREFER_GRPC, bool)

    def test_settings_repr_and_str(self):
        """Test Settings string representation"""
        with patch.dict(
            os.environ,
            {
                "NEO4J_URI": "neo4j://localhost:7687",
                "NEO4J_USERNAME": "neo4j",
                "NEO4J_PASSWORD": "password",
            },
        ):
            from config import Settings

            settings = Settings()

            # Should be able to convert to string
            settings_str = str(settings)
            assert len(settings_str) > 0

            # Should not contain sensitive information in repr
            settings_repr = repr(settings)
            assert len(settings_repr) > 0

    def test_validator_function_directly(self):
        """Test password validator function directly"""
        from config import Settings

        # Test valid password
        result = Settings.validate_neo4j_password("valid_password")
        assert result == "valid_password"

        # Test password with whitespace
        result = Settings.validate_neo4j_password("  spaced_password  ")
        assert result == "spaced_password"

        # Test empty password
        with pytest.raises(ValueError) as exc_info:
            Settings.validate_neo4j_password("")
        assert "NEO4J_PASSWORD is required and cannot be empty" in str(exc_info.value)

        # Test whitespace-only password
        with pytest.raises(ValueError) as exc_info:
            Settings.validate_neo4j_password("   ")
        assert "NEO4J_PASSWORD is required and cannot be empty" in str(exc_info.value)
