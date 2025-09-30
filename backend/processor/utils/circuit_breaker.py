import logging

import httpx
import pybreaker
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)

# Default settings: 5 failures trigger open state, 60 seconds recovery timeout
http_circuit_breaker = pybreaker.CircuitBreaker(
    fail_max=5,
    reset_timeout=60,
    exclude=[httpx.InvalidURL],  # Don't trip on invalid URLs
    name="http_circuit_breaker",
)


class CircuitBreakerListener(pybreaker.CircuitBreakerListener):
    def state_change(self, cb, old_state, new_state):
        logger.warning(f"Circuit breaker {cb.name} changed from {old_state.name} to {new_state.name}")

    def failure(self, cb, exc):
        logger.warning(f"Circuit breaker {cb.name} registered failure: {exc}")

    def success(self, cb):
        logger.debug(f"Circuit breaker {cb.name} registered success")


http_circuit_breaker.add_listeners(CircuitBreakerListener())


@http_circuit_breaker
@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10),
    retry=retry_if_exception_type((httpx.RequestError, httpx.TimeoutException)),
)
async def resilient_http_call(client: httpx.AsyncClient, method: str, url: str, **kwargs) -> httpx.Response:
    """
    Make a resilient HTTP call with circuit breaker and retry logic.

    Args:
        client: The httpx AsyncClient instance
        method: HTTP method (GET, POST, etc.)
        url: Target URL
        **kwargs: Additional arguments to pass to the request

    Returns:
        httpx.Response object

    Raises:
        pybreaker.CircuitBreakerError: When circuit is open
        httpx.HTTPStatusError: When response status >= 400
        httpx.RequestError, httpx.TimeoutException: On network errors (will retry)
    """
    response = await client.request(method, url, **kwargs)
    if response.status_code >= 400:
        response.raise_for_status()
    return response


def get_circuit_breaker_status() -> dict:
    """
    Get the current status of the circuit breaker for monitoring.

    Returns:
        Dictionary with circuit breaker state and statistics
    """
    return {
        "name": http_circuit_breaker.name,
        "state": http_circuit_breaker.current_state,
        "fail_counter": http_circuit_breaker.fail_counter,
        "success_counter": http_circuit_breaker.success_counter,
        "fail_max": http_circuit_breaker.fail_max,
        "reset_timeout": http_circuit_breaker.reset_timeout,
    }


def create_custom_circuit_breaker(
    name: str, fail_max: int = 5, reset_timeout: int = 60, exclude: list | None = None
) -> pybreaker.CircuitBreaker:
    """
    Create a custom circuit breaker instance with specific settings.

    Args:
        name: Unique name for the circuit breaker
        fail_max: Maximum failures before opening circuit
        reset_timeout: Seconds before attempting to close circuit
        exclude: List of exceptions to exclude from failure counting

    Returns:
        Configured CircuitBreaker instance
    """
    cb = pybreaker.CircuitBreaker(name=name, fail_max=fail_max, reset_timeout=reset_timeout, exclude=exclude or [])
    cb.add_listeners(CircuitBreakerListener())
    return cb
