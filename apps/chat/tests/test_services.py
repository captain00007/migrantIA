from unittest.mock import Mock
import pytest
from apps.chat.models import ChatSession, SenderTypeChoices
from apps.chat.services import ChatService
from ia.rag.response import RAGResponse, RAGSource


@pytest.mark.django_db
def test_chat_service_process_user_message():
    mock_rag = Mock()
    mock_rag.query.return_value = RAGResponse(
        content="Resposta oficial fundamentada com CPF.",
        sources=[RAGSource(title="Guia CPF", url="https://www.gov.br/cpf", source_type="LOCAL")],
        language_detected="pt",
        golden_rule_triggered=False,
    )

    service = ChatService(rag_pipeline=mock_rag)
    session = ChatSession.objects.create(ui_language="pt")

    user_msg, assistant_msg = service.process_user_message(
        session=session,
        content="Meu CPF é 123.456.789-00, como renovo?"
    )

    # Verifica sanitização LGPD
    assert "[CPF_REDACTED]" in user_msg.content
    assert "123.456.789-00" not in user_msg.content

    # Verifica resposta do assistente e vínculo reply_to
    assert assistant_msg.content == "Resposta oficial fundamentada com CPF."
    assert assistant_msg.reply_to == user_msg
    assert user_msg.replies.first() == assistant_msg
    assert len(assistant_msg.sources_cited) == 1
    assert assistant_msg.sources_cited[0]["url"] == "https://www.gov.br/cpf"
    assert session.messages.count() == 2


@pytest.mark.django_db
def test_chat_service_submit_feedback():
    service = ChatService()
    session = ChatSession.objects.create(ui_language="pt")
    
    assistant_msg = session.messages.create(
        sender_type=SenderTypeChoices.ASSISTANT,
        content="Resposta do assistente"
    )
    
    feedback = service.submit_feedback(
        message=assistant_msg,
        rating=1,
        comment="Excelente!"
    )
    assert feedback.rating == 1
    assert feedback.comment == "Excelente!"
