from .models import Organization
from django.views.generic import DetailView


class OrganizationDetailView(DetailView):
    model = Organization
    template = "organization_detail.html"
    context_object_name = "organization"
