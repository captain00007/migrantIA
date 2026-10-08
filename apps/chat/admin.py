from django.contrib import admin
from apps.chat.models import ChatSession, ChatMessage, MessageFeedback


class ChatMessageInline(admin.TabularInline):
    model = ChatMessage
    extra = 0
    readonly_fields = [
        "id",
        "sender_type",
        "content",
        "is_security_threat",
        "security_threat_reason",
        "golden_rule_triggered",
        "created_at",
    ]
    can_delete = False


@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    list_display = ["id", "ui_language", "primary_pillar", "is_active", "created_at", "updated_at"]
    list_filter = ["ui_language", "primary_pillar", "is_active"]
    search_fields = ["id"]
    inlines = [ChatMessageInline]


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "session",
        "sender_type",
        "is_security_threat",
        "security_threat_reason",
        "golden_rule_triggered",
        "created_at",
    ]
    list_filter = ["sender_type", "is_security_threat", "security_threat_reason", "golden_rule_triggered", "created_at"]
    search_fields = ["content", "session__id", "security_threat_reason"]


@admin.register(MessageFeedback)
class MessageFeedbackAdmin(admin.ModelAdmin):
    list_display = ["id", "message", "rating", "reason", "created_at"]
    list_filter = ["rating", "reason", "created_at"]
