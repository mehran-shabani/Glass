from django.urls import path

from .views import ClinicalAskView, ClinicalConfigView, HistoryDetailView, HistoryListView

urlpatterns = [
    path("clinical/ask/", ClinicalAskView.as_view()),
    path("glass/ask/", ClinicalAskView.as_view()),
    path("clinical/config/", ClinicalConfigView.as_view()),
    path("clinical/history/", HistoryListView.as_view()),
    path("clinical/history/<int:pk>/", HistoryDetailView.as_view()),
]
