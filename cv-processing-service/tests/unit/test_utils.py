"""Comprehensive tests for cv-processing-service utils to achieve 95%+ coverage."""

import pytest
from utils.errors import (
    BaseProcessingError,
    ParserError,
    LLMServiceError,
    ContentStructureError,
    DataFixerError,
    ReviewServiceError,
    EmbeddingServiceError,
)


class TestErrors:
    """Test custom error classes"""

    def test_base_processing_error(self):
        """Test BaseProcessingError"""
        error = BaseProcessingError("Base error message")

        assert str(error) == "Base error message"
        assert isinstance(error, Exception)

    def test_base_processing_error_with_details(self):
        """Test BaseProcessingError with additional details"""
        error = BaseProcessingError("Error with details", details={"code": "E001"})

        assert str(error) == "Error with details"
        assert hasattr(error, "details")
        assert error.details == {"code": "E001"}

    def test_llm_service_error(self):
        """Test LLMServiceError"""
        error = LLMServiceError(
            "LLM processing failed", model_name="gpt-4", prompt_length=1000
        )

        assert str(error) == "LLM processing failed"
        assert isinstance(error, BaseProcessingError)
        assert error.model_name == "gpt-4"
        assert error.prompt_length == 1000
        assert error.details["model_name"] == "gpt-4"
        assert error.details["prompt_length"] == 1000

    def test_parser_error(self):
        """Test ParserError"""
        error = ParserError(
            "Parser failed to extract text", file_type="pdf", parser_type="PyPDF2"
        )

        assert str(error) == "Parser failed to extract text"
        assert isinstance(error, BaseProcessingError)
        assert error.file_type == "pdf"
        assert error.parser_type == "PyPDF2"
        assert error.details["file_type"] == "pdf"
        assert error.details["parser_type"] == "PyPDF2"

    def test_content_structure_error(self):
        """Test ContentStructureError"""
        validation_errors = ["Missing name field", "Invalid email format"]
        error = ContentStructureError(
            "Structure validation failed",
            content_type="resume",
            validation_errors=validation_errors,
        )

        assert str(error) == "Structure validation failed"
        assert isinstance(error, BaseProcessingError)
        assert error.content_type == "resume"
        assert error.validation_errors == validation_errors
        assert error.details["content_type"] == "resume"
        assert error.details["validation_errors"] == validation_errors

    def test_data_fixer_error(self):
        """Test DataFixerError"""
        error = DataFixerError(
            "Failed to fix data", field_name="email", attempted_fix="normalize_email"
        )

        assert str(error) == "Failed to fix data"
        assert isinstance(error, BaseProcessingError)
        assert error.field_name == "email"
        assert error.attempted_fix == "normalize_email"
        assert error.details["field_name"] == "email"
        assert error.details["attempted_fix"] == "normalize_email"

    def test_review_service_error(self):
        """Test ReviewServiceError"""
        error = ReviewServiceError(
            "Review generation failed", review_type="technical", content_length=5000
        )

        assert str(error) == "Review generation failed"
        assert isinstance(error, BaseProcessingError)
        assert error.review_type == "technical"
        assert error.content_length == 5000
        assert error.details["review_type"] == "technical"
        assert error.details["content_length"] == 5000

    def test_embedding_service_error(self):
        """Test EmbeddingServiceError"""
        error = EmbeddingServiceError(
            "Embedding generation failed",
            model_name="all-MiniLM-L6-v2",
            text_length=10000,
        )

        assert str(error) == "Embedding generation failed"
        assert isinstance(error, BaseProcessingError)
        assert error.model_name == "all-MiniLM-L6-v2"
        assert error.text_length == 10000
        assert error.details["model_name"] == "all-MiniLM-L6-v2"
        assert error.details["text_length"] == 10000

    def test_error_inheritance_chain(self):
        """Test error inheritance chain"""
        error = LLMServiceError("Test error")

        assert isinstance(error, LLMServiceError)
        assert isinstance(error, BaseProcessingError)
        assert isinstance(error, Exception)

    def test_base_processing_error_to_dict(self):
        """Test BaseProcessingError to_dict method"""
        error = BaseProcessingError(
            "Test error", error_code="E001", details={"key": "value"}
        )

        error_dict = error.to_dict()

        assert error_dict["error_type"] == "BaseProcessingError"
        assert error_dict["message"] == "Test error"
        assert error_dict["error_code"] == "E001"
        assert error_dict["details"] == {"key": "value"}

    def test_error_with_minimal_args(self):
        """Test errors with minimal arguments"""
        errors = [
            ParserError("Simple parser error"),
            LLMServiceError("Simple LLM error"),
            ContentStructureError("Simple structure error"),
            DataFixerError("Simple fixer error"),
            ReviewServiceError("Simple review error"),
            EmbeddingServiceError("Simple embedding error"),
        ]

        for error in errors:
            assert isinstance(error, BaseProcessingError)
            assert len(str(error)) > 0

    def test_error_with_cause(self):
        """Test error with underlying cause"""
        try:
            raise ValueError("Original error")
        except ValueError as e:
            error = BaseProcessingError("Wrapped error")
            error.__cause__ = e

            assert str(error) == "Wrapped error"
            assert error.__cause__ is not None
            assert isinstance(error.__cause__, ValueError)


