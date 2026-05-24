from django.urls import path
from .views import ChatView,GlassClinicalAskView,GlassClinicalRequestListView,GlassClinicalRequestDetailView
urlpatterns=[
 path('chat/',ChatView.as_view()),
 path('glass/ask/',GlassClinicalAskView.as_view()),
 path('glass/history/',GlassClinicalRequestListView.as_view()),
 path('glass/history/<int:pk>/',GlassClinicalRequestDetailView.as_view()),
]
