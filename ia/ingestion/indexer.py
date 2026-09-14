"""
Orquestrador de indexação no PostgreSQL com PGVector para os 4 Pilares do MigrantIA.
Salva metadados em KnowledgeDocument (Django) e delega o armazenamento, embeddings
e busca vetorial de chunks diretamente ao PGVector (vectorstore).
"""
import logging
from typing import Dict, Any, List, Optional
from django.db import transaction
from langchain_core.documents import Document

from apps.sources.models import PillarChoices, OfficialSource
from apps.knowledge.models import KnowledgeDocument, DocumentTypeChoices
from ia.ingestion.splitter import BaseDocumentSplitter, DocumentSplitter
from ia.retrieval.vectorstore import get_vector_store

logger = logging.getLogger(__name__)


class KnowledgeIndexer:
    """
    Orquestrador de indexação para os 4 Pilares de Conhecimento do MigrantIA.
    """

    def __init__(
        self,
        splitter: Optional[BaseDocumentSplitter] = None,
        vector_store: Optional[Any] = None,
    ):
        self.splitter = splitter or DocumentSplitter()
        self._vector_store = vector_store

    @property
    def vector_store(self) -> Any:
        """Inicializa ou obtém a instância do PGVector sob demanda."""
        if self._vector_store is None:
            self._vector_store = get_vector_store()
        return self._vector_store

    @vector_store.setter
    def vector_store(self, val: Any) -> None:
        self._vector_store = val

    def index_documents(
        self,
        documents: List[Document],
        pillar: str = PillarChoices.IMMIGRATION,
        source: Optional[OfficialSource] = None,
        title: Optional[str] = None,
        url: Optional[str] = None,
        document_type: str = DocumentTypeChoices.GUIDE,
        content_hash: str = "",
    ) -> int:
        """
        Indexa documentos:
        1. Cria ou atualiza o registro KnowledgeDocument no Django (apenas metadados do catálogo).
        2. Divide os documentos em fragmentos textuais (chunks).
        3. Envia os fragmentos e metadados contextuais diretamente para o PGVector.
        """
        if not documents:
            return 0

        # 1. Salvar metadados no catálogo Django
        doc_title = title or (documents[0].metadata.get("title") if documents else "Documento Oficial")
        doc_url = url or (documents[0].metadata.get("url") if documents else "")

        with transaction.atomic():
            knowledge_doc, _ = KnowledgeDocument.objects.update_or_create(
                title=doc_title,
                pillar=pillar,
                defaults={
                    "source": source,
                    "document_type": document_type,
                    "url": doc_url,
                    "content_hash": content_hash,
                }
            )

            # 2. Dividir documentos
            chunks = self.splitter.split_documents(documents)
            for chunk in chunks:
                chunk.metadata.update({
                    "knowledge_document_id": knowledge_doc.id,
                    "pillar": pillar,
                    "title": doc_title,
                    "url": doc_url,
                    "document_type": document_type,
                })

            # 3. Armazenar no PGVector
            if chunks:
                self.vector_store.add_documents(chunks)
                logger.info(
                    f"Indexados {len(chunks)} fragmentos para o documento '{doc_title}' no pilar '{pillar}'."
                )

            return len(chunks)


def get_indexer(
    splitter: Optional[BaseDocumentSplitter] = None,
    vector_store: Optional[Any] = None,
) -> KnowledgeIndexer:
    """Retorna uma instância configurada do indexador de conhecimento."""
    return KnowledgeIndexer(splitter=splitter, vector_store=vector_store)
