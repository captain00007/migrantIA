import pytest
from langchain_core.documents import Document
from ia.ingestion.splitter import (
    BaseDocumentSplitter,
    DocumentSplitter,
)


def test_document_splitter_split_text():
    sample_legal_text = """
# Lei de Migracao - Lei n 13.445/2017

Art. 1 Esta Lei dispoe sobre os direitos e os deveres do migrante e do visitante.
§ 1 A politica migratoria brasileira e regida pelo principio da acolhida humanitaria.
§ 2 E garantida a igualdade de teratamento e de oportunidade ao migrante.

## Do Visto Temporario

Art. 14. O visto temporario podera ser concedido ao imigrante que venha ao Brasil:
I - para pesquisa, ensino ou extensao academica;
II - para tratamento de saude;
III - para acolhida humanitaria.
"""
    splitter = DocumentSplitter(chunk_size=200, chunk_overlap=30)
    chunks = splitter.split_text(sample_legal_text, metadata={"document_id": "lei-13445"})

    assert len(chunks) > 0
    for chunk in chunks:
        assert 'content' in chunk
        assert 'chunk_index' in chunk
        assert 'metadata' in chunk
        assert chunk['metadata']['document_id'] == "lei-13445"
        assert chunk['metadata']['total_chunks'] == len(chunks)


def test_document_splitter_split_documents():
    docs = [
        Document(
            page_content="Art. 1 Acolhida humanitaria aos cidadaos haitianos no Brasil.\n\nArt. 2 Regularizacao documental.",
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
    splitter = DocumentSplitter()
    assert splitter.split_text("") == []
    assert splitter.split_text("   ") == []
    assert splitter.split_documents([]) == []


def test_document_splitter_multiple_documents_index_isolation():
    docs = [Document(page_content="""Art 1 texto documento um.

Art 2 doc um.""", metadata={"source": "doc1.pdf"}), Document(page_content="""Art 1 texto documento dois.

Art 2 doc dois.""", metadata={"source": "doc2.pdf"})]
    splitter = DocumentSplitter(chunk_size=30, chunk_overlap=5)
    split_docs = splitter.split_documents(docs)
    doc1_chunks = [d for d in split_docs if d.metadata["source"] == "doc1.pdf"]
    doc2_chunks = [d for d in split_docs if d.metadata["source"] == "doc2.pdf"]
    assert len(doc1_chunks) >= 2
    assert len(doc2_chunks) >= 2
    for idx, d in enumerate(doc1_chunks):
        assert d.metadata["chunk_index"] == idx
        assert d.metadata["total_chunks"] == len(doc1_chunks)
    for idx, d in enumerate(doc2_chunks):
        assert d.metadata["chunk_index"] == idx
        assert d.metadata["total_chunks"] == len(doc2_chunks)
