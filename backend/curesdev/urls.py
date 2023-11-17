from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView, TemplateView

from django.conf import settings
from django.conf.urls.static import static

from accounts.views import OrganizationDetailView
from datasets.views import (
    LinkerDemo,
    SubmitView,
    DatasetCreateView,
    DatasetListView,
    DatasetDetailView,
    DatasetUpdateView,
    DatasetDeleteView,
    DatasetUploadCSV,
    DatasetExportCSVView,
    merge_view,
)

urlpatterns = (
    [
        path("", RedirectView.as_view(url="/datasets"), name="home"),
        # API: create a submission
        path("v2/submit/", SubmitView.as_view(), name="submit"),
        # Accounts
        path(
            "organization/<int:pk>/",
            OrganizationDetailView.as_view(),
            name="organization_detail",
        ),
        # Login, logout, etc.
        path("accounts/", include("django.contrib.auth.urls")),
        # Datasets
        path("datasets/", DatasetListView.as_view(), name="dataset_list"),
        path("dataset/<int:pk>/", DatasetDetailView.as_view(), name="dataset_detail"),
        path(
            "dataset/<int:pk>/export",
            DatasetExportCSVView.as_view(),
            name="dataset_export",
        ),
        path(
            "dataset/<int:pk>/edit", DatasetUpdateView.as_view(), name="dataset_update"
        ),
        path(
            "dataset/<int:pk>/delete",
            DatasetDeleteView.as_view(),
            name="dataset_delete",
        ),
        path(
            "dataset/<int:pk>/upload",
            DatasetUploadCSV.as_view(),
            name="dataset_upload_csv",
        ),
        path("datasets/new/", DatasetCreateView.as_view(), name="dataset_create"),
        # Demos
        path(
            "bloom-filter-demo",
            TemplateView.as_view(template_name="demos/bloom_filter_demo.html"),
            name="bloom-filter-demo",
        ),
        path("linker-demo", LinkerDemo.as_view(), name="linker-demo"),
        path("merge-datasets", merge_view, name="merge-datasets"),
        # Admin site
        path("admin/", admin.site.urls),
        # Debug toolbar
        path("__debug__/", include("debug_toolbar.urls")),
    ]
    + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
)
