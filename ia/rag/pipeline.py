"""
Pipeline RAG Auditado e Estrito do MigrantIA.
Implementa o fluxo de recuperação em 3 passos com avaliação dinâmica de relevância
(Score Threshold) no banco vetorial e respostas fluidas orientadas pelo LLM.
"""
import logging
from typing import Dict, Any, List, Optional, Tuple
from langchain_core.documents import Document
from langchain_core.language_models.chat_models import BaseChatModel

from ia.llm.factory import get_llm
from ia.retrieval.vectorstore import get_vector_store
from ia.retrieval.search import WhitelistSearchTool, get_search_tool
from ia.prompts.multilingual import (
    get_golden_rule_fallback,
    detect_language_heuristic,
    DEFAULT_LANGUAGE,
)
from ia.rag.chain import create_rag_chain
from ia.rag.response import RAGResponse, RAGSource

logger = logging.getLogger(__name__)

# Limiar de distância de cosseno: distâncias acima de 0.60 indicam baixa similaridade semântica
MAX_DISTANCE_THRESHOLD: float = 0.60


class RAGPipeline:
    """
    Pipeline RAG dinâmico e auditado do MigrantIA.
    """

    def __init__(
        self,
        llm: Optional[BaseChatModel] = None,
        vector_store: Optional[Any] = None,
        search_tool: Optional[WhitelistSearchTool] = None,
    ):
        self.llm = llm or get_llm(temperature=0.0)
        self.vector_store = vector_store
        self.search_tool = search_tool or get_search_tool()
        self.chain = create_rag_chain(llm=self.llm)

    def get_vector_store(self) -> Any:
        """Obtém ou inicializa o vector store do PGVector."""
        if self.vector_store is None:
            self.vector_store = get_vector_store()
        return self.vector_store

    def step_1_local_retrieval(
        self,
        query: str,
        pillar_filter: Optional[str] = None
    ) -> List[Document]:
        """
        Passo 1: Busca vetorial no PGVector filtrada dinamicamente por relevância semântica.
        Descarta automaticamente documentos irrelevantes para a mensagem atual.
        """
        try:
            vs = self.get_vector_store()
            results = vs.similarity_search_with_score(query, k=4)
            
            relevant_docs: List[Document] = []
            for doc, distance in results:
                # Apenas aceita documentos com real correlação semântica
                if distance <= MAX_DISTANCE_THRESHOLD:
                    if pillar_filter and doc.metadata.get("pillar") != pillar_filter:
                        continue
                    relevant_docs.append(doc)
            
            return relevant_docs
        except Exception as e:
            logger.error(f"[RAG Step 1] Erro na recuperação vetorial com score: {e}")
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

    def format_context(
        self,
        local_docs: List[Document],
        web_results: List[Dict[str, Any]]
    ) -> str:
        """Formata o contexto oficial agregado para injeção no prompt."""
        if not local_docs and not web_results:
            return "(Nenhum documento oficial específico anexado para esta mensagem)"

        blocks = []
        for i, doc in enumerate(local_docs, 1):
            title = doc.metadata.get("title", f"Documento Local {i}")
            url = doc.metadata.get("url", "")
            page = doc.metadata.get("page")
            page_label = doc.metadata.get("page_label")

            page_info = ""
            if page_label is not None:
                page_info = f" | Página {page_label}"
            elif page is not None:
                page_num = page + 1 if isinstance(page, int) else page
                page_info = f" | Página {page_num}"

            url_str = f" ({url})" if url else ""
            blocks.append(f"--- Fonte Local [{i}]: {title}{page_info}{url_str} ---\n{doc.page_content}")

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
        """Extrai a lista de fontes estruturadas citadas, deduplicando por documento e consolidando páginas."""
        if not local_docs and not web_results:
            return []

        grouped_local: Dict[Tuple[str, str], Dict[str, Any]] = {}

        for doc in local_docs:
            title = doc.metadata.get("title", "Documento Oficial")
            url = doc.metadata.get("url", "")
            pillar = doc.metadata.get("pillar")
            page = doc.metadata.get("page")
            page_label = doc.metadata.get("page_label")

            page_num: Optional[int] = None
            if page_label is not None:
                try:
                    page_num = int(page_label)
                except (ValueError, TypeError):
                    pass
            elif page is not None:
                try:
                    page_num = int(page) + 1
                except (ValueError, TypeError):
                    pass

            key = (title, url)
            if key not in grouped_local:
                grouped_local[key] = {
                    "title": title,
                    "url": url,
                    "snippet": doc.page_content[:200],
                    "source_type": "LOCAL",
                    "pillar": pillar,
                    "pages": set(),
                }
            if page_num is not None:
                grouped_local[key]["pages"].add(page_num)

        sources: List[RAGSource] = []
        for item in grouped_local.values():
            sorted_pages = sorted(list(item["pages"]))
            first_page = sorted_pages[0] if sorted_pages else None
            sources.append(
                RAGSource(
                    title=item["title"],
                    url=item["url"],
                    snippet=item["snippet"],
                    source_type=item["source_type"],
                    pillar=item["pillar"],
                    page=first_page,
                    pages=sorted_pages,
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
        Executa o fluxo RAG completo:
        1. Avalia dinamicamente a relevância no banco vetorial.
        2. Injeta documentos no contexto apenas se forem semanticamente relevantes.
        3. Invoca o modelo LLM com o histórico de conversa de forma dinâmica.
        """
        clean_question = (question or "").strip()
        if not clean_question:
            lang = ui_language or DEFAULT_LANGUAGE
            return RAGResponse(
                content="Por favor, digite sua dúvida ou selecione um dos tópicos de ajuda."
                if lang == "pt"
                else get_golden_rule_fallback(lang),
                language_detected=lang,
                golden_rule_triggered=False,
            )

        detected_lang = ui_language or detect_language_heuristic(clean_question)

        # 1. Recuperação Vetorial com Filtro de Relevância
        local_docs = self.step_1_local_retrieval(clean_question, pillar_filter=pillar_filter)

        # 2. Formatação do contexto e extração de fontes
        context_text = self.format_context(local_docs, [])
        sources = self.extract_sources(local_docs, [])

        # 3. Execução da cadeia LangChain com LLM e histórico
        try:
            raw_response = self.chain.invoke({
                "context": context_text,
                "question": clean_question,
                "chat_history": chat_history or [],
            })

            return RAGResponse(
                content=raw_response,
                sources=sources,
                language_detected=detected_lang,
                golden_rule_triggered=False,
                metadata={
                    "local_docs_count": len(local_docs),
                    "has_context": len(local_docs) > 0,
                }
            )
        except Exception as e:
            logger.error(f"[RAG] Erro na invocação da LLM: {e}")
            return RAGResponse(
                content=get_golden_rule_fallback(detected_lang),
                sources=[],
                language_detected=detected_lang,
                golden_rule_triggered=True,
                metadata={"error": str(e)}
            )


def get_rag_pipeline(
    llm: Optional[BaseChatModel] = None,
    vector_store: Optional[Any] = None,
    search_tool: Optional[WhitelistSearchTool] = None,
) -> RAGPipeline:
    """Retorna uma instância configurada do pipeline RAG."""
    return RAGPipeline(llm=llm, vector_store=vector_store, search_tool=search_tool)
