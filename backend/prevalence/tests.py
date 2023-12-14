import random
import string

from django.test import TestCase, Client

from accounts.models import Organization, CustomUser
from datasets.models import Dataset

from .models import Disease, DiseaseStats, GlobalStats, count_diseases_prevalence


class TestPrevalenceCounting(TestCase):
    def test_prevalence_count(self):
        client = Client()

        DISEASE_NAMES = string.ascii_uppercase
        PATIENTS_PER_DISEASE = 100

        N_ORGANIZATIONS = 5
        N_USERS_PER_ORGANIZATION = 2
        N_DATASETS_PER_USER = 2
        N_SUBMISSIONS_PER_DATASET = 20

        def random_token(length=1024):
            return "".join(random.choice("01") for _ in range(length))

        # Create random tokens for submissions
        tokens = {
            disease: [random_token() for _ in range(PATIENTS_PER_DISEASE)]
            for disease in DISEASE_NAMES
        }

        # Create diseases
        for letter in DISEASE_NAMES:
            Disease.objects.create(name=letter)

        # Create organizations
        for i in range(N_ORGANIZATIONS):
            organization = Organization.objects.create(name=f"Organization {i}")

            # Create users
            for j in range(N_USERS_PER_ORGANIZATION):
                user = CustomUser.objects.create(
                    email=f"user_{CustomUser.objects.count()}@test.com",
                    organization=organization,
                    is_prevalence_counting_user=True,
                )
                client.force_login(user)

                # Create datasets
                for k in range(N_DATASETS_PER_USER):
                    dataset = Dataset.objects.create(
                        name=f"Dataset {Dataset.objects.count()}",
                        created_by=user,
                        organization=organization,
                    )

                    # Create submissions
                    for l in range(N_SUBMISSIONS_PER_DATASET):
                        disease = random.choice(DISEASE_NAMES)
                        token = random.choice(tokens[disease])

                        reponse = client.post(
                            "/v2/submit/",
                            data={
                                "disease_id": disease,
                                "first_name_token": token,
                                "last_name_token": token,
                                "sex_at_birth_token": token,
                                "date_of_birth_token": token,
                            },
                            headers={"Authorization": f"Bearer {dataset.api_token}"},
                            content_type="application/json",
                        )
                        self.assertEqual(reponse.status_code, 200)

        # Count prevalence
        result = count_diseases_prevalence()
        print(result)

        print(GlobalStats.objects.all().values())

        for ds in DiseaseStats.objects.all():
            print(ds.disease.name, ds.n_contributors, ds.n_patients)
