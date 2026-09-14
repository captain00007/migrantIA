from unittest.mock import Mock, patch
import pytest
from langchain_core.documents import Document
from apps.sources.models import PillarChoices
from apps.knowledge.models import KnowledgeDocument
from ia.ingestion.indexer import KnowledgeIndexer, get_indexer


@pytest.mark.django_db
def test_knowledge_indexer_index_documents():
    mock_vectorstore = Mock()
    mock_splitter = Mock()
    mock_splitter.split_documents.return_value = [
        Document(page_content="Fragmento 1", metadata={}),
        Document(page_content="Fragmento 2", metadata={}),
    ]

    indexer = KnowledgeIndexer(splitter=mock_splitter)
    indexer.vector_store = mock_vectorstore

    docs = [Document(page_content="Texto completo da Lei de Migração", metadata={"title": "Lei 13.445", "url": "https://www.gov.br/lei"})]
    indexed_count = indexer.index_documents(
        documents=docs,
        pillar=PillarChoices.IMMIGRATION,
        title="Lei de Migração 13.445",
        url="https://www.gov.br/lei",
    )

    assert indexed_count == 2
    assert KnowledgeDocument.objects.filter(title="Lei de Migração 13.445").exists()
    doc_record = KnowledgeDocument.objects.get(title="Lei de Migração 13.445")
    assert doc_record.pillar == PillarChoices.IMMIGRATION
    assert mock_vectorstore.add_documents.called
