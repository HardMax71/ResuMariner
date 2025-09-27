"""Smoke tests for the processor API endpoints."""

from django.test import Client, TestCase


class ProcessorAPITests(TestCase):
    """Ensure processor routes respond with expected status codes."""

    def setUp(self) -> None:
        self.client = Client()

    def test_health_endpoint_returns_status(self) -> None:
        response = self.client.get("/api/v1/health/")

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload.get("service"), "resume-processing-api")
        self.assertEqual(payload.get("status"), "ok")

    def test_health_endpoint_includes_optional_sections(self) -> None:
        response = self.client.get("/api/v1/health/")

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertIn("queue", payload)
        self.assertIsInstance(payload["queue"], dict)
        self.assertIn("processing_config", payload)

    def test_upload_endpoint_disallows_get(self) -> None:
        response = self.client.get("/api/v1/upload/")
        self.assertEqual(response.status_code, 405)

    def test_cleanup_endpoint_disallows_get(self) -> None:
        response = self.client.get("/api/v1/jobs/cleanup/")
        self.assertEqual(response.status_code, 405)
