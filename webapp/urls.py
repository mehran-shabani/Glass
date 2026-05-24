from django.urls import path

from . import views

urlpatterns = [
    path("", views.clinical_chat_page, name="clinical-chat"),
    path("clinical/", views.clinical_chat_page, name="clinical-chat-clinical"),
]
