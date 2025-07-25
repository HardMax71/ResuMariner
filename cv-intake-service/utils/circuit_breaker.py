import logging
from typing import Any, Callable, Optional
from functools import wraps
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)
import httpx
from datetime import datetime, timedelta
from threading import Lock
from enum import Enum

logger = logging.getLogger(__name__)


class CircuitState(Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


class CircuitBreaker:
    """Circuit breaker implementation for service-to-service calls"""

    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: int = 60,
        expected_exception: tuple = (
            httpx.RequestError,
            httpx.TimeoutException,
            httpx.HTTPStatusError,
        ),
    ):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception
        self.failure_count = 0
        self.last_failure_time: Optional[datetime] = None
        self.state = CircuitState.CLOSED
        self._lock = Lock()

    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to attempt reset"""
        if self.state != CircuitState.OPEN:
            return False

        if self.last_failure_time is None:
            return True

        return datetime.now() - self.last_failure_time > timedelta(
            seconds=self.recovery_timeout
        )

    def _record_success(self):
        """Record successful call"""
        with self._lock:
            self.failure_count = 0
            self.state = CircuitState.CLOSED
            logger.info("Circuit breaker reset to CLOSED state")

    def _record_failure(self, exception: Exception):
        """Record failed call"""
        with self._lock:
            self.failure_count += 1
            self.last_failure_time = datetime.now()

            if self.failure_count >= self.failure_threshold:
                if self.state != CircuitState.OPEN:
                    self.state = CircuitState.OPEN
                    logger.warning(
                        f"Circuit breaker opened after {self.failure_count} failures"
                    )

    def call(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with circuit breaker protection"""

        # Check if circuit is open
        if self.state == CircuitState.OPEN:
            if not self._should_attempt_reset():
                logger.warning("Circuit breaker is OPEN, rejecting call")
                raise Exception("Circuit breaker is open")
            else:
                # Move to half-open state
                with self._lock:
                    self.state = CircuitState.HALF_OPEN
                    logger.info("Circuit breaker moved to HALF_OPEN state")

        try:
            # Execute the function
            result = func(*args, **kwargs)

            # Success - reset circuit breaker
            if self.state == CircuitState.HALF_OPEN:
                self._record_success()

            return result

        except self.expected_exception as e:
            # Expected failure - record and re-raise
            self._record_failure(e)
            logger.error(f"Circuit breaker recorded failure: {str(e)}")
            raise
        except Exception as e:
            # Unexpected exception - don't count towards circuit breaker
            logger.error(f"Unexpected exception in circuit breaker: {str(e)}")
            raise


def circuit_breaker(failure_threshold: int = 5, recovery_timeout: int = 60):
    """Decorator for applying circuit breaker pattern to functions"""

    def decorator(func: Callable) -> Callable:
        breaker = CircuitBreaker(failure_threshold, recovery_timeout)

        @wraps(func)
        async def wrapper(*args, **kwargs):
            return await breaker.call(func, *args, **kwargs)

        return wrapper

    return decorator


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10),
    retry=retry_if_exception_type((httpx.RequestError, httpx.TimeoutException)),
)
async def resilient_http_call(
    client: httpx.AsyncClient, method: str, url: str, **kwargs
) -> httpx.Response:
    """Make HTTP call with retry logic and proper error handling"""

    try:
        response = await client.request(method, url, **kwargs)

        # Check for HTTP errors
        if response.status_code >= 400:
            logger.error(
                f"HTTP {response.status_code} error for {method} {url}: {response.text}"
            )

            # Raise appropriate exception for different status codes
            if response.status_code >= 500:
                response.raise_for_status()
            elif response.status_code == 429:
                response.raise_for_status()
            else:
                # Client error - don't retry
                response.raise_for_status()

        return response

    except httpx.TimeoutException as e:
        logger.error(f"Timeout for {method} {url}: {str(e)}")
        raise
    except httpx.RequestError as e:
        logger.error(f"Request error for {method} {url}: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error for {method} {url}: {str(e)}")
        raise
