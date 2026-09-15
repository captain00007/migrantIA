import pytest
from apps.chat.models import (
    ChatSession,
    ChatMessage,
    MessageFeedback,
    SenderTypeChoices,
    FeedbackRatingChoices,
)
from apps.sources.models import PillarChoices


@pytest.mark.django_db
def test_create_chat_session():
    session = ChatSession.objects.create(
        ui_language="ht",
        primary_pillar=PillarChoices.IMMIGRATION,
        metadata={"platform": "PWA"}
    )
    assert session.id is not None
    assert session.ui_language == "ht"
    assert session.primary_pillar == PillarChoices.IMMIGRATION
    assert session.is_active is True


@pytest.mark.django_db
def test_create_chat_messages_and_feedback():
    session = ChatSession.objects.create(ui_language="pt")
    
    user_msg = ChatMessage.objects.create(
        session=session,
        sender_type=SenderTypeChoices.USER,
        content="Como emitir o CPF?"
    )
    
    assistant_msg = ChatMessage.objects.create(
        session=session,
        reply_to=user_msg,
        sender_type=SenderTypeChoices.ASSISTANT,
        content="O CPF pode ser emitido na Receita Federal.",
        sources_cited=[{"title": "Receita Federal", "url": "https://www.gov.br/receita"}],
        golden_rule_triggered=False
    )
    
    assert session.messages.count() == 2
    assert assistant_msg.reply_to == user_msg
    assert user_msg.replies.count() == 1
    assert user_msg.replies.first() == assistant_msg
    assert assistant_msg.sources_cited[0]["url"] == "https://www.gov.br/receita"
    
    feedback = MessageFeedback.objects.create(
        message=assistant_msg,
        rating=FeedbackRatingChoices.POSITIVE,
        comment="Muito clara a resposta!"
    )
    
    assert assistant_msg.feedback == feedback
    assert feedback.rating == 1
