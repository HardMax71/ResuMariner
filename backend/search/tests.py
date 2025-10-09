from django.test import Client, TestCase


class SearchAPITests(TestCase):
    """Verify that the public search routes expose the expected verbs."""

    def setUp(self) -> None:
        self.client = Client()

    def test_semantic_search_get_not_allowed(self) -> None:
        response = self.client.get("/search/semantic/")
        self.assertEqual(response.status_code, 405)

    def test_structured_search_get_not_allowed(self) -> None:
        response = self.client.get("/search/structured/")
        self.assertEqual(response.status_code, 405)

    def test_hybrid_search_get_not_allowed(self) -> None:
        response = self.client.get("/search/hybrid/")
        self.assertEqual(response.status_code, 405)
