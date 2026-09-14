from unittest.mock import Mock, patch
import pytest
from langchain_core.documents import Document
from langchain_core.language_models.chat_models import BaseChatModel
from ia.rag.pipeline import RAGPipeline, get_rag_pipeline
from ia.rag.response import RAGResponse


class DummyChatModel(BaseChatModel):
    response_text: str = "Resposta oficial fundamentada."

    def _generate(self, messages, stop=None, run_manager=None, **kwargs):
        from langchain_core.outputs import ChatGeneration, ChatResult
        from langchain_core.messages import AIMessage
        return ChatResult(generations=[ChatGeneration(message=AIMessage(content=self.response_text))])

    @property
    def _llm_type(self) -> str:
        return "dummy"


def test_rag_pipeline_step_1_local_evidence():
    dummy_llm = DummyChatModel(response_text="O CPF pode ser emitido na Receita Federal.")
    dummy_retriever = Mock()
    dummy_retriever.invoke.return_value = [
        Document(
            page_content="Instruções da Receita Federal sobre CPF.",
            metadata={"title": "Guia CPF", "url": "https://www.gov.br/receita", "pillar": "IMMIGRATION"}
        )
    ]
    pipeline = RAGPipeline(llm=dummy_llm, retriever=dummy_retriever)
    response = pipeline.query("Como tirar CPF?", ui_language="pt")

    assert isinstance(response, RAGResponse)
    assert response.golden_rule_triggered is False
    assert "Receita Federal" in response.content
    assert len(response.sources) == 1
    assert response.sources[0].url == "https://www.gov.br/receita"
    assert response.metadata["step"] == 1


def test_rag_pipeline_step_2_whitelist_search_fallback():
    dummy_llm = DummyChatModel(response_text="Conforme o portal oficial, o agendamento é online.")
    dummy_retriever = Mock()
    dummy_retriever.invoke.return_value = []  # Local vazio

    dummy_search = Mock()
    dummy_search.search.return_value = [
        {
            "title": "Portal Polícia Federal",
            "url": "https://www.gov.br/pf/pt-br/assuntos/imigracao",
            "content": "Agendamento de atendimento presencial para imigrantes.",
            "score": 0.95
        }
    ]

    pipeline = RAGPipeline(llm=dummy_llm, retriever=dummy_retriever, search_tool=dummy_search)
    response = pipeline.query("Como agendar na PF?", ui_language="pt")

    assert isinstance(response, RAGResponse)
    assert response.golden_rule_triggered is False
    assert len(response.sources) == 1
    assert response.sources[0].source_type == "WEB"
    assert response.sources[0].url == "https://www.gov.br/pf/pt-br/assuntos/imigracao"
    assert response.metadata["step"] == 2


def test_rag_pipeline_step_3_golden_rule():
    dummy_llm = DummyChatModel()
    dummy_retriever = Mock()
    dummy_retriever.invoke.return_value = []

    dummy_search = Mock()
    dummy_search.search.return_value = []

    pipeline = RAGPipeline(llm=dummy_llm, retriever=dummy_retriever, search_tool=dummy_search)
    response = pipeline.query("Pergunta desconhecida sem evidências", ui_language="ht")

    assert isinstance(response, RAGResponse)
    assert response.golden_rule_triggered is True
    assert "Mwen pa jwenn" in response.content
    assert len(response.sources) == 0
    assert response.metadata["step"] == 3


def test_rag_pipeline_empty_query():
    pipeline = get_rag_pipeline(llm=DummyChatModel())
    response = pipeline.query("")
    assert "digite sua dúvida" in response.content
