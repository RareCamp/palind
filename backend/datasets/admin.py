from django.contrib import admin

from .models import (
    Tag,
    Dataset,
    PublicID,
    DatasetPatient,
    Submission,
)


class DatasetAdmin(admin.ModelAdmin):
    readonly_fields = ("api_token",)
    list_display = (
        "id",
        "name",
        "description",
        "organization",
        "created_by",
        "api_token",
    )


class DatasetPatientAdmin(admin.ModelAdmin):
    readonly_fields = ("public_id",)
    list_display = ("public_id", "created_at", "dataset")

    list_filter = ("dataset",)


class SubmissionAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "created_at",
        "dataset",
        "disease",
        "dataset_patient",
        "protocol_version",
    )

    list_filter = ("dataset", "protocol_version")


class PublicIDAdmin(admin.ModelAdmin):
    list_display = ("id", "dataset_patient")

    def dataset_patient(self, obj):
        return obj.datasetpatient


admin.site.register(Tag)
admin.site.register(Dataset, DatasetAdmin)
admin.site.register(PublicID, PublicIDAdmin)
admin.site.register(DatasetPatient, DatasetPatientAdmin)
admin.site.register(Submission, SubmissionAdmin)
