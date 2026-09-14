"""
Rotas REST do aplicativo apps/chat.
"""
from django.urls import path
from apps.chat.views import (
    SessionListCreateView,
    SessionDetailView,
    SessionMessagesView,
    MessageFeedbackView,
)

app_name = "chat"

urlpatterns = [
    path("sessions/", SessionListCreateView.as_view(), name="session-list-create"),
    path("sessions/<uuid:session_id>/", SessionDetailView.as_view(), name="session-detail"),
    path("sessions/<uuid:session_id>/messages/", SessionMessagesView.as_view(), name="session-messages"),
    path("messages/<uuid:message_id>/feedback/", MessageFeedbackView.as_view(), name="message-feedback"),
]
