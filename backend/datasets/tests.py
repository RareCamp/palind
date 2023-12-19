from django.test import TestCase, Client


from django.contrib.auth.models import User

from .models import Dataset


class TestSubmissionCreate(TestCase):
    def setUp(self):
        self.client = Client()

    def test_get(self):
        reponse = self.client.get("/v2/submit/")
        self.assertEqual(reponse.status_code, 405)  # 405 Method Not Allowed

    def test_post(self):
        reponse = self.client.post("/v2/submit/")
        self.assertEqual(reponse.status_code, 401)  # 401 Unauthorized

        # Post with invalid token
        reponse = self.client.post(
            "/v2/submit/",
            HTTP_AUTHORIZATION="Bearer 123",
            content_type="application/json",
        )
        self.assertEqual(reponse.status_code, 401)  # 401 Unauthorized
