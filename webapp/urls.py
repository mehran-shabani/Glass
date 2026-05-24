from django.urls import path
from . import views
urlpatterns=[path('',views.glass_chat_page,name='glass-chat')]
