import csv
import sys

from django.core.management.base import BaseCommand
from django.db.models.functions import Length

import numpy as np
from faker import Faker


from prevalence.models import Disease


class Command(BaseCommand):
    help = "Create a randomized dataset for prevalence counting"

    def handle(self, *args, **options):
        diseases = (
            Disease.objects.exclude(OMIM__exact="")
            .annotate(name_len=Length("name"))
            .exclude(name__regex=r"\d")
            .filter(name_len__lt=15)
            .order_by("?")
        )

        faker = Faker()

        HEADER = [
                "disease_id",
                "first_name",
                "last_name",
                "date_of_birth",
                "middle_name",
                "sex_at_birth",
                "city_at_birth",
                "zip_code_at_birth",
                "address_at_bith",
                "state_at_birth",
                "country_at_birth",
            ]

        rows = []
        for disease in diseases:
            # Pick a random number of patients
            num_patients = 1 + 10 * np.random.poisson(1)

            for _ in range(num_patients):
                rows.append((
                        disease.OMIM,
                        faker.first_name(),
                        faker.last_name(),
                        faker.date_of_birth(),
                        faker.first_name(),
                        np.random.choice(["M", "F"]),
                        faker.city(),
                        faker.zipcode(),
                        faker.zipcode()[:5],
                        faker.street_address(),
                        faker.state_abbr(),
                        faker.country_code(representation="alpha-3"),
                ))
            
            if len(rows) > 100:
                break

        # Write first 20 rows to one file
        writer = csv.writer(open("patients1.csv", "w"))
        writer.writerow(HEADER)
        writer.writerows(rows[:20])

        # Write next 20 rows to another file
        writer = csv.writer(open("patients2.csv", "w"))
        writer.writerow(HEADER)
        writer.writerows(rows[20:40])