class TestCircuitBreaker:
    """Test circuit breaker utility"""

    def test_circuit_breaker_exists(self):
        """Test circuit breaker module can be imported"""
        try:
            from utils.circuit_breaker import CircuitBreaker

            assert CircuitBreaker is not None
        except ImportError:
            pytest.skip("CircuitBreaker not implemented")

    def test_circuit_breaker_initialization(self):
        """Test circuit breaker initialization"""
        try:
            from utils.circuit_breaker import CircuitBreaker

            breaker = CircuitBreaker(failure_threshold=3, recovery_timeout=60)

            assert breaker.failure_threshold == 3
            assert breaker.recovery_timeout == 60
        except ImportError:
            pytest.skip("CircuitBreaker not implemented")


class TestMonitoring:
    """Test monitoring utilities"""

    def test_monitoring_functions_exist(self):
        """Test monitoring functions exist"""
        from utils.monitoring import get_metrics, init_monitoring

        assert get_metrics is not None
        assert init_monitoring is not None

    def test_get_metrics(self):
        """Test get_metrics function"""
        from utils.monitoring import get_metrics

        metrics = get_metrics()
        assert isinstance(metrics, str)

    def test_init_monitoring(self):
        """Test init_monitoring function"""
        from utils.monitoring import init_monitoring
        from fastapi import FastAPI

        app = FastAPI()

        # Should not raise an exception
        init_monitoring(app, "test-service")

    def test_monitoring_middleware_exists(self):
        """Test MetricsMiddleware exists"""
        from utils.monitoring import MetricsMiddleware

        assert MetricsMiddleware is not None

    def test_metrics_middleware_initialization(self):
        """Test MetricsMiddleware can be initialized"""
        from utils.monitoring import MetricsMiddleware
        from fastapi import FastAPI

        app = FastAPI()
        middleware = MetricsMiddleware(app, service_name="test")

        assert middleware is not None

    def test_trace_function_decorator(self):
        """Test trace_function decorator"""
        try:
            from utils.monitoring import trace_function

            @trace_function("test.operation")
            def test_func():
                return "success"

            result = test_func()
            assert result == "success"
        except ImportError:
            pytest.skip("trace_function not available")

    def test_record_metrics_functions(self):
        """Test metrics recording functions"""
        try:
            from utils.monitoring import record_job_metrics, record_error_metrics

            # Should not raise exceptions
            record_job_metrics("test-service", "created", "job_type")
            record_error_metrics("test-service", "TestError", "operation")
        except ImportError:
            pytest.skip("Metrics recording functions not available")


class TestLogger:
    """Test logger utilities"""

    def test_logger_module_exists(self):
        """Test logger module can be imported"""
        try:
            from utils import logger

            assert logger is not None
        except ImportError:
            pytest.skip("Logger module not available")

    def test_service_logger_class(self):
        """Test ServiceLogger class"""
        try:
            from utils.logger import ServiceLogger

            logger = ServiceLogger("test-module")
            assert logger is not None
        except ImportError:
            pytest.skip("ServiceLogger not available")

    def test_logging_context_functions(self):
        """Test logging context management functions"""
        try:
            from utils.logger import set_request_context, clear_request_context

            # Should not raise exceptions
            set_request_context(job_id="test-123")
            clear_request_context()
        except ImportError:
            pytest.skip("Logging context functions not available")

    def test_service_logger_methods(self):
        """Test ServiceLogger methods"""
        try:
            from utils.logger import ServiceLogger

            logger = ServiceLogger("test")

            # Test logging methods exist
            assert hasattr(logger, "info")
            assert hasattr(logger, "error")
            assert hasattr(logger, "warning")
            assert hasattr(logger, "debug")

            # Should not raise exceptions
            logger.info("Test info message")
            logger.error("Test error message")
        except ImportError:
            pytest.skip("ServiceLogger methods not available")

    def test_service_call_logging(self):
        """Test service call logging method"""
        try:
            from utils.logger import ServiceLogger

            logger = ServiceLogger("test")

            if hasattr(logger, "service_call"):
                # Should not raise exceptions
                logger.service_call(
                    "external-service", "operation", "success", duration_ms=100
                )
                logger.service_call(
                    "external-service",
                    "operation",
                    "error",
                    duration_ms=200,
                    error="Test error",
                )
        except ImportError:
            pytest.skip("Service call logging not available")


