from .models import Organization
from django.views.generic import DetailView

from django.contrib.auth.mixins import LoginRequiredMixin


class OrganizationDetailView(LoginRequiredMixin, DetailView):
    model = Organization
    template = "organization_detail.html"
    context_object_name = "organization"
