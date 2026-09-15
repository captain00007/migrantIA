"""
Serializadores REST para o app apps/chat.
"""
from rest_framework import serializers
from apps.chat.models import (
    ChatSession,
    ChatMessage,
    MessageFeedback,
    UILanguageChoices,
    SenderTypeChoices,
    FeedbackRatingChoices,
    FeedbackReasonChoices,
)
from apps.sources.models import PillarChoices


class MessageFeedbackSerializer(serializers.ModelSerializer):
    """Serializador para criação e consulta de avaliações de mensagens."""
    
    class Meta:
        model = MessageFeedback
        fields = ["id", "rating", "reason", "comment", "created_at"]
        read_only_fields = ["id", "created_at"]

    def validate_rating(self, value):
        if value not in [1, -1]:
            raise serializers.ValidationError("O rating deve ser 1 (útil) ou -1 (não útil).")
        return value


class ChatMessageSerializer(serializers.ModelSerializer):
    """Serializador detalhado de mensagens do chat."""
    feedback = MessageFeedbackSerializer(read_only=True)

    class Meta:
        model = ChatMessage
        fields = [
            "id",
            "session_id",
            "reply_to_id",
            "sender_type",
            "content",
            "sources_cited",
            "golden_rule_triggered",
            "metadata",
            "feedback",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "session_id",
            "reply_to_id",
            "sender_type",
            "sources_cited",
            "golden_rule_triggered",
            "metadata",
            "feedback",
            "created_at",
        ]


class ChatSessionSerializer(serializers.ModelSerializer):
    """Serializador de sessões de atendimento."""
    messages_count = serializers.IntegerField(source="messages.count", read_only=True)

    class Meta:
        model = ChatSession
        fields = [
            "id",
            "ui_language",
            "primary_pillar",
            "is_active",
            "metadata",
            "messages_count",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "messages_count", "created_at", "updated_at"]


class CreateSessionSerializer(serializers.Serializer):
    """Validação de payload para abertura de nova sessão."""
    ui_language = serializers.ChoiceField(
        choices=UILanguageChoices.choices,
        default="pt",
        required=False
    )
    primary_pillar = serializers.ChoiceField(
        choices=PillarChoices.choices,
        required=False,
        allow_null=True
    )
    metadata = serializers.DictField(
        required=False,
        default=dict
    )


class SendMessageInputSerializer(serializers.Serializer):
    """Validação de mensagem enviada pelo usuário."""
    content = serializers.CharField(
        min_length=1,
        max_length=4000,
        trim_whitespace=True
    )
    ui_language = serializers.ChoiceField(
        choices=UILanguageChoices.choices,
        required=False,
        allow_null=True
    )
    pillar = serializers.ChoiceField(
        choices=PillarChoices.choices,
        required=False,
        allow_null=True
    )


class SendMessageResponseSerializer(serializers.Serializer):
    """Estrutura da resposta retornada após o processamento da mensagem."""
    user_message = ChatMessageSerializer()
    assistant_message = ChatMessageSerializer()
