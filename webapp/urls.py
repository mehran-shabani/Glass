from django.urls import path
from . import views
urlpatterns=[path('',views.clinical_chat_page,name='clinical-chat')]
