from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView

from django.conf import settings
from django.conf.urls.static import static

from datasets.views import (
    DatasetDetailView,
    LinkerDemo,
    SubmitView,
    UploadCSV,
    DatasetCreateView,
    DatasetsView,
    DatasetUpdateView,
    DatasetDeleteView,
    merge_view,
)

urlpatterns = (
    [
        # Home page
        path("", TemplateView.as_view(template_name="home.html"), name="home"),
        # Create a submission
        path("v2/submit/", SubmitView.as_view(), name="submit"),
        # Organization
        # path(
        #     "organization/<int:pk>/",
        #     OrganizationDetailView.as_view(),
        #     name="organization",
        # ),
        path("dataset/<int:pk>/upload-csv", UploadCSV.as_view(), name="upload_csv"),
        # Demos
        path(
            "bloom-filter-demo",
            TemplateView.as_view(template_name="bloom_filter_demo.html"),
            name="bloom-filter-demo",
        ),
        path("linker-demo", LinkerDemo.as_view(), name="linker-demo"),
        path("merge-datasets", merge_view, name="merge-datasets"),
        # Dashboard
        path("datasets/", DatasetsView.as_view(), name="dataset_list"),
        path("dataset/<int:pk>/", DatasetDetailView.as_view(), name="dataset_detail"),
        path(
            "dataset/<int:pk>/edit", DatasetUpdateView.as_view(), name="dataset_update"
        ),
        path(
            "dataset/<int:pk>/delete",
            DatasetDeleteView.as_view(),
            name="dataset_delete",
        ),
        path("datasets/new/", DatasetCreateView.as_view(), name="dataset_create"),
        # Admin site
        path("admin/", admin.site.urls),
        # Debug toolbar
        path("__debug__/", include("debug_toolbar.urls")),
    ]
    + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
)
