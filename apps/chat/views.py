"""
Views e Endpoints REST do Chat do MigrantIA.
"""
import logging
from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination

from apps.chat.models import ChatSession, ChatMessage
from apps.chat.serializers import (
    ChatSessionSerializer,
    CreateSessionSerializer,
    ChatMessageSerializer,
    SendMessageInputSerializer,
    SendMessageResponseSerializer,
    MessageFeedbackSerializer,
)
from apps.chat.services import get_chat_service

logger = logging.getLogger(__name__)


class ChatHomeView(TemplateView):
    """
    GET / -> Renderiza a interface PWA do MigrantIA.
    """
    template_name = "index.html"


class StandardMessagesPagination(PageNumberPagination):
    page_size = 50
    page_size_query_param = "page_size"
    max_page_size = 100


class SessionListCreateView(APIView):
    """
    POST /api/chat/sessions/ -> Cria uma nova sessão.
    GET /api/chat/sessions/  -> Lista sessões recentes ativas.
    """

    def get(self, request):
        sessions = ChatSession.objects.filter(is_active=True).order_by("-updated_at")[:20]
        serializer = ChatSessionSerializer(sessions, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = CreateSessionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        chat_service = get_chat_service()
        session, _ = chat_service.get_or_create_session(
            ui_language=data.get("ui_language"),
            primary_pillar=data.get("primary_pillar"),
            metadata=data.get("metadata"),
        )
        return Response(
            ChatSessionSerializer(session).data,
            status=status.HTTP_201_CREATED
        )


class SessionDetailView(APIView):
    """
    GET /api/chat/sessions/<uuid:session_id>/ -> Recupera dados de uma sessão existente.
    """

    def get(self, request, session_id):
        session = get_object_or_404(ChatSession, id=session_id)
        serializer = ChatSessionSerializer(session)
        return Response(serializer.data, status=status.HTTP_200_OK)


class SessionMessagesView(APIView):
    """
    GET  /api/chat/sessions/<uuid:session_id>/messages/ -> Histórico de mensagens da sessão.
    POST /api/chat/sessions/<uuid:session_id>/messages/ -> Envia pergunta e processa com RAG.
    """

    def get(self, request, session_id):
        session = get_object_or_404(ChatSession, id=session_id)
        messages = session.messages.all().order_by("created_at")
        serializer = ChatMessageSerializer(messages, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, session_id):
        session = get_object_or_404(ChatSession, id=session_id)
        input_serializer = SendMessageInputSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)
        validated = input_serializer.validated_data

        chat_service = get_chat_service()
        user_msg, assistant_msg = chat_service.process_user_message(
            session=session,
            content=validated["content"],
            pillar_filter=validated.get("pillar"),
            ui_language_override=validated.get("ui_language"),
        )

        response_data = {
            "user_message": ChatMessageSerializer(user_msg).data,
            "assistant_message": ChatMessageSerializer(assistant_msg).data,
        }
        return Response(response_data, status=status.HTTP_200_OK)


class MessageFeedbackView(APIView):
    """
    POST /api/chat/messages/<uuid:message_id>/feedback/ -> Registra avaliação da resposta.
    """

    def post(self, request, message_id):
        message = get_object_or_404(ChatMessage, id=message_id)
        serializer = MessageFeedbackSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated = serializer.validated_data

        chat_service = get_chat_service()
        feedback = chat_service.submit_feedback(
            message=message,
            rating=validated["rating"],
            reason=validated.get("reason"),
            comment=validated.get("comment", ""),
        )

        return Response(
            MessageFeedbackSerializer(feedback).data,
            status=status.HTTP_201_CREATED
        )
