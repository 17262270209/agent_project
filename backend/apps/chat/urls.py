from django.urls import path
from . import views

urlpatterns = [
    path('sessions/', views.SessionListView.as_view(), name='session-list'),
    path('sessions/<str:session_id>/', views.SessionDetailView.as_view(), name='session-detail'),
    path('sessions/<str:session_id>/continue/', views.ContinueSessionView.as_view(), name='session-continue'),
    path('send/', views.ChatSendView.as_view(), name='chat-send'),
    path('quick-questions/', views.QuickQuestionsView.as_view(), name='quick-questions'),
]
