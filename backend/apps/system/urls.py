from django.urls import path
from . import views

urlpatterns = [
    path('statistics/', views.StatisticsView.as_view(), name='statistics'),
    path('config/', views.SystemConfigView.as_view(), name='system-config'),
    path('logs/', views.LogsView.as_view(), name='logs'),
]
