import uuid


from django.core.validators import MinLengthValidator
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

import numpy as np


class Organization(models.Model):
    name = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    users = models.ManyToManyField("auth.User")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "     Organization"


def dice(a, b) -> float:
    a = np.array([x == "1" for x in a])
    b = np.array([x == "1" for x in b])
    return 2 * (a & b).sum() / (a.sum() + b.sum())


def are_similar(a, b):
    token_fields = [
        f.name for f in Submission._meta.get_fields() if f.name.endswith("_token")
    ]
    pairs_of_tokens = [
        (getattr(a, field), getattr(b, field))
        for field in token_fields
        if getattr(a, field) != "" and getattr(b, field) != ""
    ]
    if len(pairs_of_tokens) == 0:
        return False

    dices = [dice(a, b).round(2) for a, b in pairs_of_tokens]
    # print(dices)

    # Protocol 2: all but 1 field with Dice score > 0.7x
    THRESHOLD = 0.6
    return sum(dice > THRESHOLD for dice in dices) >= len(dices) - 1


class Dataset(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)

    name = models.CharField(max_length=200)
    description = models.TextField()

    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    created_by = models.ForeignKey("auth.User", on_delete=models.CASCADE)

    api_token = models.CharField(max_length=36, default=uuid.uuid4, editable=False)

    def __str__(self):
        return self.name

    def find_matching_patient(self, submission):
        for patient in self.datasetpatient_set.all():
            if are_similar(patient.submission_set.first(), submission):
                return patient
        return None

    def create_patient(self, submission):
        patient = DatasetPatient.objects.create(dataset=self)
        submission.dataset_patient = patient
        submission.save()

    class Meta:
        verbose_name = "    Dataset"


class PublicID(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def url(self):
        return f"patientids.com/{self.id}"

    def __str__(self):
        return self.url()

    class Meta:
        verbose_name = "    Public ID"


class DatasetPatient(models.Model):
    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE)
    public_id = models.OneToOneField(PublicID, on_delete=models.CASCADE, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    global_patient = models.ForeignKey(
        "GlobalPatient", on_delete=models.CASCADE, null=True
    )

    def __str__(self):
        return self.public_id.url()


# Create a public ID for each dataset patient
@receiver(post_save, sender=DatasetPatient)
def create_public_id(sender, instance, created, **kwargs):
    if created:
        instance.public_id = PublicID.objects.create()
        instance.save()


class Submission(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)

    protocol_version = models.CharField(
        max_length=200,
        choices=[
            ("1.0.0", "1.0.0"),
        ],
    )

    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE)
    dataset_patient = models.ForeignKey(DatasetPatient, on_delete=models.CASCADE)

    # Tokens
    first_name_token = models.CharField(
        max_length=1024,
        blank=True,
        validators=[MinLengthValidator(1024)],
        verbose_name="First name",
    )
    middle_name_token = models.CharField(
        max_length=1024,
        blank=True,
        validators=[MinLengthValidator(1024)],
        verbose_name="Middle name",
    )
    last_name_token = models.CharField(
        max_length=1024,
        blank=True,
        validators=[MinLengthValidator(1024)],
        verbose_name="Last name",
    )
    full_name_token = models.CharField(
        max_length=1024,
        blank=True,
        validators=[MinLengthValidator(1024)],
        verbose_name="Full name",
    )

    first_name_soundex_token = models.CharField(
        max_length=1024,
        blank=True,
        validators=[MinLengthValidator(1024)],
        verbose_name="First name soundex",
    )
    last_name_soundex_token = models.CharField(
        max_length=1024,
        blank=True,
        validators=[MinLengthValidator(1024)],
        verbose_name="Last name soundex",
    )

    gender_token = models.CharField(
        max_length=1024,
        blank=True,
        validators=[MinLengthValidator(1024)],
        verbose_name="Gender",
        help_text="M or F",
    )

    date_of_birth_token = models.CharField(
        max_length=1024,
        blank=True,
        validators=[MinLengthValidator(1024)],
        verbose_name="Date of birth",
        help_text="YYYY-MM-DD",
    )

    city_at_birth_token = models.CharField(
        max_length=1024,
        blank=True,
        validators=[MinLengthValidator(1024)],
        verbose_name="City at birth",
        help_text="City name",
    )
    address_at_bith_token = models.CharField(
        max_length=1024,
        blank=True,
        validators=[MinLengthValidator(1024)],
        verbose_name="Address at birth",
        help_text="Street address",
    )
    state_at_birth_token = models.CharField(
        max_length=1024,
        blank=True,
        validators=[MinLengthValidator(1024)],
        verbose_name="State at birth",
        help_text="ISO 3166-2",
    )
    country_at_birth_token = models.CharField(
        max_length=1024,
        blank=True,
        validators=[MinLengthValidator(1024)],
        verbose_name="Country at birth",
        help_text="ISO 3166-1 alpha-3",
    )

    def __str__(self):
        return f"Submission {self.id} for {self.dataset_patient.public_id.url()}"


class GlobalPatient(models.Model):
    pass
