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

    source = models.ForeignKey("datasets.Source", on_delete=models.CASCADE)
    n_patients = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = " Patients by Source"
        verbose_name_plural = " Patients by Source"


class Disease(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    do_id = models.CharField(max_length=20, blank=True)
    do_json = models.JSONField(blank=True, null=True)

    # External IDs
    SNOMEDCT_US_2023_03_01 = models.CharField(max_length=200, blank=True)
    UMLS_CUI = models.CharField(max_length=200, blank=True)
    ICD10CM = models.CharField(max_length=200, blank=True)
    ICD9CM = models.CharField(max_length=200, blank=True)
    SNOMEDCT_US_2021_09_01 = models.CharField(max_length=200, blank=True)
    MESH = models.CharField(max_length=200, blank=True)
    NCI = models.CharField(max_length=200, blank=True)
    ORDO = models.CharField(max_length=200, blank=True)
    GARD = models.CharField(max_length=200, blank=True)
    EFO = models.CharField(max_length=200, blank=True)
    OMIM = models.CharField(max_length=200, blank=True)
    ICDO = models.CharField(max_length=200, blank=True)
    KEGG = models.CharField(max_length=200, blank=True)
    MEDDRA = models.CharField(max_length=200, blank=True)
    SNOMEDCT_US_2021_07_31 = models.CharField(max_length=200, blank=True)
    SNOMEDCT_US_2020_03_01 = models.CharField(max_length=200, blank=True)
    SNOMEDCT_US_2023_10_01 = models.CharField(max_length=200, blank=True)
    ICD11 = models.CharField(max_length=200, blank=True)
    SNOMEDCT_US_2022_07_31 = models.CharField(max_length=200, blank=True)
    SNOMEDCT_US_2023_09_01 = models.CharField(max_length=200, blank=True)

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
    global_stats = models.ForeignKey(GlobalStats, on_delete=models.CASCADE)
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
    sources = collections.defaultdict(int)

    for p in DatasetPatient.objects.all():
        submission = p.submission_set.last()
        if submission.disease:
            patients[submission.disease].append(submission)

    disease_stats = []
    for disease_name, disease_patients in patients.items():
        disease, _ = Disease.objects.get_or_create(name=disease_name)

        for p in disease_patients:
            contributors[disease_name].add(p.dataset.created_by.organization.pk)
            if not any(are_similar(p, up) for up in unique_patients[disease_name]):
                unique_patients[disease_name].append(p)
                sources[p.dataset.source] += 1

        disease_stats.append(
            DiseaseStats(
                disease=disease,
                n_contributors=len(contributors[disease_name]),
                n_patients=len(unique_patients[disease_name]),
                confidence="low",  # TODO
            )
        )

    global_stats = GlobalStats.objects.create(
        n_diseases=len(unique_patients),
        n_contributors=len(set(itertools.chain(*contributors.values()))),
        n_patients=sum(len(v) for v in unique_patients.values()),
    )

    for source, n in sources.items():
        PatientsBySource.objects.create(
            source=source, n_patients=n, global_stats=global_stats
        )

    # Assign all disease stats to the global stats
    for ds in disease_stats:
        ds.global_stats = global_stats
        ds.save()

    return global_stats, disease_stats
