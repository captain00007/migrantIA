"""
Orquestrador do Fluxo RAG em 3 Passos do MigrantIA.
Passo 1: Recuperação Híbrida Local (PostgreSQL/pgvector).
Passo 2: Busca Externa com Whitelist Estrita (se local insuficiente).
Passo 3: Regra de Ouro da Transparência & Contatos Comunitários (fallback se sem evidências).
"""
import logging
from typing import List, Dict, Any, Optional
from langchain_core.documents import Document
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.retrievers import BaseRetriever

from ia.llm.factory import get_llm
from ia.retrieval.retriever import get_hybrid_retriever
from ia.retrieval.search import WhitelistSearchTool, get_search_tool
from ia.prompts.multilingual import (
    get_golden_rule_fallback,
    detect_language_heuristic,
    DEFAULT_LANGUAGE,
)
from ia.rag.chain import create_rag_chain
from ia.rag.response import RAGResponse, RAGSource

logger = logging.getLogger(__name__)


class RAGPipeline:
    """
    Pipeline RAG auditado e estrito do MigrantIA.
    """

    def __init__(
        self,
        llm: Optional[BaseChatModel] = None,
        retriever: Optional[BaseRetriever] = None,
        search_tool: Optional[WhitelistSearchTool] = None,
    ):
        self.llm = llm or get_llm(temperature=0.0)
        self.retriever = retriever
        self.search_tool = search_tool or get_search_tool()
        self.chain = create_rag_chain(llm=self.llm)

    def get_retriever(self) -> BaseRetriever:
        """Obtém ou inicializa o retriever híbrido."""
        if self.retriever is None:
            self.retriever = get_hybrid_retriever()
        return self.retriever

    def step_1_local_retrieval(
        self,
        query: str,
        pillar_filter: Optional[str] = None
    ) -> List[Document]:
        """
        Passo 1: Recupera documentos locais do PGVector com busca híbrida.
        """
        try:
            retriever = self.get_retriever()
            docs = retriever.invoke(query)
            if pillar_filter and docs:
                docs = [
                    d for d in docs
                    if d.metadata.get("pillar") == pillar_filter
                ]
            return docs
        except Exception as e:
            logger.error(f"[RAG Step 1] Erro na recuperação local: {e}")
            return []

    def step_2_whitelist_search(
        self,
        query: str
    ) -> List[Dict[str, Any]]:
        """
        Passo 2: Executa busca externa estritamente na whitelist de domínios homologados.
        """
        try:
            if not self.search_tool:
                return []
            return self.search_tool.search(query=query, max_results=3)
        except Exception as e:
            logger.error(f"[RAG Step 2] Erro na busca whitelist: {e}")
            return []

    def step_3_golden_rule_fallback(
        self,
        language: str = DEFAULT_LANGUAGE
    ) -> RAGResponse:
        """
        Passo 3: Aplica a Regra de Ouro com mensagem transparente no idioma do usuário
        e contatos de suporte de parceiros comunitários e defensorias.
        """
        message = get_golden_rule_fallback(language)
        return RAGResponse(
            content=message,
            sources=[],
            language_detected=language,
            golden_rule_triggered=True,
            metadata={"step": 3, "reason": "No validated official evidence found"}
        )

    def format_context(
        self,
        local_docs: List[Document],
        web_results: List[Dict[str, Any]]
    ) -> str:
        """Formata o contexto oficial agregado para injeção no prompt."""
        blocks = []
        for i, doc in enumerate(local_docs, 1):
            title = doc.metadata.get("title", f"Documento Local {i}")
            url = doc.metadata.get("url", "")
            url_str = f" ({url})" if url else ""
            blocks.append(f"--- Fonte Local [{i}]: {title}{url_str} ---\n{doc.page_content}")

        for j, res in enumerate(web_results, 1):
            title = res.get("title", f"Fonte Web {j}")
            url = res.get("url", "")
            content = res.get("content", "")
            blocks.append(f"--- Fonte Web Homologada [{j}]: {title} ({url}) ---\n{content}")

        return "\n\n".join(blocks)

    def extract_sources(
        self,
        local_docs: List[Document],
        web_results: List[Dict[str, Any]]
    ) -> List[RAGSource]:
        """Extrai a lista de fontes estruturadas citadas."""
        sources: List[RAGSource] = []
        for doc in local_docs:
            sources.append(
                RAGSource(
                    title=doc.metadata.get("title", "Documento Oficial"),
                    url=doc.metadata.get("url", ""),
                    snippet=doc.page_content[:200],
                    source_type="LOCAL",
                    pillar=doc.metadata.get("pillar"),
                )
            )

        for res in web_results:
            sources.append(
                RAGSource(
                    title=res.get("title", "Portal Governamental/ONG"),
                    url=res.get("url", ""),
                    snippet=res.get("content", "")[:200],
                    source_type="WEB",
                )
            )
        return sources

    def query(
        self,
        question: str,
        ui_language: Optional[str] = None,
        chat_history: Optional[List[Any]] = None,
        pillar_filter: Optional[str] = None,
    ) -> RAGResponse:
        """
        Executa o fluxo RAG completo em 3 passos para uma pergunta do usuário.
        """
        if not question or not question.strip():
            lang = ui_language or DEFAULT_LANGUAGE
            return RAGResponse(
                content="Por favor, digite sua dúvida ou selecione um dos tópicos de ajuda."
                if lang == "pt"
                else get_golden_rule_fallback(lang),
                language_detected=lang,
                golden_rule_triggered=False,
            )

        detected_lang = ui_language or detect_language_heuristic(question)

        # PASSO 1: Busca Híbrida Local
        local_docs = self.step_1_local_retrieval(question, pillar_filter=pillar_filter)

        # PASSO 2: Busca Externa com Whitelist (se local vazio)
        web_results: List[Dict[str, Any]] = []
        if not local_docs:
            logger.info(f"[RAG] Nenhuma evidência local para '{question}'. Iniciando Passo 2 (Whitelist Web).")
            web_results = self.step_2_whitelist_search(question)

        # PASSO 3: Regra de Ouro (se nenhuma evidência oficial encontrada)
        if not local_docs and not web_results:
            logger.warning(f"[RAG] Nenhuma evidência oficial encontrada para '{question}'. Acionando Passo 3.")
            return self.step_3_golden_rule_fallback(detected_lang)

        # GERAÇÃO FUNDAMENTADA
        context_text = self.format_context(local_docs, web_results)
        sources = self.extract_sources(local_docs, web_results)

        try:
            raw_response = self.chain.invoke({
                "context": context_text,
                "question": question,
                "chat_history": chat_history or [],
            })

            return RAGResponse(
                content=raw_response,
                sources=sources,
                language_detected=detected_lang,
                golden_rule_triggered=False,
                metadata={
                    "step": 1 if local_docs else 2,
                    "local_docs_count": len(local_docs),
                    "web_results_count": len(web_results),
                }
            )
        except Exception as e:
            logger.error(f"[RAG] Erro na invocação da LLM: {e}")
            return self.step_3_golden_rule_fallback(detected_lang)


def get_rag_pipeline(
    llm: Optional[BaseChatModel] = None,
    retriever: Optional[BaseRetriever] = None,
    search_tool: Optional[WhitelistSearchTool] = None,
) -> RAGPipeline:
    """Retorna uma instância configurada do pipeline RAG."""
    return RAGPipeline(llm=llm, retriever=retriever, search_tool=search_tool)
