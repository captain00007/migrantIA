"""
Camada de Serviços de Chat do MigrantIA.
Orquestra o ciclo de vida das sessões, higienização LGPD, histórico e pipeline RAG.
Garante que a Moderação e Segurança de Entrada (Normalização Unicode, PII, InjectionGuard, Intent)
seja executada desde o início, ANTES mesmo de salvar a questão no banco de dados.
"""
import logging
from typing import Dict, Any, List, Optional, Tuple
from django.db import transaction
from langchain_core.messages import HumanMessage, AIMessage

from apps.chat.models import (
    ChatSession,
    ChatMessage,
    MessageFeedback,
    SenderTypeChoices,
)
from apps.chat.privacy import sanitize_pii
from ia.guardrails.moderator import InputModerator, GuardrailResult
from ia.security import log_security_event
from ia.prompts.multilingual import DEFAULT_LANGUAGE, detect_language_heuristic
from ia.prompts.refusals import get_refusal_message, RefusalReason
from ia.rag.pipeline import RAGPipeline, get_rag_pipeline

logger = logging.getLogger(__name__)


class ChatService:
    """
    Serviço central de atendimento e persistência de conversas do MigrantIA.
    Aplica guardrails de segurança e higienização antes da persistência no banco.
    """

    def __init__(
        self,
        rag_pipeline: Optional[RAGPipeline] = None,
        moderator: Optional[InputModerator] = None,
    ):
        self._rag_pipeline = rag_pipeline
        self._moderator = moderator

    @property
    def rag_pipeline(self) -> RAGPipeline:
        """Obtém ou instancia o pipeline RAG sob demanda."""
        if self._rag_pipeline is None:
            self._rag_pipeline = get_rag_pipeline()
        return self._rag_pipeline

    @property
    def moderator(self) -> InputModerator:
        """Obtém ou instancia o moderador de entrada."""
        if self._moderator is None:
            if isinstance(self._rag_pipeline, RAGPipeline) and hasattr(self._rag_pipeline, "moderator") and isinstance(self._rag_pipeline.moderator, InputModerator):
                self._moderator = self._rag_pipeline.moderator
            else:
                self._moderator = InputModerator()
        return self._moderator

    def get_or_create_session(
        self,
        session_id: Optional[str] = None,
        ui_language: Optional[str] = None,
        primary_pillar: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Tuple[ChatSession, bool]:
        """
        Recupera uma sessão existente ou cria uma nova com os parâmetros fornecidos.
        """
        if session_id:
            try:
                session = ChatSession.objects.get(id=session_id)
                # Atualiza idioma ou pilar se explicitamente informados
                if ui_language and session.ui_language != ui_language:
                    session.ui_language = ui_language
                    session.save(update_fields=["ui_language", "updated_at"])
                return session, False
            except (ChatSession.DoesNotExist, ValueError):
                logger.info(f"Sessão '{session_id}' não encontrada. Criando nova sessão.")

        lang = ui_language or DEFAULT_LANGUAGE
        session = ChatSession.objects.create(
            ui_language=lang,
            primary_pillar=primary_pillar,
            metadata=metadata or {},
        )
        return session, True

    def get_session_history(
        self,
        session: ChatSession,
        limit: int = 10
    ) -> List[Any]:
        """
        Carrega as mensagens recentes válidas e seguras da sessão formatadas para a chain do LangChain.
        Descarta automaticamente do histórico qualquer interação que tenha sido bloqueada por segurança
        (ex: tentativas de Prompt Injection), garantindo que o contexto do LLM permaneça 100% limpo e seguro.
        """
        # Identifica mensagens do assistente bloqueadas por guardrails e as perguntas associadas
        blocked_pairs = session.messages.filter(
            sender_type=SenderTypeChoices.ASSISTANT,
            metadata__blocked_by__isnull=False
        ).values_list("id", "reply_to_id")

        blocked_message_ids = set()
        for assist_id, reply_id in blocked_pairs:
            if assist_id:
                blocked_message_ids.add(assist_id)
            if reply_id:
                blocked_message_ids.add(reply_id)

        # Filtra apenas mensagens seguras e válidas
        messages_query = session.messages.all()
        if blocked_message_ids:
            messages_query = messages_query.exclude(id__in=blocked_message_ids)

        messages = messages_query.order_by("-created_at")[:limit]
        chronological = list(reversed(messages))

        history = []
        for msg in chronological:
            if msg.sender_type == SenderTypeChoices.USER:
                history.append(HumanMessage(content=msg.content))
            elif msg.sender_type == SenderTypeChoices.ASSISTANT:
                history.append(AIMessage(content=msg.content))
        return history

    def process_user_message(
        self,
        session: ChatSession,
        content: str,
        pillar_filter: Optional[str] = None,
        ui_language_override: Optional[str] = None,
    ) -> Tuple[ChatMessage, ChatMessage]:
        """
        Processa uma mensagem do usuário:
        1. Resolução do idioma de atendimento.
        2. Moderação e Segurança de Entrada ANTES de persistir no banco:
           - Normalização Unicode (NFKC, Homoglyphs, Zero-Width strip)
           - PII Masking / Higienização LGPD
           - InjectionGuard (Prompt Injection, Jailbreak & Encoding Obfuscation)
           - IntentClassifier (Roteamento semântico)
        3. Se for detectado ataque/violação de segurança:
           - Salva registro higienizado e resposta de bloqueio segura imediatamente.
        4. Se for segura:
           - Carrega histórico recente das mensagens anteriores.
           - Salva a mensagem do usuário com o conteúdo sanitizado e normalizado.
           - Invoca o RAGPipeline com o contexto protegido.
           - Salva a resposta do assistente vinculada à pergunta com as fontes citadas.
        """
        clean_text = (content or "").strip()
        if not clean_text:
            raise ValueError("O conteúdo da mensagem não pode ser vazio.")

        # 1. Resolução preliminar do idioma
        effective_lang = ui_language_override or session.ui_language
        if not effective_lang:
            effective_lang = detect_language_heuristic(clean_text)

        # 2. Moderação e Segurança de Entrada ANTES de salvar a questão no banco de dados
        guard_result: GuardrailResult = self.moderator.inspect(clean_text, ui_language=effective_lang)

        # 3. Bloqueio Imediato de Prompt Injection / Violação de Segurança
        if not guard_result.is_safe:
            log_security_event(
                event_type="PROMPT_INJECTION_BLOCKED",
                raw_input=guard_result.sanitized_text,
                reason=guard_result.reason,
                step=0,
            )
            with transaction.atomic():
                user_msg = ChatMessage.objects.create(
                    session=session,
                    sender_type=SenderTypeChoices.USER,
                    content=guard_result.sanitized_text,
                )
                assistant_msg = ChatMessage.objects.create(
                    session=session,
                    reply_to=user_msg,
                    sender_type=SenderTypeChoices.ASSISTANT,
                    content=guard_result.refusal_message or get_refusal_message(RefusalReason.SECURITY_VIOLATION, ui_language=effective_lang),
                    sources_cited=[],
                    golden_rule_triggered=False,
                    metadata={
                        "step": 0,
                        "blocked_by": "injection_guard",
                        "reason": guard_result.reason,
                        "intent": guard_result.intent.value if hasattr(guard_result.intent, "value") else str(guard_result.intent),
                    },
                )
                session.updated_at = assistant_msg.created_at
                session.save(update_fields=["updated_at"])
            return user_msg, assistant_msg

        # 4. Mensagem Segura: Carrega histórico anterior antes de persistir a nova pergunta
        chat_history = self.get_session_history(session=session, limit=10)

        # 5. Salva a mensagem do usuário no banco com o conteúdo higienizado e normalizado
        user_msg = ChatMessage.objects.create(
            session=session,
            sender_type=SenderTypeChoices.USER,
            content=guard_result.sanitized_text,
        )

        # 6. Executa o RAG FORA de qualquer transação de banco de dados
        pillar = pillar_filter or session.primary_pillar
        rag_response = self.rag_pipeline.query(
            question=guard_result.sanitized_text,
            ui_language=effective_lang,
            chat_history=chat_history,
            pillar_filter=pillar,
            guard_result=guard_result,
        )

        # 7. Salva a resposta do assistente vinculada à pergunta e atualiza a sessão atomicamente
        sources_payload = [
            source.model_dump() if hasattr(source, "model_dump") else source.dict()
            for source in rag_response.sources
        ]

        with transaction.atomic():
            assistant_msg = ChatMessage.objects.create(
                session=session,
                reply_to=user_msg,
                sender_type=SenderTypeChoices.ASSISTANT,
                content=rag_response.content,
                sources_cited=sources_payload,
                golden_rule_triggered=rag_response.golden_rule_triggered,
                metadata=rag_response.metadata,
            )

            session.updated_at = assistant_msg.created_at
            session.save(update_fields=["updated_at"])

        return user_msg, assistant_msg

    def submit_feedback(
        self,
        message: ChatMessage,
        rating: int,
        reason: Optional[str] = None,
        comment: str = "",
    ) -> MessageFeedback:
        """
        Registra ou atualiza a avaliação de feedback para uma mensagem do assistente.
        """
        if message.sender_type != SenderTypeChoices.ASSISTANT:
            raise ValueError("Apenas mensagens geradas pelo assistente podem receber avaliação.")

        feedback, _ = MessageFeedback.objects.update_or_create(
            message=message,
            defaults={
                "rating": rating,
                "reason": reason,
                "comment": comment.strip(),
            }
        )
        return feedback


def get_chat_service(
    rag_pipeline: Optional[RAGPipeline] = None,
    moderator: Optional[InputModerator] = None,
) -> ChatService:
    """Retorna uma instância configurada do serviço de chat."""
    return ChatService(rag_pipeline=rag_pipeline, moderator=moderator)
