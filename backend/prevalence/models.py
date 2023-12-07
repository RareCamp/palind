from django.db import models


class GlobalStats(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    n_diseases = models.PositiveIntegerField(default=0)
    n_contributors = models.PositiveIntegerField(default=0)
    n_patients = models.PositiveIntegerField(default=0)


class PatientsBySource(models.Model):
    global_stats = models.ForeignKey(GlobalStats, on_delete=models.CASCADE)

    source = models.CharField(max_length=200)
    n_patients = models.PositiveIntegerField(default=0)


class Disease(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class URLSource(models.Model):
    disease = models.ForeignKey(Disease, on_delete=models.CASCADE)
    
    name = models.CharField(max_length=200)
    url = models.URLField(max_length=200)

    def __str__(self):
        return self.name


class DiseaseStats(models.Model):
    disease = models.ForeignKey(Disease, on_delete=models.CASCADE)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    n_contributors = models.PositiveIntegerField(default=0)
    n_patients = models.PositiveIntegerField(default=0)

    confidence = models.CharField(
        max_length=20, choices=[("low", "low"), ("medium", "medium"), ("high", "high")]
    )
