import uuid
from django.conf import settings


from django.core.validators import MinLengthValidator
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse

import numpy as np


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

    # Protocol 2: all but 1 field with Dice score > 0.7x
    THRESHOLD = 0.6
    return sum(dice > THRESHOLD for dice in dices) >= len(dices) - 1


class Tag(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class Source(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name

    @property
    def color(self):
        # Create a gradient from cd4610 to  0f4c81, and pick a color based on the pk rank
        pks = list(Source.objects.all().values_list("pk", flat=True))
        FROM = 0xCD4610
        TO = 0x0F4C81
        print(pks.index(self.pk) // len(pks))
        return f"#{int(FROM + (TO - FROM) * (pks.index(self.pk) // len(pks))):06x}"


class Dataset(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)

    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    tags = models.ManyToManyField(Tag, blank=True)
    source = models.ForeignKey(Source, on_delete=models.CASCADE, null=True, blank=True)

    disease = models.ForeignKey(
        "prevalence.Disease", on_delete=models.CASCADE, null=True, blank=True
    )

    public = models.BooleanField(default=True)

    organization = models.ForeignKey(
        "accounts.Organization", on_delete=models.CASCADE, null=True, blank=True
    )
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    api_token = models.CharField(max_length=36, default=uuid.uuid4, editable=False)

    to_delete = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    def find_matching_patient(self, submission):
        for patient in self.datasetpatient_set.all():
            if patient.submission_set.first() and are_similar(
                patient.submission_set.first(), submission
            ):
                return patient
        return None

    def create_patient(self, submission):
        patient = DatasetPatient.objects.create(dataset=self)
        submission.dataset_patient = patient
        submission.save()

    def get_absolute_url(self):
        return reverse("dataset_detail", kwargs={"pk": self.pk})

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


class Run(models.Model):
    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)


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

    disease = models.ForeignKey(
        "prevalence.Disease", on_delete=models.CASCADE, null=True
    )

    #
    # Tokens
    #

    # Required fields
    first_name_token = models.CharField(
        max_length=1024,
        validators=[MinLengthValidator(1024)],
        verbose_name="First name",
    )
    last_name_token = models.CharField(
        max_length=1024,
        validators=[MinLengthValidator(1024)],
        verbose_name="Last name",
    )
    date_of_birth_token = models.CharField(
        max_length=1024,
        validators=[MinLengthValidator(1024)],
        verbose_name="Date of birth",
        help_text="YYYY-MM-DD",
    )

    # Optional fields
    middle_name_token = models.CharField(
        max_length=1024,
        blank=True,
        validators=[MinLengthValidator(1024)],
        verbose_name="Middle name",
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

    sex_at_birth_token = models.CharField(
        max_length=1024,
        blank=False,
        validators=[MinLengthValidator(1024)],
        verbose_name="Sex at birth",
        help_text="M or F",
    )

    city_at_birth_token = models.CharField(
        max_length=1024,
        blank=True,
        validators=[MinLengthValidator(1024)],
        verbose_name="City at birth",
        help_text="City name",
    )
    zip_code_at_birth_token = models.CharField(
        max_length=1024,
        blank=True,
        validators=[MinLengthValidator(1024)],
        verbose_name="Zip code at birth",
        help_text="Zip code",
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
        try:
            return f"Submission {self.id} for {self.dataset_patient.public_id.url()}"
        except:
            return f"Submission {self.id} without dataset_patient"


class GlobalPatient(models.Model):
    pass
