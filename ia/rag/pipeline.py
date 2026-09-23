"""
Pipeline RAG Defense-in-Depth do MigrantIA com Roteamento Semântico Dinâmico.
1. Normalização de Entrada (NFKC + Homoglyphs + Zero-Width Strip)
2. Detecção de Codificações Adversárias (Base64/Hex) & InjectionGuard
3. PII Masking (LGPD)
4. Recuperação Vetorial Segura (PGVector com Score Threshold <= 0.60 & Whitelist Search)
5. ContextShield: Encapsulamento XML/CDATA (Data vs. Instructions)
6. Execução Semântica Unificada do LLM (Canary Token Efêmero + Decisão Contextual Dinâmica)
7. OutputGuard: Anti-Exfiltração Markdown, HTML Stripper, Link Sanitizer e Canary Scan
"""
import logging
from typing import Dict, Any, List, Optional, Tuple
from langchain_core.documents import Document
from langchain_core.language_models.chat_models import BaseChatModel

from ia.llm.factory import get_llm
from ia.retrieval.vectorstore import get_vector_store
from ia.retrieval.search import WhitelistSearchTool, get_search_tool
from ia.guardrails import InputModerator
from ia.security import (
    CanaryManager,
    OutputGuard,
    ContextShield,
    log_security_event,
)
from ia.prompts.refusals import (
    get_refusal_message,
    RefusalReason,
    DEFAULT_LANGUAGE,
)
from ia.prompts.multilingual import detect_language_heuristic
from ia.rag.chain import create_rag_chain
from ia.rag.response import RAGResponse, RAGSource

logger = logging.getLogger(__name__)

# Limiar de distância de cosseno: distâncias acima de 0.60 indicam baixa similaridade semântica
MAX_DISTANCE_THRESHOLD: float = 0.60


