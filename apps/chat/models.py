import uuid
from django.db import models
from apps.sources.models import PillarChoices
from ia.prompts.multilingual import SUPPORTED_UI_LANGUAGES, DEFAULT_LANGUAGE


class UILanguageChoices(models.TextChoices):
    KREYOL = "ht", "Kreyòl Ayisyen (Crioulo Haitiano)"
    FRENCH = "fr", "Français (Francês)"
    SPANISH = "es", "Español (Espanhol)"
    ENGLISH = "en", "English (Inglês)"
    PORTUGUESE = "pt", "Português (Brasil)"


class SenderTypeChoices(models.TextChoices):
    USER = "USER", "Usuário"
    ASSISTANT = "ASSISTANT", "Assistente MigrantIA"
    SYSTEM = "SYSTEM", "Sistema"


class FeedbackRatingChoices(models.IntegerChoices):
    POSITIVE = 1, "Útil / Positivo"
    NEGATIVE = -1, "Não Útil / Negativo"


class FeedbackReasonChoices(models.TextChoices):
    INACCURATE = "INACCURATE", "Informação Incorreta ou Imprecisa"
    UNHELPFUL = "UNHELPFUL", "Não Respondeu à Dúvida"
    OUTDATED = "OUTDATED", "Informação Desatualizada"
    LANGUAGE_ERROR = "LANGUAGE_ERROR", "Problema de Tradução ou Idioma"
    OTHER = "OTHER", "Outro Motivo"


class ChatSession(models.Model):
    """
    Sessão de conversação entre o usuário (migrante/refugiado) e o assistente MigrantIA.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    ui_language = models.CharField(
        max_length=10,
        choices=UILanguageChoices.choices,
        default=DEFAULT_LANGUAGE,
        db_index=True,
        help_text="Código ISO do idioma da interface e respostas"
    )
    primary_pillar = models.CharField(
        max_length=30,
        choices=PillarChoices.choices,
        null=True,
        blank=True,
        db_index=True,
        help_text="Pilar temático principal da sessão se selecionado"
    )
    is_active = models.BooleanField(default=True)
    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text="Metadados de acesso anônimos (ex: canal PWA, user-agent)"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Sessão de Atendimento"
        verbose_name_plural = "Sessões de Atendimento"
        ordering = ["-updated_at"]

    def __str__(self):
        return f"Sessão {self.id} [{self.ui_language}] - {self.created_at.strftime('%d/%m/%Y %H:%M')}"


class ChatMessage(models.Model):
    """
    Mensagem individual persistida em uma sessão de atendimento.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session = models.ForeignKey(
        ChatSession,
        on_delete=models.CASCADE,
        related_name="messages",
        db_index=True
    )
    sender_type = models.CharField(
        max_length=20,
        choices=SenderTypeChoices.choices,
        default=SenderTypeChoices.USER,
        db_index=True
    )
    content = models.TextField(
        help_text="Conteúdo textual da mensagem (higienizado contra PII/LGPD)"
    )
    sources_cited = models.JSONField(
        default=list,
        blank=True,
        help_text="Lista de fontes oficiais e links governamentais citados"
    )
    golden_rule_triggered = models.BooleanField(
        default=False,
        help_text="Indica se a resposta ativou a salvaguarda da Regra de Ouro (sem evidências)"
    )
    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text="Métricas de tempo de resposta, step RAG e tokens"
    )
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        verbose_name = "Mensagem do Chat"
        verbose_name_plural = "Mensagens do Chat"
        ordering = ["created_at"]

    def __str__(self):
        return f"[{self.get_sender_type_display()}] {self.content[:40]}..."


class MessageFeedback(models.Model):
    """
    Avaliação de qualidade e utilidade registrada pelo usuário para uma resposta do assistente.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    message = models.OneToOneField(
        ChatMessage,
        on_delete=models.CASCADE,
        related_name="feedback"
    )
    rating = models.SmallIntegerField(
        choices=FeedbackRatingChoices.choices,
        help_text="+1 para útil, -1 para não útil"
    )
    reason = models.CharField(
        max_length=30,
        choices=FeedbackReasonChoices.choices,
        null=True,
        blank=True,
        help_text="Motivo categorizado em caso de feedback negativo"
    )
    comment = models.TextField(
        blank=True,
        default="",
        help_text="Comentário livre ou sugestão do usuário"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Avaliação da Mensagem"
        verbose_name_plural = "Avaliações das Mensagens"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Feedback {self.get_rating_display()} na mensagem {self.message_id}"
