from unittest.mock import Mock, patch
from pathlib import Path
import pytest
from langchain_core.documents import Document
from apps.sources.models import PillarChoices
from apps.knowledge.models import KnowledgeDocument, DocumentTypeChoices
from ia.ingestion.indexer import KnowledgeIndexer, get_indexer, compute_content_hash
from ia.ingestion.storage import get_documents_storage_dir


def test_compute_content_hash():
    docs = [
        Document(page_content="Primeiro parágrafo de teste."),
        Document(page_content="Segundo parágrafo de teste."),
    ]
    hash1 = compute_content_hash(docs)
    assert isinstance(hash1, str)
    assert len(hash1) == 64

    # Mesmo conteúdo gera mesmo hash
    docs_same = [
        Document(page_content="Primeiro parágrafo de teste."),
        Document(page_content="Segundo parágrafo de teste."),
    ]
    assert compute_content_hash(docs_same) == hash1

    # Conteúdo alterado gera hash diferente
    docs_diff = [Document(page_content="Conteúdo modificado")]
    assert compute_content_hash(docs_diff) != hash1


@pytest.mark.django_db
def test_knowledge_indexer_new_document_and_storage_bundle(tmp_path):
    mock_vectorstore = Mock()
    mock_splitter = Mock()
    mock_splitter.split_documents.return_value = [
        Document(page_content="Fragmento 1", metadata={}),
        Document(page_content="Fragmento 2", metadata={}),
    ]

    indexer = KnowledgeIndexer(splitter=mock_splitter, vector_store=mock_vectorstore)

    # Cria arquivo original de teste
    test_file = tmp_path / "lei_13445.txt"
    test_file.write_text("Texto completo original da Lei de Migração 13.445", encoding="utf-8")

    docs = [
        Document(
            page_content="Texto completo limpo da Lei de Migração 13.445",
            metadata={"title": "Lei 13.445", "url": "https://www.gov.br/lei"}
        )
    ]
    indexed_count = indexer.index_documents(
        documents=docs,
        pillar=PillarChoices.IMMIGRATION,
        title="Lei de Migração 13.445",
        url="https://www.gov.br/lei",
        source_file=test_file,
        original_filename="lei_13445.txt",
    )

    assert indexed_count == 2
    assert KnowledgeDocument.objects.filter(title="Lei de Migração 13.445").exists()
    doc_record = KnowledgeDocument.objects.get(title="Lei de Migração 13.445")
    assert doc_record.pillar == PillarChoices.IMMIGRATION
    assert doc_record.content_hash != ""
    assert mock_vectorstore.add_documents.called

    # Verifica se a pasta do hash e os arquivos foram criados
    storage_dir = doc_record.storage_dir
    assert storage_dir is not None
    assert storage_dir.exists()

    raw_saved = storage_dir / "lei_13445.txt"
    assert raw_saved.exists()
    assert "Texto completo original" in raw_saved.read_text(encoding="utf-8")

    cleaned_saved = storage_dir / "cleaned.md"
    assert cleaned_saved.exists()
    assert "Texto completo limpo" in cleaned_saved.read_text(encoding="utf-8")


@pytest.mark.django_db
def test_knowledge_indexer_skip_identical_content():
    mock_vectorstore = Mock()
    mock_splitter = Mock()
    mock_splitter.split_documents.return_value = [
        Document(page_content="Fragmento 1", metadata={})
    ]

    indexer = KnowledgeIndexer(splitter=mock_splitter, vector_store=mock_vectorstore)

    docs = [
        Document(
            page_content="Conteúdo estático sobre solicitação de refúgio no CONARE.",
            metadata={"title": "Guia CONARE"}
        )
    ]

    # 1ª Ingestão: Criação
    first_count = indexer.index_documents(
        documents=docs,
        pillar=PillarChoices.IMMIGRATION,
        title="Guia CONARE",
        url="https://www.gov.br/conare",
    )
    assert first_count == 1
    assert mock_vectorstore.add_documents.call_count == 1

    # 2ª Ingestão com mesmo conteúdo e nova URL: Deve pular vetorização e atualizar URL
    mock_vectorstore.reset_mock()
    mock_splitter.reset_mock()

    second_count = indexer.index_documents(
        documents=docs,
        pillar=PillarChoices.IMMIGRATION,
        title="Guia CONARE",
        url="https://www.gov.br/conare-atualizado",
    )

    assert second_count == 0
    assert not mock_vectorstore.add_documents.called
    assert not mock_splitter.split_documents.called

    # Confirma que a URL foi atualizada no metadado
    doc_record = KnowledgeDocument.objects.get(title="Guia CONARE")
    assert doc_record.url == "https://www.gov.br/conare-atualizado"


@pytest.mark.django_db
def test_knowledge_indexer_update_modified_content():
    mock_vectorstore = Mock()
    mock_splitter = Mock()
    mock_splitter.split_documents.return_value = [
        Document(page_content="Fragmento Versão 1", metadata={})
    ]

    indexer = KnowledgeIndexer(splitter=mock_splitter, vector_store=mock_vectorstore)

    docs_v1 = [
        Document(page_content="Versão original da portaria de acolhida humanitária.")
    ]

    # 1ª Ingestão
    indexer.index_documents(
        documents=docs_v1,
        pillar=PillarChoices.IMMIGRATION,
        title="Portaria Humanitária",
    )
    doc_v1 = KnowledgeDocument.objects.get(title="Portaria Humanitária")
    hash_v1 = doc_v1.content_hash
    assert hash_v1 != ""

    # 2ª Ingestão: Conteúdo alterado
    mock_vectorstore.reset_mock()
    mock_splitter.split_documents.return_value = [
        Document(page_content="Fragmento Versão 2 modificado", metadata={})
    ]

    docs_v2 = [
        Document(page_content="Versão revisada e ampliada da portaria com novas regras.")
    ]

    with patch.object(indexer, "_delete_document_vectors") as mock_delete:
        second_count = indexer.index_documents(
            documents=docs_v2,
            pillar=PillarChoices.IMMIGRATION,
            title="Portaria Humanitária",
        )

        assert second_count == 1
        assert mock_delete.called
        assert mock_delete.call_args[0][0] == doc_v1.id
        assert mock_vectorstore.add_documents.called

    doc_v2 = KnowledgeDocument.objects.get(title="Portaria Humanitária")
    assert doc_v2.content_hash != hash_v1
