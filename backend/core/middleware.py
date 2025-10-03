import time

from core.metrics import REQUEST_COUNT, REQUEST_DURATION


class PrometheusMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Skip metrics endpoint to avoid recursion
        if request.path == "/metrics":
            return self.get_response(request)

        start_time = time.time()
        response = self.get_response(request)
        duration = time.time() - start_time

        endpoint = self._normalize_path(request.path)
        method = request.method

        REQUEST_DURATION.labels(method=method, endpoint=endpoint).observe(duration)
        REQUEST_COUNT.labels(method=method, endpoint=endpoint, status=response.status_code).inc()

        return response

    def _normalize_path(self, path: str) -> str:
        path = path.rstrip("/") or "/"
        # Limit to 100 chars to prevent cardinality explosion
        if len(path) > 100:
            path = path[:100] + "..."
        return path
