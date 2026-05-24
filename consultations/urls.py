from django.urls import path

from .views import (
    ClinicalAskView,
    ClinicalConfigView,
    ClinicalHistoryDetailView,
    ClinicalHistoryListView,
)

urlpatterns = [
    path("clinical/config/", ClinicalConfigView.as_view(), name="clinical-config"),
    path("clinical/ask/", ClinicalAskView.as_view(), name="clinical-ask"),
    path("clinical/history/", ClinicalHistoryListView.as_view(), name="clinical-history"),
    path("clinical/history/<int:pk>/", ClinicalHistoryDetailView.as_view(), name="clinical-history-detail"),
]
