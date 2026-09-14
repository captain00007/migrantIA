"""
Módulo de Recuperação (Retrievers) do MigrantIA.
Fornece retrievers semânticos (.as_retriever via PGVector) e híbridos com RRF (Reciprocal Rank Fusion).
"""
import logging
from typing import Optional, List, Dict, Any
from collections import defaultdict

from pydantic import Field
from langchain_core.retrievers import BaseRetriever
from langchain_core.documents import Document
from langchain_core.callbacks import CallbackManagerForRetrieverRun
from langchain_community.retrievers import BM25Retriever

from ia.retrieval.vectorstore import get_vector_store, DEFAULT_COLLECTION_NAME

logger = logging.getLogger(__name__)


class EnsembleHybridRetriever(BaseRetriever):
    """
    Retriever Hébrido que combina múltiplos retrievers (ex: Vetorial + BM25)
    utilizando o algoritmo de Reciprocal Rank Fusion (RRF).
    """
    retrievers: List[BaseRetriever]
    weights: List[float] = Field(default_factory=lambda: [0.6, 0.4])
    c: int = 60
    k: int = 4

    def _get_relevant_documents(
        self,
        query: str,
        *,
        run_manager: Optional[CallbackManagerForRetrieverRun] = None,
    ) -> List[Document]:
        doc_lists: List[List[Document]] = [
            retriever.invoke(query) for retriever in self.retrievers
        ]

        rrf_scores: Dict[str, float] = defaultdict(float)
        all_docs: Dict[str, Document] = {}

        for weight, docs in zip(self.weights, doc_lists):
            for rank, doc in enumerate(docs):
                doc_key = doc.page_content.strip()
                all_docs[doc_key] = doc
                rrf_scores[doc_key] += weight / (self.c + rank + 1)

        sorted_keys = sorted(rrf_scores.keys(), key=lambda k: rrf_scores[k], reverse=True)
        return [all_docs[key] for key in sorted_keys[: self.k]]


def get_vector_retriever(
    k: int = 4,
    pillar: Optional[str] = None,
    collection_name: str = DEFAULT_COLLECTION_NAME,
    search_type: str = "similarity",
    score_threshold: Optional[float] = None,
    **search_kwargs: Any,
) -> BaseRetriever:
    """
    Retorna o retriever vetorial nativo do PGVector (.as_retriever).
    """
    vectorstore = get_vector_store(collection_name=collection_name)
    
    kwargs: Dict[str, Any] = {"k": k, **search_kwargs}
    if pillar:
        kwargs["filter"] = {"pillar": pillar}
    if score_threshold is not None:
        kwargs["score_threshold"] = score_threshold
        search_type = "similarity_score_threshold"
    return vectorstore.as_retriever(
        search_type=search_type,
        search_kwargs=kwargs,
    )


def get_hybrid_retriever(
    documents: Optional[List[Document]] = None,
    k: int = 4,
    pillar: Optional[str] = None,
    weights: Optional[List[float]] = None,
    collection_name: str = DEFAULT_COLLECTION_NAME,
) -> BaseRetriever:
    """
    Cria e retorna um Retriever Híbrido combinando:
    1. Busca Semântica Vetorial (PGVector)
    2. Busca Léxica por Palavras-Chave e Siglas (BM25)
    FusÃo realizada através de Reciprocal Rank Fusion (RRF).
    """
    weights_list = weights if weights is not None  else [0.6, 0.4]

    vector_retriever = get_vector_retriever(
        k=k,
        pillar=pillar,
        collection_name=collection_name,
    )

    if not documents:
        return vector_retriever

    if pillar:
        bm25_docs = [doc for doc in documents if doc.metadata.get("pillar") == pillar]
    else:
        bm25_docs = documents

    if not bm25_docs:
        return vector_retriever

    bm25_retriever = BM25Retriever.from_documents(bm25_docs, k=k)

    return EnsembleHybridRetriever(
        retrievers=[vector_retriever, bm25_retriever],
        weights=weights_list,
        k=k,
    )
