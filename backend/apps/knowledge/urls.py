from django.urls import path
from . import views

urlpatterns = [
    path('status/', views.KnowledgeStatusView.as_view(), name='knowledge-status'),
    path('upload/', views.DocumentUploadView.as_view(), name='document-upload'),
    path('documents/', views.DocumentListView.as_view(), name='document-list'),
    path('documents/<str:md5>/', views.DocumentDeleteView.as_view(), name='document-delete'),
    path('search/', views.SearchTestView.as_view(), name='search-test'),
    path('rebuild/', views.RebuildView.as_view(), name='rebuild'),
]
