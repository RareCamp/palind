from django.contrib import admin

from .models import (
    Organization,
    DatasetTag,
    Dataset,
    PublicID,
    DatasetPatient,
    GlobalPatient,
    Submission,
    UserProfile,
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
        "dataset_patient",
        "protocol_version",
    )

    list_filter = ("dataset", "protocol_version")


class OrganizationAdmin(admin.ModelAdmin):
    list_display = ("name", "users_list")

    def users_list(self, obj):
        return ", ".join([u.username for u in obj.users.all()])


class PublicIDAdmin(admin.ModelAdmin):
    list_display = ("id", "dataset_patient")

    def dataset_patient(self, obj):
        return obj.datasetpatient


admin.site.register(DatasetTag)
admin.site.register(UserProfile)
admin.site.register(Dataset, DatasetAdmin)
admin.site.register(Organization, OrganizationAdmin)
admin.site.register(PublicID, PublicIDAdmin)
admin.site.register(DatasetPatient, DatasetPatientAdmin)
admin.site.register(Submission, SubmissionAdmin)
admin.site.register(GlobalPatient)
