from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

from .models import Disease, URLSource, GlobalStats, DiseaseStats, PatientsBySource


class URLSourceAdmin(admin.ModelAdmin):
    list_display = ("name", "url", "disease_link")

    def disease_link(self, obj):
        url = reverse("admin:prevalence_disease_change", args=[obj.disease.id])
        return format_html('<a href="{}">{}</a>', url, obj.disease)

    disease_link.short_description = "Disease"


class GlobalStatsAdmin(admin.ModelAdmin):
    list_display = ("n_diseases", "n_contributors", "n_patients", "created_at")


class DiseaseStatsAdmin(admin.ModelAdmin):
    list_display = (
        "disease",
        "n_contributors",
        "n_patients",
        "confidence",
        "created_at",
    )


class PatientsBySourceAdmin(admin.ModelAdmin):
    list_display = ("source", "n_patients")


class DiseaseAdmin(admin.ModelAdmin):
    list_display = ("name", "description", "do_id", "OMIM", "ORDO", "UMLS_CUI", "NCI")
    search_fields = ["do_json"]


admin.site.register(Disease, DiseaseAdmin)
admin.site.register(URLSource, URLSourceAdmin)
admin.site.register(GlobalStats, GlobalStatsAdmin)
admin.site.register(DiseaseStats, DiseaseStatsAdmin)
admin.site.register(PatientsBySource, PatientsBySourceAdmin)
