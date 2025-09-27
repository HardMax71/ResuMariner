"""Confirm storage-specific routes are not publicly exposed via this service."""

from django.test import Client, TestCase


class StorageRouteTests(TestCase):
    """Ensure requests to storage endpoints receive the expected HTTP status."""

    def setUp(self) -> None:
        self.client = Client()

    def test_upsert_resume_endpoint_not_registered(self) -> None:
        response = self.client.post("/storage/resume", data={})
        self.assertEqual(response.status_code, 404)

    def test_store_vectors_endpoint_not_registered(self) -> None:
        response = self.client.post("/storage/vectors", data={})
        self.assertEqual(response.status_code, 404)

    def test_delete_resume_endpoint_not_registered(self) -> None:
        response = self.client.delete("/storage/resume/sample-id/delete")
        self.assertEqual(response.status_code, 404)