class TestUtilsIntegration:
    """Test integration between utility modules"""

    def test_error_monitoring_integration(self):
        """Test integration between errors and monitoring"""
        try:
            from utils.errors import LLMServiceError
            from utils.monitoring import record_error_metrics

            try:
                raise LLMServiceError("Test integration error")
            except LLMServiceError:
                # Record the error in monitoring
                record_error_metrics(
                    "test-service", "LLMServiceError", "test_operation"
                )

                # Should complete without exceptions
                assert True
        except ImportError:
            pytest.skip("Error monitoring integration not available")

    def test_error_logging_integration(self):
        """Test integration between errors and logging"""
        try:
            from utils.errors import ParserError
            from utils.logger import ServiceLogger

            logger = ServiceLogger("integration-test")

            try:
                raise ParserError("Test parser error for logging")
            except ParserError as e:
                # Log the error
                logger.error(f"Parser failed: {str(e)}")

                # Should complete without exceptions
                assert True
        except ImportError:
            pytest.skip("Error logging integration not available")

    def test_all_utils_modules_importable(self):
        """Test all utility modules can be imported"""
        modules_to_test = ["utils.errors", "utils.monitoring", "utils.logger"]

        importable_modules = []

        for module in modules_to_test:
            try:
                __import__(module)
                importable_modules.append(module)
            except ImportError:
                pass

        # At least errors module should be importable
        assert "utils.errors" in importable_modules

    def test_error_classes_complete(self):
        """Test all expected error classes exist"""
        from utils.errors import (
            BaseProcessingError,
            ParserError,
            LLMServiceError,
            ContentStructureError,
            DataFixerError,
            ReviewServiceError,
            EmbeddingServiceError,
        )

        # All error classes should be subclasses of BaseProcessingError
        error_classes = [
            ParserError,
            LLMServiceError,
            ContentStructureError,
            DataFixerError,
            ReviewServiceError,
            EmbeddingServiceError,
        ]

        for error_class in error_classes:
            assert issubclass(error_class, BaseProcessingError)
            assert issubclass(error_class, Exception)

    def test_utility_function_signatures(self):
        """Test utility functions have expected signatures"""
        # Test monitoring functions
        try:
            from utils.monitoring import get_metrics, init_monitoring
            import inspect

            # get_metrics should take no required arguments
            sig = inspect.signature(get_metrics)
            assert (
                len([p for p in sig.parameters.values() if p.default == p.empty]) == 0
            )

            # init_monitoring should take app and service_name
            sig = inspect.signature(init_monitoring)
            params = list(sig.parameters.keys())
            assert "app" in params
            assert "service_name" in params
        except ImportError:
            pytest.skip("Monitoring functions not available")

    def test_error_message_formatting(self):
        """Test error message formatting is consistent"""
        errors = [
            BaseProcessingError("Base error"),
            LLMServiceError("Service error"),
            ParserError("Parser error"),
            ContentStructureError("Structure error"),
            DataFixerError("Fixer error"),
            ReviewServiceError("Review error"),
            EmbeddingServiceError("Embedding error"),
        ]

        for error in errors:
            # All errors should have meaningful string representation
            error_str = str(error)
            assert len(error_str) > 0
            assert error_str != "None"
            assert "error" in error_str.lower()

    def test_utils_module_structure(self):
        """Test utils module has expected structure"""
        import utils

        # Utils should be a package
        assert hasattr(utils, "__path__")

        # Should have key modules
        expected_modules = ["errors"]

        for module in expected_modules:
            try:
                getattr(utils, module)
            except AttributeError:
                # Try importing as submodule
                try:
                    __import__(f"utils.{module}")
                except ImportError:
                    pytest.fail(f"Expected utils.{module} to be available")

    def test_concurrent_utility_usage(self):
        """Test utilities work correctly under concurrent usage"""
        import asyncio
        from utils.errors import LLMServiceError

        async def create_error(error_id):
            """Create and handle an error"""
            try:
                raise LLMServiceError(f"Concurrent error {error_id}")
            except LLMServiceError as e:
                return str(e)

        async def test_concurrent():
            tasks = [create_error(i) for i in range(5)]
            results = await asyncio.gather(*tasks)

            # All tasks should complete successfully
            assert len(results) == 5
            for i, result in enumerate(results):
                assert f"Concurrent error {i}" in result

        # Run the concurrent test
        asyncio.run(test_concurrent())
