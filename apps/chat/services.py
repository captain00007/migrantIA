"""
Camada de Serviços de Chat do MigrantIA.
Orquestra o ciclo de vida das sessões, higienização LGPD, histórico e pipeline RAG.
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
from ia.rag.pipeline import RAGPipeline, get_rag_pipeline
from ia.prompts.multilingual import DEFAULT_LANGUAGE, detect_language_heuristic

logger = logging.getLogger(__name__)


class ChatService:
    """
    Serviço central de atendimento e persistência de conversas do MigrantIA.
    """

    def __init__(self, rag_pipeline: Optional[RAGPipeline] = None):
        self._rag_pipeline = rag_pipeline

    @property
    def rag_pipeline(self) -> RAGPipeline:
        """Obtém ou instancia o pipeline RAG sob demanda."""
        if self._rag_pipeline is None:
            self._rag_pipeline = get_rag_pipeline()
        return self._rag_pipeline

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
        limit: int = 6
    ) -> List[Any]:
        """
        Carrega as mensagens recentes da sessão formatadas para a chain do LangChain.
        """
        messages = session.messages.order_by("-created_at")[:limit]
        # Inverte para ordem cronológica
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
        1. Higieniza dados sensíveis (LGPD).
        2. Registra a mensagem do usuário no banco.
        3. Invoca o RAGPipeline com o histórico recente da conversa.
        4. Registra a resposta fundamentada do assistente com as fontes citadas e o vínculo reply_to.
        """
        clean_text = content.strip()
        if not clean_text:
            raise ValueError("O conteúdo da mensagem não pode ser vazio.")

        # 1. Higienização LGPD
        sanitized_content = sanitize_pii(clean_text)

        # 2. Resolução do idioma
        effective_lang = ui_language_override or session.ui_language
        if not effective_lang:
            effective_lang = detect_language_heuristic(clean_text)

        with transaction.atomic():
            # 3. Salva a mensagem do usuário
            user_msg = ChatMessage.objects.create(
                session=session,
                sender_type=SenderTypeChoices.USER,
                content=sanitized_content,
            )

            # 4. Obtém histórico para a chain
            chat_history = self.get_session_history(session=session, limit=6)

            # 5. Executa o RAG
            pillar = pillar_filter or session.primary_pillar
            rag_response = self.rag_pipeline.query(
                question=sanitized_content,
                ui_language=effective_lang,
                chat_history=chat_history,
                pillar_filter=pillar,
            )

            # 6. Salva a resposta do assistente vinculada à pergunta via reply_to
            sources_payload = [
                source.model_dump() if hasattr(source, "model_dump") else source.dict()
                for source in rag_response.sources
            ]

            assistant_msg = ChatMessage.objects.create(
                session=session,
                reply_to=user_msg,
                sender_type=SenderTypeChoices.ASSISTANT,
                content=rag_response.content,
                sources_cited=sources_payload,
                golden_rule_triggered=rag_response.golden_rule_triggered,
                metadata=rag_response.metadata,
            )

            # Atualiza a sessão
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


def get_chat_service(rag_pipeline: Optional[RAGPipeline] = None) -> ChatService:
    """Retorna uma instância configurada do serviço de chat."""
    return ChatService(rag_pipeline=rag_pipeline)