class RAGPipeline:
    """
    Pipeline RAG dinâmico, seguro e auditado do MigrantIA.
    """

    def __init__(
        self,
        llm: Optional[BaseChatModel] = None,
        vector_store: Optional[Any] = None,
        retriever: Optional[Any] = None,
        search_tool: Optional[WhitelistSearchTool] = None,
        moderator: Optional[InputModerator] = None,
        output_guard: Optional[OutputGuard] = None,
    ):
        self.llm = llm or get_llm(temperature=0.0)
        self.vector_store = vector_store
        self.retriever = retriever
        self.search_tool = search_tool or get_search_tool()
        self.moderator = moderator or InputModerator()
        self.output_guard = output_guard or OutputGuard()
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
            if self.retriever is not None:
                if hasattr(self.retriever, "invoke"):
                    docs = self.retriever.invoke(query)
                elif hasattr(self.retriever, "get_relevant_documents"):
                    docs = self.retriever.get_relevant_documents(query)
                else:
                    docs = []
                if pillar_filter:
                    docs = [d for d in docs if d.metadata.get("pillar") == pillar_filter]
                return docs

            vs = self.get_vector_store()
            results = vs.similarity_search_with_score(query, k=4)

            relevant_docs: List[Document] = []
            for doc, distance in results:
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

    def _execute_llm_with_guard(
        self,
        context_xml: str,
        user_query_xml: str,
        chat_history: Optional[List[Any]] = None,
        canary_token: Optional[str] = None,
        ui_language: str = DEFAULT_LANGUAGE,
    ) -> Tuple[str, bool, Optional[str]]:
        """
        Executa o LLM com contexto isolado e passa a resposta pelo OutputGuard.
        Retorna (sanitized_response, is_safe, violation_reason).
        """
        raw_response = self.chain.invoke({
            "context": context_xml,
            "question": user_query_xml,
            "chat_history": chat_history or [],
        })

        # Camada de Segurança pós-geração (OutputGuard)
        clean_response, is_safe, reason = self.output_guard.sanitize(
            output_text=raw_response,
            canary_token=canary_token
        )

        if not is_safe:
            log_security_event(
                event_type="OUTPUT_VIOLATION_BLOCKED",
                reason=reason,
                step=10,
            )
            return get_refusal_message(RefusalReason.SECURITY_VIOLATION, ui_language=ui_language), False, reason

        return clean_response, True, None

    def query(
        self,
        question: str,
        ui_language: Optional[str] = None,
        chat_history: Optional[List[Any]] = None,
        pillar_filter: Optional[str] = None,
    ) -> RAGResponse:
        """
        Executa o pipeline RAG completo em abordagem semântica unificada.
        """
        clean_question = (question or "").strip()
        effective_ui_lang = (ui_language or DEFAULT_LANGUAGE).lower()[:2]

        if not clean_question:
            return RAGResponse(
                content="Por favor, digite sua dúvida ou selecione um dos tópicos de ajuda."
                if effective_ui_lang == "pt"
                else get_refusal_message(RefusalReason.GOLDEN_RULE, ui_language=effective_ui_lang),
                language_detected=effective_ui_lang,
                golden_rule_triggered=False,
                metadata={"step": 0}
            )

        detected_lang = detect_language_heuristic(clean_question)

        # 1. Moderação e Segurança de Entrada (Normalização Unicode, PII, InjectionGuard)
        guard_result = self.moderator.inspect(clean_question, ui_language=effective_ui_lang)

        # Bloqueio Imediato de Prompt Injection / Ataque Adversário
        if not guard_result.is_safe:
            log_security_event(
                event_type="PROMPT_INJECTION_BLOCKED",
                raw_input=clean_question,
                reason=guard_result.reason,
                step=0,
            )
            return RAGResponse(
                content=guard_result.refusal_message or get_refusal_message(RefusalReason.SECURITY_VIOLATION, ui_language=effective_ui_lang),
                sources=[],
                language_detected=detected_lang,
                golden_rule_triggered=False,
                metadata={
                    "step": 0,
                    "blocked_by": "injection_guard",
                    "reason": guard_result.reason,
                }
            )

        # 2. Busca Vetorial Local com Score Threshold
        local_docs = self.step_1_local_retrieval(guard_result.sanitized_text, pillar_filter=pillar_filter)
        web_results = []
        step_used = 1

        if local_docs:
            context_xml = ContextShield.build_isolated_context(local_docs, [])
            sources = self.extract_sources(local_docs, [])
            step_used = 1
        else:
            # Tenta busca externa na whitelist se configurada
            web_results = self.step_2_whitelist_search(guard_result.sanitized_text)
            if web_results:
                context_xml = ContextShield.build_isolated_context([], web_results)
                sources = self.extract_sources([], web_results)
                step_used = 2
            else:
                # Sem documentos locais nem web: contexto vai vazio de forma limpa
                context_xml = ContextShield.build_isolated_context([], [])
                sources = []
                step_used = 3

        # 3. Geração Semântica Unificada no LLM
        user_query_xml = ContextShield.format_user_query(guard_result.sanitized_text)
        canary_token = CanaryManager.generate_token()

        try:
            response_text, is_safe, reason = self._execute_llm_with_guard(
                context_xml=context_xml,
                user_query_xml=user_query_xml,
                chat_history=chat_history,
                canary_token=canary_token,
                ui_language=effective_ui_lang,
            )

            # Verifica se o modelo acionou a Regra de Ouro (transparência quando não encontra)
            is_golden_rule = (
                step_used == 3
                and not sources
                and any(
                    phrase in response_text.lower()
                    for phrase in [
                        "não encontrei essa informação",
                        "no encontré esta información",
                        "i did not find this information",
                        "je n'ai pas trouvé",
                        "mwen pa jwenn",
                    ]
                )
            )

            return RAGResponse(
                content=response_text,
                sources=sources,
                language_detected=detected_lang,
                golden_rule_triggered=is_golden_rule,
                metadata={
                    "step": step_used,
                    "local_docs_count": len(local_docs),
                    "web_results_count": len(web_results),
                    "has_context": len(local_docs) > 0 or len(web_results) > 0,
                }
            )
        except Exception as e:
            logger.error(f"[RAG Execution] Erro na execução da LLM: {e}")
            return RAGResponse(
                content=get_refusal_message(RefusalReason.GOLDEN_RULE, ui_language=effective_ui_lang),
                sources=[],
                language_detected=detected_lang,
                golden_rule_triggered=True,
                metadata={"step": 3, "error": str(e)}
            )


def get_rag_pipeline(
    llm: Optional[BaseChatModel] = None,
    vector_store: Optional[Any] = None,
    retriever: Optional[Any] = None,
    search_tool: Optional[WhitelistSearchTool] = None,
    moderator: Optional[InputModerator] = None,
    output_guard: Optional[OutputGuard] = None,
) -> RAGPipeline:
    """Retorna uma instância configurada do pipeline RAG."""
    return RAGPipeline(
        llm=llm,
        vector_store=vector_store,
        retriever=retriever,
        search_tool=search_tool,
        moderator=moderator,
        output_guard=output_guard,
    )
