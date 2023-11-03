import json
from typing import Any, Dict
import uuid

from django.http import JsonResponse, HttpResponse
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views import View
from django.views.generic import (
    DetailView,
    TemplateView,
    ListView,
    CreateView,
    DeleteView,
    UpdateView,
)
from django.views.decorators.csrf import csrf_exempt

from accounts.models import Organization

from .models import Dataset, DatasetPatient, Submission, are_similar, dice

#############
# Dashboard #
#############


class DatasetsView(ListView):
    model = Dataset
    template_name = "dashboard/dataset_list.html"
    context_object_name = "datasets"

    def get_queryset(self):
        return Dataset.objects.filter(organization__users=self.request.user)


class DatasetDetailView(DetailView):
    model = Dataset
    template_name = "dashboard/dataset_detail.html"
    context_object_name = "dataset"

    # Only allow users who are part of the organization to view it
    def get_queryset(self):
        return Dataset.objects.filter(organization__users=self.request.user)


class DatasetCreateView(CreateView):
    model = Dataset
    template_name = "dashboard/dataset_create.html"
    fields = ["name", "description", "tags"]

    def form_valid(self, form):
        form.instance.public = True  # TODO: remove this
        form.instance.created_by = self.request.user
        form.instance.organization = self.request.user.organization
        return super().form_valid(form)


class DatasetUpdateView(UpdateView):
    model = Dataset
    template_name = "dashboard/dataset_update.html"
    fields = ["name", "description", "tags"]

    def get_queryset(self):
        return Dataset.objects.filter(organization=self.request.user.organization)

    def form_valid(self, form):
        form.instance.public = True  # TODO: remove this
        form.instance.created_by = self.request.user
        form.instance.organization = self.request.user.organization
        return super().form_valid(form)


class DatasetDeleteView(DeleteView):
    model = Dataset
    template_name = "dashboard/dataset_confirm_delete.html"
    success_url = reverse_lazy("dataset_list")

    def get_queryset(self):
        return Dataset.objects.filter(organization=self.request.user.organization)


class DatasetUploadCSV(DetailView):
    model = Dataset
    template_name = "dashboard/dataset_upload_csv.html"
    context_object_name = "dataset"

    def get_queryset(self):
        return Dataset.objects.filter(organization=self.request.user.organization)

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        data = super().get_context_data(**kwargs)
        data["fields"] = [
            {
                "field": f.name.replace("_token", ""),
                "name": f.verbose_name,
                "description": f.help_text,
            }
            for f in Submission._meta.get_fields()
            if f.name.endswith("_token")
            and "soundex" not in f.name
            and "full" not in f.name
        ]
        return data


#######
# API #
#######


@method_decorator(csrf_exempt, name="dispatch")
class SubmitView(View):
    """
    Submit tokens to a dataset
    The dataset is identified by the token in the Authorization header
    A new patient is created if no similar patient is found
    """

    def post(self, request):
        # Get Auth token bearer from header
        token = uuid.UUID(
            request.META.get("HTTP_AUTHORIZATION", None).replace("Bearer ", "")
        )

        # Find dataset with this token
        try:
            print(token)
            dataset = Dataset.objects.get(api_token=token)
        except:
            return HttpResponse(status=401, content="Invalid token")

        # Create submission
        data = json.loads(request.body.decode("utf-8"))
        submission = Submission(
            protocol_version="1.0.0",
            dataset=dataset,
            first_name_token=data.get("first_name_token", ""),
            middle_name_token=data.get("middle_name_token", ""),
            last_name_token=data.get("last_name_token", ""),
            full_name_token=data.get("full_name_token", ""),
            first_name_soundex_token=data.get("first_name_soundex_token", ""),
            last_name_soundex_token=data.get("last_name_soundex_token", ""),
            gender_token=data.get("gender_token", ""),
            date_of_birth_token=data.get("date_of_birth_token", ""),
            address_at_bith_token=data.get("address_at_bith_token", ""),
            city_at_birth_token=data.get("city_at_birth_token", ""),
            state_at_birth_token=data.get("state_at_birth_token", ""),
            country_at_birth_token=data.get("country_at_birth_token", ""),
        )

        # Search if there is any similar patient and create one if not
        patient = dataset.find_matching_patient(submission)
        if patient is None:
            patient = DatasetPatient.objects.create(dataset=dataset)

        # Set the patient and save submission
        submission.dataset_patient = patient
        submission.save()

        print(token, dataset)
        return JsonResponse({"public_id": patient.public_id.url()})


# class OrganizationDetailView(DetailView):
#     model = Organization
#     template_name = "organization.html"
#     context_object_name = "organization"

#     # Only allow users who are part of the organization to view it
#     def get_queryset(self):
#         return Organization.objects.filter(users=self.request.user)


#########
# Demos #
#########


# Dataset detailview
class UploadCSV(DetailView):
    model = Dataset
    template_name = "upload_csv.html"
    context_object_name = "dataset"

    # Only allow users who are part of the organization to view it
    def get_queryset(self):
        return (
            Dataset.objects.all()
        )  # filter(organization__users__contains=self.request.user)

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        data = super().get_context_data(**kwargs)
        data["fields"] = [
            {
                "field": f.name.replace("_token", ""),
                "name": f.verbose_name,
                "description": f.help_text,
            }
            for f in Submission._meta.get_fields()
            if f.name.endswith("_token")
            and "soundex" not in f.name
            and "full" not in f.name
        ]
        return data


class LinkerDemo(TemplateView):
    template_name = "linker_demo.html"

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        data = super().get_context_data(**kwargs)
        data["organizations"] = Organization.objects.all()
        return data


def merge_view(request):
    # Get two get parameters
    dataset1 = request.GET.get("dataset1", None)
    dataset2 = request.GET.get("dataset2", None)

    dataset1 = Dataset.objects.get(pk=dataset1)
    dataset2 = Dataset.objects.get(pk=dataset2)

    matches = []

    for p1 in dataset1.datasetpatient_set.all():
        s1 = p1.submission_set.first()
        for p2 in dataset2.datasetpatient_set.all():
            s2 = p2.submission_set.first()
            if are_similar(s1, s2):
                matches.append(
                    {
                        "patient1": p1.public_id.url(),
                        "patient2": p2.public_id.url(),
                        "similarity": 0.99,
                        "fields_similarity": [
                            {
                                "field": f.verbose_name,
                                "similarity": (
                                    100 * dice(getattr(s1, f.name), getattr(s2, f.name))
                                ),
                            }
                            for f in Submission._meta.get_fields()
                            if f.name.endswith("_token")
                            if getattr(s1, f.name) != "" and getattr(s2, f.name) != ""
                        ],
                    }
                )
                matches[-1]["similarity"] = sum(
                    f["similarity"] for f in matches[-1]["fields_similarity"]
                ) / len(matches[-1]["fields_similarity"])
    return JsonResponse(matches, safe=False)
