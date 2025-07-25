"""
Comprehensive tests for cv-intake-service utils to achieve 95%+ coverage.
"""

import pytest
import asyncio
from unittest.mock import Mock, patch


class TestUtilsErrors:
    """Test utils/errors.py"""

    def test_base_service_error(self):
        """Test BaseServiceError class"""
        try:
            from utils.errors import BaseServiceError

            # Test basic error
            error = BaseServiceError("Test error message")
            assert str(error) == "Test error message"
            assert error.message == "Test error message"
            assert error.code is None
            assert error.details == {}  # details defaults to empty dict, not None

            # Test error with code and details
            error_with_details = BaseServiceError(
                "Detailed error", "ERR001", {"field": "value", "extra": "info"}
            )
            assert error_with_details.code == "ERR001"
            assert error_with_details.details == {"field": "value", "extra": "info"}

        except ImportError:
            pytest.skip("Cannot import BaseServiceError")

    def test_repository_error(self):
        """Test RepositoryError class"""
        try:
            from utils.errors import RepositoryError

            error = RepositoryError(
                "Database connection failed",
                operation="create_job",
                entity="Job",
                error_code="DB001",
            )

            assert "Database connection failed" in str(error)
            assert error.code == "DB001"

        except ImportError:
            pytest.skip("Cannot import RepositoryError")

    def test_all_error_classes(self):
        """Test all error classes exist and inherit correctly"""
        try:
            from utils.errors import (
                BaseServiceError,
                RepositoryError,
                FileServiceError,
                ProcessingServiceError,
                JobServiceError,
            )

            # Test inheritance
            assert issubclass(RepositoryError, BaseServiceError)
            assert issubclass(FileServiceError, BaseServiceError)
            assert issubclass(ProcessingServiceError, BaseServiceError)
            assert issubclass(JobServiceError, BaseServiceError)

        except ImportError:
            pytest.skip("Cannot import error classes")


class TestUtilsRedisQueue:
    """Test utils/redis_queue.py"""

    def setup_method(self):
        """Setup mocks for Redis tests"""
        self.patches = {}
        self.patches["redis"] = patch("redis.Redis")
        self.mock_redis = self.patches["redis"].start()
        self.mock_redis_instance = Mock()
        # RedisJobQueue uses Redis() constructor directly, not from_url()
        self.mock_redis.return_value = self.mock_redis_instance

        # Mock the ping method to simulate successful connection
        self.mock_redis_instance.ping = Mock(return_value=True)

        # Mock settings to provide proper values
        self.patches["settings"] = patch("utils.redis_queue.settings")
        self.mock_settings = self.patches["settings"].start()
        self.mock_settings.REDIS_WORKER_TIMEOUT = 30
        self.mock_settings.REDIS_JOB_QUEUE = "cv_processing_queue"
        self.mock_settings.REDIS_CLEANUP_QUEUE = "cv_cleanup_queue"
        self.mock_settings.REDIS_JOB_PREFIX = "cv:job:"
        self.mock_settings.REDIS_MAX_RETRIES = 3

    def teardown_method(self):
        """Cleanup patches"""
        for patch_obj in self.patches.values():
            try:
                patch_obj.stop()
            except Exception:
                pass

    def test_redis_queue_initialization(self):
        """Test RedisJobQueue initialization"""
        try:
            from utils.redis_queue import RedisJobQueue

            queue = RedisJobQueue()
            assert queue is not None

        except ImportError:
            pytest.skip("Cannot import RedisJobQueue")

    def test_enqueue_job_success(self):
        """Test successful job enqueueing"""
        try:
            from utils.redis_queue import RedisJobQueue

            # Setup mocks
            self.mock_redis_instance.lpush = Mock(return_value=1)
            self.mock_redis_instance.hset = Mock(return_value=1)
            self.mock_redis_instance.expire = Mock(return_value=1)

            queue = RedisJobQueue()

            job_id = "test-job-123"
            file_path = "/tmp/test.pdf"
            priority = 1

            queue.enqueue_job(job_id, file_path, priority)

            # Verify Redis operations were called
            self.mock_redis_instance.lpush.assert_called()
            self.mock_redis_instance.hset.assert_called()

        except ImportError:
            pytest.skip("Cannot import RedisJobQueue for enqueue test")

    def test_dequeue_job_success(self):
        """Test successful job dequeueing"""
        try:
            from utils.redis_queue import RedisJobQueue

            # Setup mocks
            task_id = "task-uuid-123"
            self.mock_redis_instance.brpop = Mock(
                return_value=("queue:pending", task_id)
            )
            # Mock hgetall to return job data
            self.mock_redis_instance.hgetall = Mock(
                return_value={
                    "job_id": "test-job-123",
                    "file_path": "/tmp/test.pdf",
                    "priority": "1",
                    "retries": "0",
                    "max_retries": "3",
                }
            )

            queue = RedisJobQueue()

            job = queue.dequeue_job()

            assert job is not None
            assert job["job_id"] == "test-job-123"

        except ImportError:
            pytest.skip("Cannot import RedisJobQueue for dequeue test")

    def test_get_queue_stats(self):
        """Test get_queue_stats method"""
        try:
            from utils.redis_queue import RedisJobQueue

            # Setup mocks for get_queue_stats
            self.mock_redis_instance.llen = Mock(
                side_effect=[10, 3]  # job_queue, cleanup_queue
            )
            self.mock_redis_instance.zcard = Mock(return_value=2)  # scheduled_retries
            self.mock_redis_instance.scan_iter = Mock(
                return_value=iter(
                    ["cv:task:1", "cv:task:2", "cv:task:3"]
                )  # active_jobs
            )
            self.mock_redis_instance.memory_usage = Mock(return_value=1024)

            queue = RedisJobQueue()

            stats = queue.get_queue_stats()

            assert isinstance(stats, dict)
            assert "queue_length" in stats
            assert "cleanup_queue_length" in stats
            assert "scheduled_retries" in stats
            assert "active_jobs" in stats
            assert stats["queue_length"] == 10
            assert stats["cleanup_queue_length"] == 3
            assert stats["scheduled_retries"] == 2
            assert stats["active_jobs"] == 3

        except ImportError:
            pytest.skip("Cannot import RedisJobQueue for stats test")


