from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from datasets.models import Dataset


from .managers import CustomUserManager


class Organization(models.Model):
    name = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class CustomUser(AbstractUser):
    username = None
    email = models.EmailField("email address", unique=True)
    picture = models.ImageField(upload_to="profile_pictures", null=True, blank=True)
    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, related_name="users", null=True
    )

    default_dataset = models.ForeignKey(
        Dataset, on_delete=models.SET_NULL, null=True, blank=True
    )

    is_prevalence_counting_user = models.BooleanField(default=False)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.email

    def full_name(self):
        if self.first_name == "" and self.last_name == "":
            return self.email
        return f"{self.first_name} {self.last_name}"

    class Meta:
        verbose_name = "User"


@receiver(post_save, sender=CustomUser)
def create_default_dataset(sender, instance, created, **kwargs):
    if instance.default_dataset is None:
        instance.default_dataset = Dataset.objects.create(
            name="Default dataset",
            description="Dataset for prevalence counting.",
            created_by=instance,
        )
        instance.save()
