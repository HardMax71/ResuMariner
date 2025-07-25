"""Comprehensive tests for cv-search-service config.py to achieve 95%+ coverage."""

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
                "API_KEY": "test-api-key-16char",
                "JWT_SECRET": "super-secret-jwt-key-that-is-very-long-32-chars",
            },
            clear=True,
        ):
            from config import Settings

            settings = Settings()

            # Service defaults
            assert settings.SERVICE_NAME == "cv-search-service"
            assert not settings.DEBUG
            assert settings.LOG_LEVEL == "INFO"
            assert settings.PORT == 8003

            # Neo4j defaults
            assert settings.NEO4J_DATABASE == "neo4j"
            assert settings.NEO4J_MAX_CONNECTION_LIFETIME == 3600
            assert settings.NEO4J_MAX_CONNECTION_POOL_SIZE == 50
            assert settings.NEO4J_CONNECTION_TIMEOUT == 30

            # Qdrant defaults
            assert settings.QDRANT_HOST == "qdrant"
            assert settings.QDRANT_PORT == 6333
            assert settings.QDRANT_COLLECTION == "cv_key_points"
            assert settings.QDRANT_TIMEOUT == 30
            assert settings.QDRANT_PREFER_GRPC

            # Embedding defaults
            assert settings.EMBEDDING_MODEL == "all-MiniLM-L6-v2"
            assert settings.VECTOR_SIZE == 384

            # Search defaults
            assert settings.DEFAULT_VECTOR_WEIGHT == 0.7
            assert settings.DEFAULT_GRAPH_WEIGHT == 0.3

            # Performance defaults
            assert settings.CACHE_ENABLED
            assert settings.CACHE_TTL == 3600

            # JWT defaults
            assert settings.JWT_ALGORITHM == "HS256"

            # Rate limiting defaults
            assert settings.RATE_LIMIT_SEARCH == "20/minute"
            assert settings.RATE_LIMIT_SUGGEST == "30/minute"

    def test_settings_with_custom_values(self):
        """Test settings with custom environment values"""
        custom_env = {
            "SERVICE_NAME": "custom-search-service",
            "DEBUG": "true",
            "LOG_LEVEL": "DEBUG",
            "PORT": "9003",
            "NEO4J_URI": "neo4j://custom:7687",
            "NEO4J_USERNAME": "custom_user",
            "NEO4J_PASSWORD": "custom_password",
            "NEO4J_DATABASE": "custom_db",
            "QDRANT_HOST": "custom-qdrant",
            "QDRANT_PORT": "9333",
            "EMBEDDING_MODEL": "custom-model",
            "VECTOR_SIZE": "512",
            "DEFAULT_VECTOR_WEIGHT": "0.8",
            "DEFAULT_GRAPH_WEIGHT": "0.2",
            "CACHE_ENABLED": "false",
            "CACHE_TTL": "7200",
            "API_KEY": "custom-api-key-16char",
            "JWT_SECRET": "custom-jwt-secret-that-is-very-long-32-chars",
            "JWT_ALGORITHM": "HS512",
            "RATE_LIMIT_SEARCH": "10/minute",
            "RATE_LIMIT_SUGGEST": "15/minute",
        }

        with patch.dict(os.environ, custom_env):
            from config import Settings

            settings = Settings()

            assert settings.SERVICE_NAME == "custom-search-service"
            assert settings.DEBUG
            assert settings.LOG_LEVEL == "DEBUG"
            assert settings.PORT == 9003
            assert settings.NEO4J_URI == "neo4j://custom:7687"
            assert settings.NEO4J_USERNAME == "custom_user"
            assert settings.NEO4J_PASSWORD == "custom_password"
            assert settings.NEO4J_DATABASE == "custom_db"
            assert settings.QDRANT_HOST == "custom-qdrant"
            assert settings.QDRANT_PORT == 9333
            assert settings.EMBEDDING_MODEL == "custom-model"
            assert settings.VECTOR_SIZE == 512
            assert settings.DEFAULT_VECTOR_WEIGHT == 0.8
            assert settings.DEFAULT_GRAPH_WEIGHT == 0.2
            assert not settings.CACHE_ENABLED
            assert settings.CACHE_TTL == 7200
            assert settings.API_KEY == "custom-api-key-16char"
            assert settings.JWT_SECRET == "custom-jwt-secret-that-is-very-long-32-chars"
            assert settings.JWT_ALGORITHM == "HS512"
            assert settings.RATE_LIMIT_SEARCH == "10/minute"
            assert settings.RATE_LIMIT_SUGGEST == "15/minute"

    def test_neo4j_password_validation_success(self):
        """Test successful Neo4j password validation"""
        with patch.dict(
            os.environ,
            {
                "NEO4J_URI": "neo4j://localhost:7687",
                "NEO4J_USERNAME": "neo4j",
                "NEO4J_PASSWORD": "valid_password",
                "API_KEY": "test-api-key-16char",
                "JWT_SECRET": "super-secret-jwt-key-that-is-very-long-32-chars",
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
                "API_KEY": "test-api-key-16char",
                "JWT_SECRET": "super-secret-jwt-key-that-is-very-long-32-chars",
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
                "API_KEY": "test-api-key-16char",
                "JWT_SECRET": "super-secret-jwt-key-that-is-very-long-32-chars",
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
                "API_KEY": "test-api-key-16char",
                "JWT_SECRET": "super-secret-jwt-key-that-is-very-long-32-chars",
            },
        ):
            from config import Settings

            settings = Settings()
            assert settings.NEO4J_PASSWORD == "valid_password"

    def test_weights_validation_success(self):
        """Test successful weights validation"""
        with patch.dict(
            os.environ,
            {
                "NEO4J_URI": "neo4j://localhost:7687",
                "NEO4J_USERNAME": "neo4j",
                "NEO4J_PASSWORD": "password",
                "API_KEY": "test-api-key-16char",
                "JWT_SECRET": "super-secret-jwt-key-that-is-very-long-32-chars",
                "DEFAULT_VECTOR_WEIGHT": "0.6",
                "DEFAULT_GRAPH_WEIGHT": "0.4",
            },
        ):
            from config import Settings

            settings = Settings()
            assert settings.DEFAULT_VECTOR_WEIGHT == 0.6
            assert settings.DEFAULT_GRAPH_WEIGHT == 0.4

    def test_weights_validation_failure(self):
        """Test weights validation failure when they don't sum to 1.0"""
        with patch.dict(
            os.environ,
            {
                "NEO4J_URI": "neo4j://localhost:7687",
                "NEO4J_USERNAME": "neo4j",
                "NEO4J_PASSWORD": "password",
                "API_KEY": "test-api-key-16char",
                "JWT_SECRET": "super-secret-jwt-key-that-is-very-long-32-chars",
                "DEFAULT_VECTOR_WEIGHT": "0.6",
                "DEFAULT_GRAPH_WEIGHT": "0.5",  # 0.6 + 0.5 = 1.1 != 1.0
            },
        ):
            from config import Settings

            with pytest.raises(ValidationError) as exc_info:
                Settings()

            assert "Vector weight and graph weight must sum to 1.0" in str(
                exc_info.value
            )

    def test_weights_validation_with_tolerance(self):
        """Test weights validation passes within tolerance"""
        with patch.dict(
            os.environ,
            {
                "NEO4J_URI": "neo4j://localhost:7687",
                "NEO4J_USERNAME": "neo4j",
                "NEO4J_PASSWORD": "password",
                "API_KEY": "test-api-key-16char",
                "JWT_SECRET": "super-secret-jwt-key-that-is-very-long-32-chars",
                "DEFAULT_VECTOR_WEIGHT": "0.7001",  # Within 0.001 tolerance
                "DEFAULT_GRAPH_WEIGHT": "0.2999",
            },
        ):
            from config import Settings

            settings = Settings()
            assert (
                abs(
                    settings.DEFAULT_VECTOR_WEIGHT + settings.DEFAULT_GRAPH_WEIGHT - 1.0
                )
                <= 0.001
            )

    def test_jwt_secret_validation_success(self):
        """Test successful JWT secret validation"""
        with patch.dict(
            os.environ,
            {
                "NEO4J_URI": "neo4j://localhost:7687",
                "NEO4J_USERNAME": "neo4j",
                "NEO4J_PASSWORD": "password",
                "API_KEY": "test-api-key-16char",
                "JWT_SECRET": "this-is-a-very-long-jwt-secret-key-with-32-characters",
            },
        ):
            from config import Settings

            settings = Settings()
            assert len(settings.JWT_SECRET) >= 32

    def test_jwt_secret_validation_too_short(self):
        """Test JWT secret validation failure when too short"""
        with patch.dict(
            os.environ,
            {
                "NEO4J_URI": "neo4j://localhost:7687",
                "NEO4J_USERNAME": "neo4j",
                "NEO4J_PASSWORD": "password",
                "API_KEY": "test-api-key-16char",
                "JWT_SECRET": "short",  # Less than 32 characters
            },
        ):
            from config import Settings

            with pytest.raises(ValidationError) as exc_info:
                Settings()

            assert "JWT_SECRET must be at least 32 characters long" in str(
                exc_info.value
            )

    def test_jwt_secret_validation_empty(self):
        """Test JWT secret validation failure when empty"""
        with patch.dict(
            os.environ,
            {
                "NEO4J_URI": "neo4j://localhost:7687",
                "NEO4J_USERNAME": "neo4j",
                "NEO4J_PASSWORD": "password",
                "API_KEY": "test-api-key-16char",
                "JWT_SECRET": "",
            },
        ):
            from config import Settings

            with pytest.raises(ValidationError) as exc_info:
                Settings()

            assert "JWT_SECRET must be at least 32 characters long" in str(
                exc_info.value
            )

    def test_api_key_validation_success(self):
        """Test successful API key validation"""
        with patch.dict(
            os.environ,
            {
                "NEO4J_URI": "neo4j://localhost:7687",
                "NEO4J_USERNAME": "neo4j",
                "NEO4J_PASSWORD": "password",
                "API_KEY": "valid-api-key-16chars",
                "JWT_SECRET": "super-secret-jwt-key-that-is-very-long-32-chars",
            },
        ):
            from config import Settings

            settings = Settings()
            assert len(settings.API_KEY) >= 16

    def test_api_key_validation_too_short(self):
        """Test API key validation failure when too short"""
        with patch.dict(
            os.environ,
            {
                "NEO4J_URI": "neo4j://localhost:7687",
                "NEO4J_USERNAME": "neo4j",
                "NEO4J_PASSWORD": "password",
                "API_KEY": "short",  # Less than 16 characters
                "JWT_SECRET": "super-secret-jwt-key-that-is-very-long-32-chars",
            },
        ):
            from config import Settings

            with pytest.raises(ValidationError) as exc_info:
                Settings()

            assert "API_KEY must be at least 16 characters long" in str(exc_info.value)

    def test_api_key_validation_empty(self):
        """Test API key validation failure when empty"""
        with patch.dict(
            os.environ,
            {
                "NEO4J_URI": "neo4j://localhost:7687",
                "NEO4J_USERNAME": "neo4j",
                "NEO4J_PASSWORD": "password",
                "API_KEY": "",
                "JWT_SECRET": "super-secret-jwt-key-that-is-very-long-32-chars",
            },
        ):
            from config import Settings

            with pytest.raises(ValidationError) as exc_info:
                Settings()

            assert "API_KEY must be at least 16 characters long" in str(exc_info.value)

    def test_required_fields_missing(self):
        """Test validation error when required fields are missing"""
        # Test missing NEO4J_URI
        with patch.dict(
            os.environ,
            {
                "NEO4J_USERNAME": "neo4j",
                "NEO4J_PASSWORD": "password",
                "API_KEY": "test-api-key-16char",
                "JWT_SECRET": "super-secret-jwt-key-that-is-very-long-32-chars",
            },
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
            "API_KEY": "test-api-key-16char",
            "JWT_SECRET": "super-secret-jwt-key-that-is-very-long-32-chars",
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

    def test_field_constraints_vector_size(self):
        """Test vector size constraints"""
        base_env = {
            "NEO4J_URI": "neo4j://localhost:7687",
            "NEO4J_USERNAME": "neo4j",
            "NEO4J_PASSWORD": "password",
            "API_KEY": "test-api-key-16char",
            "JWT_SECRET": "super-secret-jwt-key-that-is-very-long-32-chars",
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

    def test_field_constraints_cache_ttl(self):
        """Test cache TTL constraints"""
        base_env = {
            "NEO4J_URI": "neo4j://localhost:7687",
            "NEO4J_USERNAME": "neo4j",
            "NEO4J_PASSWORD": "password",
            "API_KEY": "test-api-key-16char",
            "JWT_SECRET": "super-secret-jwt-key-that-is-very-long-32-chars",
        }

        # Test minimum cache TTL
        with patch.dict(os.environ, {**base_env, "CACHE_TTL": "60"}):
            from config import Settings

            settings = Settings()
            assert settings.CACHE_TTL == 60

        # Test maximum cache TTL
        with patch.dict(os.environ, {**base_env, "CACHE_TTL": "86400"}):
            from config import Settings

            settings = Settings()
            assert settings.CACHE_TTL == 86400

    def test_weight_constraints(self):
        """Test weight field constraints"""
        base_env = {
            "NEO4J_URI": "neo4j://localhost:7687",
            "NEO4J_USERNAME": "neo4j",
            "NEO4J_PASSWORD": "password",
            "API_KEY": "test-api-key-16char",
            "JWT_SECRET": "super-secret-jwt-key-that-is-very-long-32-chars",
        }

        # Test minimum weights
        with patch.dict(
            os.environ,
            {**base_env, "DEFAULT_VECTOR_WEIGHT": "0.0", "DEFAULT_GRAPH_WEIGHT": "1.0"},
        ):
            from config import Settings

            settings = Settings()
            assert settings.DEFAULT_VECTOR_WEIGHT == 0.0
            assert settings.DEFAULT_GRAPH_WEIGHT == 1.0

        # Test maximum weights
        with patch.dict(
            os.environ,
            {**base_env, "DEFAULT_VECTOR_WEIGHT": "1.0", "DEFAULT_GRAPH_WEIGHT": "0.0"},
        ):
            from config import Settings

            settings = Settings()
            assert settings.DEFAULT_VECTOR_WEIGHT == 1.0
            assert settings.DEFAULT_GRAPH_WEIGHT == 0.0

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
            "API_KEY": "test-api-key-16char",
            "JWT_SECRET": "super-secret-jwt-key-that-is-very-long-32-chars",
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
                {
                    **base_env,
                    "DEBUG": str_val,
                    "CACHE_ENABLED": str_val,
                    "QDRANT_PREFER_GRPC": str_val,
                },
            ):
                from config import Settings

                settings = Settings()
                assert settings.DEBUG == expected
                assert settings.CACHE_ENABLED == expected
                assert settings.QDRANT_PREFER_GRPC == expected

    def test_settings_singleton_behavior(self):
        """Test settings singleton instantiation"""
        from config import settings

        # Settings should be instantiated and accessible
        assert settings is not None
        assert settings.SERVICE_NAME == "cv-search-service"

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

    def test_all_field_types(self):
        """Test all field types are handled correctly"""
        from config import settings

        # String fields
        assert isinstance(settings.SERVICE_NAME, str)
        assert isinstance(settings.LOG_LEVEL, str)
        assert isinstance(settings.NEO4J_URI, str)
        assert isinstance(settings.NEO4J_USERNAME, str)
        assert isinstance(settings.NEO4J_PASSWORD, str)
        assert isinstance(settings.NEO4J_DATABASE, str)
        assert isinstance(settings.QDRANT_HOST, str)
        assert isinstance(settings.QDRANT_COLLECTION, str)
        assert isinstance(settings.EMBEDDING_MODEL, str)
        assert isinstance(settings.API_KEY, str)
        assert isinstance(settings.JWT_SECRET, str)
        assert isinstance(settings.JWT_ALGORITHM, str)
        assert isinstance(settings.RATE_LIMIT_SEARCH, str)
        assert isinstance(settings.RATE_LIMIT_SUGGEST, str)

        # Integer fields
        assert isinstance(settings.PORT, int)
        assert isinstance(settings.NEO4J_MAX_CONNECTION_LIFETIME, int)
        assert isinstance(settings.NEO4J_MAX_CONNECTION_POOL_SIZE, int)
        assert isinstance(settings.NEO4J_CONNECTION_TIMEOUT, int)
        assert isinstance(settings.QDRANT_PORT, int)
        assert isinstance(settings.QDRANT_TIMEOUT, int)
        assert isinstance(settings.VECTOR_SIZE, int)
        assert isinstance(settings.CACHE_TTL, int)

        # Float fields
        assert isinstance(settings.DEFAULT_VECTOR_WEIGHT, float)
        assert isinstance(settings.DEFAULT_GRAPH_WEIGHT, float)

        # Boolean fields
        assert isinstance(settings.DEBUG, bool)
        assert isinstance(settings.QDRANT_PREFER_GRPC, bool)
        assert isinstance(settings.CACHE_ENABLED, bool)

    def test_validator_functions_directly(self):
        """Test validator functions directly"""
        from config import Settings

        # Test Neo4j password validator
        result = Settings.validate_neo4j_password("valid_password")
        assert result == "valid_password"

        result = Settings.validate_neo4j_password("  spaced_password  ")
        assert result == "spaced_password"

        with pytest.raises(ValueError):
            Settings.validate_neo4j_password("")

        with pytest.raises(ValueError):
            Settings.validate_neo4j_password("   ")

        # Test JWT secret validator
        result = Settings.validate_jwt_secret("this-is-a-very-long-jwt-secret-32-chars")
        assert len(result) >= 32

        with pytest.raises(ValueError):
            Settings.validate_jwt_secret("short")

        # Test API key validator
        result = Settings.validate_api_key("valid-api-key-16chars")
        assert len(result) >= 16

        with pytest.raises(ValueError):
            Settings.validate_api_key("short")

        # Test weights validator
        result = Settings.validate_weights_sum(0.3, {"DEFAULT_VECTOR_WEIGHT": 0.7})
        assert result == 0.3

        with pytest.raises(ValueError):
            Settings.validate_weights_sum(0.5, {"DEFAULT_VECTOR_WEIGHT": 0.7})