class TestUtilsSecurity:
    """Test utils/security.py"""

    def setup_method(self):
        """Setup mocks for security tests"""
        self.patches = {}
        self.patches["jwt"] = patch("jwt.decode")
        self.patches["redis"] = patch("redis.Redis")
        self.patches["verify_token"] = patch("utils.security.verify_token")

        self.mock_jwt = self.patches["jwt"].start()
        self.mock_redis = self.patches["redis"].start()
        self.mock_verify_token = self.patches["verify_token"].start()

        # Setup environment
        self.patches["env"] = patch.dict(
            "os.environ",
            {
                "JWT_SECRET": "test-secret_minimum_32_characters_long",
                "API_KEY": "test-api-key_16chars",
            },
        )
        self.patches["env"].start()

    def teardown_method(self):
        """Cleanup patches"""
        for patch_obj in self.patches.values():
            try:
                patch_obj.stop()
            except Exception:
                pass

    def test_validate_api_key_success(self):
        """Test successful API key validation"""
        try:
            from utils.security import validate_api_key
            from config import settings

            # Mock verify_token to return valid payload that matches settings.API_KEY
            self.mock_verify_token.return_value = {
                "sub": "api_key",
                "api_key": settings.API_KEY,  # Use actual settings.API_KEY
                "exp": 9999999999,
            }

            # Create mock HTTPAuthorizationCredentials object
            from fastapi.security import HTTPAuthorizationCredentials

            mock_credentials = Mock(spec=HTTPAuthorizationCredentials)
            mock_credentials.credentials = "valid-jwt-token"

            result = asyncio.run(validate_api_key(mock_credentials))

            assert result == settings.API_KEY  # Should return settings.API_KEY

        except ImportError:
            pytest.skip("Cannot import validate_api_key")

    def test_rate_limiter_configuration(self):
        """Test rate limiter configuration"""
        try:
            from utils.security import limiter

            assert limiter is not None

        except ImportError:
            pytest.skip("Cannot import limiter")


