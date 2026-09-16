"""
Orquestrador de indexação no PostgreSQL com PGVector para os 4 Pilares do MigrantIA.
Executa a limpeza (TextCleaner), o particionamento (DocumentSplitter),
o salvamento unificado do arquivo original e do texto limpo em disco,
e a gravação dos embeddings no PostgreSQL/PGVector.
"""
import io
import hashlib
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
from django.db import connection, transaction
from langchain_core.documents import Document

from apps.sources.models import PillarChoices, OfficialSource
from apps.knowledge.models import KnowledgeDocument, DocumentTypeChoices
from ia.ingestion.cleaners import BaseCleaner, TextCleaner
from ia.ingestion.splitter import BaseDocumentSplitter, DocumentSplitter
from ia.ingestion.storage import save_document_bundle
from ia.retrieval.vectorstore import get_vector_store

logger = logging.getLogger(__name__)


def compute_content_hash(documents: List[Document]) -> str:
    """Gera hash SHA-256 a partir do conteúdo textual concatenado dos documentos."""
    combined_text = "\n\n".join(doc.page_content for doc in documents if doc.page_content)
    return hashlib.sha256(combined_text.encode("utf-8")).hexdigest()


class KnowledgeIndexer:
    """
    Orquestrador de indexação para os 4 Pilares de Conhecimento do MigrantIA.
    """

    def __init__(
        self,
        splitter: Optional[BaseDocumentSplitter] = None,
        cleaner: Optional[BaseCleaner] = None,
        vector_store: Optional[Any] = None,
    ):
        self.splitter = splitter or DocumentSplitter()
        self.cleaner = cleaner or TextCleaner()
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

    def _delete_document_vectors(self, knowledge_document_id: int) -> None:
        """
        Remove do PGVector todos os fragmentos associados a um determinado KnowledgeDocument.
        """
        try:
            with connection.cursor() as cursor:
                if connection.vendor == "postgresql":
                    cursor.execute(
                        "DELETE FROM langchain_pg_embedding WHERE cmetadata->>'knowledge_document_id' = %s",
                        [str(knowledge_document_id)],
                    )
                elif connection.vendor == "sqlite":
                    cursor.execute(
                        "SELECT name FROM sqlite_master WHERE type='table' AND name='langchain_pg_embedding';"
                    )
                    if cursor.fetchone():
                        cursor.execute(
                            "DELETE FROM langchain_pg_embedding WHERE json_extract(cmetadata, '$.knowledge_document_id') = ?",
                            [str(knowledge_document_id)],
                        )
            logger.info(f"Fragmentos antigos removidos para o documento ID {knowledge_document_id}.")
        except Exception as e:
            logger.warning(
                f"Erro ao tentar remover fragmentos do PGVector para o documento {knowledge_document_id}: {e}"
            )

    def index_documents(
        self,
        documents: List[Document],
        pillar: str = PillarChoices.IMMIGRATION,
        source: Optional[OfficialSource] = None,
        title: Optional[str] = None,
        url: Optional[str] = None,
        document_type: str = DocumentTypeChoices.GUIDE,
        content_hash: str = "",
        source_file: Optional[Union[str, Path, bytes, io.BytesIO]] = None,
        original_filename: Optional[str] = None,
    ) -> int:
        """
        Indexa documentos com controle de idempotência por hash de conteúdo e armazenamento de artefatos:
        1. Limpa e normaliza os documentos carregados (TextCleaner).
        2. Calcula o hash SHA-256 do conteúdo limpo (se não fornecido).
        3. Salva o arquivo original e o texto limpo no diretório media/documents/<hash>/.
        4. Verifica se o documento já existe no Django:
           - Se existir e o hash for idêntico: atualiza metadados e PULA vetorização (retorna 0).
           - Se existir e o hash mudou: limpa vetores antigos do PGVector e atualiza com novos vetores.
           - Se for novo: cria o registro e efetua a vetorização.
        """
        if not documents:
            return 0

        # Etapa de Limpeza e Normalização (TextCleaner)
        cleaned_docs = self.cleaner.clean_documents(documents)
        if not cleaned_docs:
            return 0

        doc_title = title or (cleaned_docs[0].metadata.get("title") if cleaned_docs else "Documento Oficial")
        doc_url = (url or (cleaned_docs[0].metadata.get("url") if cleaned_docs else None) or "")
        effective_hash = content_hash or compute_content_hash(cleaned_docs)

        # Salva o bundle (original + cleaned.md) no disco
        save_document_bundle(
            content_hash=effective_hash,
            cleaned_docs=cleaned_docs,
            source_file=source_file,
            original_filename=original_filename,
        )

        with transaction.atomic():
            existing_doc = KnowledgeDocument.objects.filter(
                title=doc_title,
                pillar=pillar
            ).first()

            if existing_doc:
                # Caso 1: Conteúdo idêntico (Idempotência / Sem alterações)
                if existing_doc.content_hash == effective_hash and effective_hash != "":
                    logger.info(
                        f"Documento '{doc_title}' no pilar '{pillar}' não foi modificado "
                        f"(hash {effective_hash[:8]}...). Pulando geração de embeddings."
                    )
                    existing_doc.source = source
                    existing_doc.document_type = document_type
                    existing_doc.url = doc_url
                    existing_doc.save(update_fields=["source", "document_type", "url", "updated_at"])
                    return 0

                # Caso 2: Conteúdo modificado
                logger.info(
                    f"Documento '{doc_title}' foi alterado. Atualizando metadados e re-indexando vetores."
                )
                self._delete_document_vectors(existing_doc.id)

                existing_doc.source = source
                existing_doc.document_type = document_type
                existing_doc.url = doc_url
                existing_doc.content_hash = effective_hash
                existing_doc.save(update_fields=["source", "document_type", "url", "content_hash", "updated_at"])
                knowledge_doc = existing_doc
            else:
                # Caso 3: Novo documento
                knowledge_doc = KnowledgeDocument.objects.create(
                    title=doc_title,
                    pillar=pillar,
                    source=source,
                    document_type=document_type,
                    url=doc_url,
                    content_hash=effective_hash,
                )

            # Dividir documentos e enviar ao PGVector
            chunks = self.splitter.split_documents(cleaned_docs)
            for chunk in chunks:
                chunk.metadata.update({
                    "knowledge_document_id": knowledge_doc.id,
                    "pillar": pillar,
                    "title": doc_title,
                    "url": doc_url,
                    "document_type": document_type,
                })

            if chunks:
                self.vector_store.add_documents(chunks)
                logger.info(
                    f"Indexados {len(chunks)} fragmentos para o documento '{doc_title}' no pilar '{pillar}'."
                )

            return len(chunks)


def get_indexer(
    splitter: Optional[BaseDocumentSplitter] = None,
    cleaner: Optional[BaseCleaner] = None,
    vector_store: Optional[Any] = None,
) -> KnowledgeIndexer:
    """Retorna uma instância configurada do indexador de conhecimento."""
    return KnowledgeIndexer(splitter=splitter, cleaner=cleaner, vector_store=vector_store)
