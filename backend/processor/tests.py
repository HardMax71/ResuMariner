from django.test import Client, TestCase


class ProcessorAPIBasicTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_health_endpoint_responds(self):
        response = self.client.get("/api/v1/health/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "ok")

    def test_upload_requires_post(self):
        response = self.client.get("/api/v1/resumes/")
        self.assertEqual(response.status_code, 200)

    def test_cleanup_requires_post(self):
        response = self.client.get("/api/v1/resumes/cleanup/")
        self.assertEqual(response.status_code, 405)
