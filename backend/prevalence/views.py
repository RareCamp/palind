from django.views.generic import TemplateView
from django.db.models import Max

from .models import Disease, DiseaseStats, GlobalStats


class PrevalenceView(TemplateView):
    template_name = "prevalence.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        disease_stats = DiseaseStats.objects.filter(
            id__in=DiseaseStats.objects.values("disease")
            .annotate(max_id=Max("id"))
            .values("max_id")
        ).order_by("-n_patients")

        context["diseases"] = disease_stats[:16]

        context["patients_by_disease"] = disease_stats[:5]

        global_stats = GlobalStats.objects.order_by("-created_at").first()

        context["global_stats"] = global_stats
        context[
            "patients_by_source"
        ] = global_stats.patientsbysource_set.all().order_by("-n_patients")

        return context
