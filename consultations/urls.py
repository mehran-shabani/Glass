from django.urls import path

from .views import ClinicalAskView, ClinicalConfigView, ClinicalRequestDetailView, ClinicalRequestListView

urlpatterns = [
    path('clinical/ask/', ClinicalAskView.as_view()),
    path('glass/ask/', ClinicalAskView.as_view()),
    path('clinical/config/', ClinicalConfigView.as_view()),
    path('clinical/history/', ClinicalRequestListView.as_view()),
    path('clinical/history/<int:pk>/', ClinicalRequestDetailView.as_view()),
]