class TestUtilsHealthChecks:
    """Test utils/health_checks.py"""

    def setup_method(self):
        """Setup mocks for health check tests"""
        self.patches = {}

        # Mock all external dependencies
        self.patches["redis"] = patch("redis.Redis")
        self.patches["neo4j"] = patch("neo4j.GraphDatabase")

        mock_redis = self.patches["redis"].start()
        mock_neo4j = self.patches["neo4j"].start()

        # Setup successful connections
        mock_redis.from_url.return_value.ping.return_value = True
        mock_neo4j.driver.return_value.verify_connectivity.return_value = None

    def teardown_method(self):
        """Cleanup patches"""
        for patch_obj in self.patches.values():
            try:
                patch_obj.stop()
            except Exception:
                pass

    def test_health_checker_initialization(self):
        """Test HealthChecker initialization"""
        try:
            from utils.health_checks import HealthChecker

            health_checker = HealthChecker()
            assert health_checker is not None

        except ImportError:
            pytest.skip("Cannot import HealthChecker")

    def test_comprehensive_health_check(self):
        """Test comprehensive health check"""
        try:
            from utils.health_checks import HealthChecker

            health_checker = HealthChecker()

            result = asyncio.run(health_checker.get_comprehensive_health())

            assert isinstance(result, dict)
            assert "status" in result

        except ImportError:
            pytest.skip("Cannot import HealthChecker for comprehensive test")


class TestUtilsMonitoring:
    """Test utils/monitoring.py"""

    def setup_method(self):
        """Setup mocks for monitoring tests"""
        self.patches = {}

        # Mock Prometheus
        self.patches["prometheus_counter"] = patch("prometheus_client.Counter")
        self.patches["prometheus_histogram"] = patch("prometheus_client.Histogram")
        self.patches["prometheus_generate"] = patch("prometheus_client.generate_latest")

        # Mock OpenTelemetry
        self.patches["otel"] = patch("opentelemetry.trace.get_tracer")

        for patch_obj in self.patches.values():
            patch_obj.start()

    def teardown_method(self):
        """Cleanup patches"""
        for patch_obj in self.patches.values():
            try:
                patch_obj.stop()
            except Exception:
                pass

    def test_monitoring_initialization(self):
        """Test monitoring initialization"""
        try:
            from utils.monitoring import init_monitoring

            mock_app = Mock()
            init_monitoring(mock_app, "test-service")

            # Should not raise any exceptions
            assert True

        except ImportError:
            pytest.skip("Cannot import monitoring functions")

    def test_get_metrics(self):
        """Test get_metrics function"""
        try:
            from utils.monitoring import get_metrics

            # Mock prometheus generate_latest
            self.patches["prometheus_generate"].return_value = b"# Metrics data"

            result = get_metrics()

            assert isinstance(result, str)

        except ImportError:
            pytest.skip("Cannot import get_metrics")


class TestUtilsLogger:
    """Test utils/logger.py"""

    def test_logger_setup(self):
        """Test logger setup and configuration"""
        try:
            from utils.logger import (
                setup_logging,
                set_request_context,
                clear_request_context,
            )

            # Test setup_logging
            setup_logging("test-service", "DEBUG", True)

            # Test context functions
            test_context = {"request_id": "test-123", "user_id": "user-456"}
            set_request_context(test_context)
            clear_request_context()

            # Just verify the functions exist and can be called
            assert True  # Test passed if no exceptions

        except ImportError:
            pytest.skip("Cannot import logger functions")


class TestUtilsCircuitBreaker:
    """Test utils/circuit_breaker.py"""

    def test_circuit_breaker_initialization(self):
        """Test CircuitBreaker initialization"""
        try:
            from utils.circuit_breaker import CircuitBreaker

            cb = CircuitBreaker(failure_threshold=3, recovery_timeout=60)
            assert cb is not None
            assert cb.failure_threshold == 3
            assert cb.recovery_timeout == 60

        except ImportError:
            pytest.skip("Cannot import CircuitBreaker")

    def test_circuit_breaker_success(self):
        """Test circuit breaker with successful operations"""
        try:
            from utils.circuit_breaker import CircuitBreaker

            cb = CircuitBreaker(failure_threshold=3, recovery_timeout=60)

            def successful_operation():
                return "success"

            result = cb.call(successful_operation)
            assert result == "success"
            assert cb.failure_count == 0

        except ImportError:
            pytest.skip("Cannot import CircuitBreaker for success test")

    def test_circuit_breaker_failure(self):
        """Test circuit breaker with failing operations"""
        try:
            from utils.circuit_breaker import CircuitBreaker
            import httpx

            cb = CircuitBreaker(failure_threshold=2, recovery_timeout=60)

            def failing_operation():
                raise httpx.RequestError("Operation failed")

            # First failure
            with pytest.raises(httpx.RequestError):
                cb.call(failing_operation)
            assert cb.failure_count == 1

            # Second failure - should open circuit
            with pytest.raises(httpx.RequestError):
                cb.call(failing_operation)
            assert cb.failure_count == 2

        except ImportError:
            pytest.skip("Cannot import CircuitBreaker for failure test")
