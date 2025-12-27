from django.urls import path
from .views import DataIngestionView

urlpatterns = [
    path("api/v1/ingest/", DataIngestionView.as_view(), name="data-ingest"),
]
