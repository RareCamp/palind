import collections
import itertools

from django.db import models

from datasets.models import DatasetPatient, are_similar


class GlobalStats(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    n_diseases = models.PositiveIntegerField(default=0)
    n_contributors = models.PositiveIntegerField(default=0)
    n_patients = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "   Global Stats"
        verbose_name_plural = "   Global Stats"


class PatientsBySource(models.Model):
    global_stats = models.ForeignKey(GlobalStats, on_delete=models.CASCADE)

    source = models.CharField(max_length=200)
    n_patients = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = " Patients by Source"
        verbose_name_plural = " Patients by Source"


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

    class Meta:
        verbose_name = "URL Source"


class DiseaseStats(models.Model):
    disease = models.ForeignKey(Disease, on_delete=models.CASCADE)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    n_contributors = models.PositiveIntegerField(default=0)
    n_patients = models.PositiveIntegerField(default=0)

    confidence = models.CharField(
        max_length=20, choices=[("low", "low"), ("medium", "medium"), ("high", "high")]
    )

    class Meta:
        verbose_name = "  Disease Stats"
        verbose_name_plural = "  Disease Stats"


def count_diseases_prevalence():
    patients = collections.defaultdict(list)
    unique_patients = collections.defaultdict(list)
    contributors = collections.defaultdict(set)

    for p in DatasetPatient.objects.all():
        submission = p.submission_set.last()
        if submission.disease:
            patients[submission.disease].append(submission)

    for disease_name, disease_patients in patients.items():
        disease, _ = Disease.objects.get_or_create(name=disease_name)

        for p in disease_patients:
            contributors[disease_name].add(p.dataset.created_by.organization.pk)
            if not any(are_similar(p, up) for up in unique_patients[disease_name]):
                unique_patients[disease_name].append(p)

        DiseaseStats.objects.create(
            disease=disease,
            n_contributors=len(contributors[disease_name]),
            n_patients=len(unique_patients[disease_name]),
            confidence="low",  # TODO
        )

    gs = GlobalStats.objects.create(
        n_diseases=len(unique_patients),
        n_contributors=len(set(itertools.chain(*contributors.values()))),
        n_patients=sum(len(v) for v in unique_patients.values()),
    )

    return {
        "total_patients": sum(len(v) for v in patients.values()),
        "unique_patients": gs.n_patients,
        "contributors": gs.n_contributors,
    }
