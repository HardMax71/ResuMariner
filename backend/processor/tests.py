from django.test import Client, TestCase


class ProcessorAPIBasicTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_resumes_collection_requires_file_for_post(self):
        response = self.client.post("/api/v1/resumes/")
        self.assertEqual(response.status_code, 400)

    def test_config_endpoint_responds(self):
        response = self.client.get("/api/v1/config/file-types/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn(".pdf", data)
        self.assertIn("media_type", data[".pdf"])
        self.assertEqual(data[".pdf"]["parser"], "pdf")
