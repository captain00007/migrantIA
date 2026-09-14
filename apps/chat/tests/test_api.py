from unittest.mock import Mock, patch
import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from apps.chat.models import ChatSession, ChatMessage, SenderTypeChoices
from ia.rag.response import RAGResponse, RAGSource


@pytest.fixture
def api_client():
    return APIClient()


@pytest.mark.django_db
def test_api_create_session(api_client):
    url = reverse("chat:session-list-create")
    payload = {
        "ui_language": "ht",
        "primary_pillar": "IMMIGRATION",
        "metadata": {"device": "mobile"}
    }
    response = api_client.post(url, data=payload, format="json")
    assert response.status_code == 201
    assert response.data["ui_language"] == "ht"
    assert response.data["primary_pillar"] == "IMMIGRATION"
    assert "id" in response.data


@pytest.mark.django_db
def test_api_get_session_detail(api_client):
    session = ChatSession.objects.create(ui_language="fr")
    url = reverse("chat:session-detail", kwargs={"session_id": str(session.id)})
    response = api_client.get(url)
    assert response.status_code == 200
    assert response.data["id"] == str(session.id)
    assert response.data["ui_language"] == "fr"


@pytest.mark.django_db
@patch("apps.chat.services.ChatService.rag_pipeline")
def test_api_send_message_and_receive_rag(mock_rag_pipeline_prop, api_client):
    mock_rag = Mock()
    mock_rag.query.return_value = RAGResponse(
        content="Instruções para solicitar refúgio.",
        sources=[RAGSource(title="CONARE", url="https://www.gov.br/conare", source_type="LOCAL")],
        language_detected="pt",
        golden_rule_triggered=False
    )
    mock_rag_pipeline_prop.__get__ = Mock(return_value=mock_rag)

    session = ChatSession.objects.create(ui_language="pt")
    url = reverse("chat:session-messages", kwargs={"session_id": str(session.id)})

    payload = {
        "content": "Como pedir refúgio no Brasil? Meu CPF é 111.222.333-44",
        "pillar": "IMMIGRATION"
    }
    response = api_client.post(url, data=payload, format="json")
    assert response.status_code == 200
    assert "user_message" in response.data
    assert "assistant_message" in response.data
    assert "[CPF_REDACTED]" in response.data["user_message"]["content"]
    assert "Instruções para solicitar refúgio." in response.data["assistant_message"]["content"]
    assert len(response.data["assistant_message"]["sources_cited"]) == 1


@pytest.mark.django_db
def test_api_submit_feedback(api_client):
    session = ChatSession.objects.create(ui_language="pt")
    assistant_msg = ChatMessage.objects.create(
        session=session,
        sender_type=SenderTypeChoices.ASSISTANT,
        content="Resposta informativa"
    )
    url = reverse("chat:message-feedback", kwargs={"message_id": str(assistant_msg.id)})

    payload = {
        "rating": 1,
        "comment": "Muito útil, obrigado!"
    }
    response = api_client.post(url, data=payload, format="json")
    assert response.status_code == 201
    assert response.data["rating"] == 1
    assert response.data["comment"] == "Muito útil, obrigado!"
