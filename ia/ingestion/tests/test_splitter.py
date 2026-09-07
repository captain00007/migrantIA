import pytest
from langchain_core.documents import Document
from ia.ingestion.splitter import (
    BaseDocumentSplitter,
    LegalDocumentSplitter,
    DocumentSplitter,
    get_legal_text_splitter,
    split_document_text
)


def test_legal_document_splitter_split_text():
    sample_legal_text = """
# Lei de Migração - Lei nº 13.445/2017

Art. 1º Esta Lei dispõe sobre os direitos e os deveres do migrante e do visitante.
§ 1º A política migratória brasileira é regida pelo princípio da acolhida humanitária.
§ 2º É garantida a igualdade de tratamento e de oportunidade ao migrante.

## Do Visto Temporário

Art. 14. O visto temporário poderá ser concedido ao imigrante que venha ao Brasil:
I - para pesquisa, ensino ou extensão acadêmica;
II - para tratamento de saúde;
III - para acolhida humanitária.
"""
    splitter = LegalDocumentSplitter(chunk_size=200, chunk_overlap=30)
    chunks = splitter.split_text(sample_legal_text, metadata={"document_id": "lei-13445"})

    assert len(chunks) > 0
    for chunk in chunks:
        assert 'content' in chunk
        assert 'chunk_index' in chunk
        assert 'metadata' in chunk
        assert chunk['metadata']['document_id'] == "lei-13445"
        assert chunk['metadata']['total_chunks'] == len(chunks)


def test_legal_document_splitter_split_documents():
    docs = [
        Document(
            page_content="Art. 1º Acolhida humanitária aos cidadãos haitianos no Brasil.\n\nArt. 2º Regularização documental.",
            metadata={"source": "portaria_37_2023.pdf", "author": "MJSP"}
        )
    ]
    splitter = DocumentSplitter(chunk_size=80, chunk_overlap=10)
    split_docs = splitter.split_documents(docs)

    assert len(split_docs) >= 1
    for idx, doc in enumerate(split_docs):
        assert doc.metadata['source'] == "portaria_37_2023.pdf"
        assert doc.metadata['author'] == "MJSP"
        assert doc.metadata['chunk_index'] == idx
        assert doc.metadata['total_chunks'] == len(split_docs)


def test_splitter_empty_input():
    splitter = LegalDocumentSplitter()
    assert splitter.split_text("") == []
    assert splitter.split_text("   ") == []
    assert splitter.split_documents([]) == []


def test_legacy_functions_compatibility():
    raw_text = "Texto de teste para validação de compatibilidade com indexador."
    result = split_document_text(raw_text, metadata={"title": "Teste"})
    assert len(result) == 1
    assert result[0]['metadata']['title'] == "Teste"

    raw_splitter = get_legal_text_splitter()
    assert raw_splitter._chunk_size == 1000
