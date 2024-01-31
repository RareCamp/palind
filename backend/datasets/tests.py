from django.test import TestCase, Client


from accounts.models import CustomUser as User
from prevalence.models import Disease

from .models import Dataset, Submission, DatasetPatient, TOKEN_LENGTH


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


from django.core.exceptions import ValidationError


class TestSubmissionModel(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(email="test@test.com", password="test")
        self.dataset = Dataset.objects.create(name="Test Dataset", created_by=self.user)
        self.dataset_patient = DatasetPatient.objects.create(dataset=self.dataset)
        self.disease = Disease.objects.create(name="Test Disease")

    def test_submission_with_invalid_tokens(self):
        invalid_tokens = [
            "0" * (TOKEN_LENGTH - 1),  # Too short
            "1" * (TOKEN_LENGTH + 1),  # Too long
            "2" * TOKEN_LENGTH,  # Contains invalid character
            "a" * TOKEN_LENGTH,  # Contains invalid character
            "01" * (TOKEN_LENGTH // 2) + "a",  # Contains invalid character
        ]

        for token in invalid_tokens:
            with self.assertRaises(ValidationError):
                submission = Submission(
                    protocol_version="1.0.0",
                    disease=self.disease,
                    dataset=self.dataset,
                    dataset_patient=self.dataset_patient,
                    first_name_token=token,
                    last_name_token=token,
                    date_of_birth_token=token,
                    sex_at_birth_token=token,
                )
                submission.full_clean()

    def test_submission_with_valid_token(self):
        valid_token = "0" * 512 + "1" * 512  # Correct token format

        submission = Submission(
            protocol_version="1.0.0",
            disease=self.disease,
            dataset=self.dataset,
            dataset_patient=self.dataset_patient,
            first_name_token=valid_token,
            last_name_token=valid_token,
            date_of_birth_token=valid_token,
            sex_at_birth_token=valid_token,
        )
        try:
            submission.full_clean()
        except ValidationError:
            self.fail("Submission with valid token should not raise ValidationError")
