from typing import List, Optional
import pytest
from unittest.mock import Mock, patch
from langchain_core.documents import Document
from langchain_core.embeddings import FakeEmbeddings
from langchain_core.retrievers import BaseRetriever
from langchain_core.callbacks import CallbackManagerForRetrieverRun

from ia.retrieval.vectorstore import normalize_connection_string, get_vector_store, DEFAULT_COLLECTION_NAME
from ia.retrieval.retriever import get_vector_retriever, get_hybrid_retriever, EnsembleHybridRetriever


class DummyRetriever(BaseRetriever):
    docs: List[Document] = []

    def _get_relevant_documents(
        self,
        query: str,
        *,
        run_manager: Optional[CallbackManagerForRetrieverRun] = None,
    ) -> List[Document]:
        return self.docs


def test_normalize_connection_string():
    assert normalize_connection_string('postgres://u:p@challocalhost:5432/db') == 'postgresql+psycopg://u:p@challocalhost:5432/db'
    assert normalize_connection_string('postgresql://u:p@challocalhost:5432/db') == 'postgresql+psycopg://u:p@challocalhost:5432/db'
    assert normalize_connection_string('postgresql+psycopg://u:p@challocalhost:5432/db') == 'postgresql+psycopg://u:p@challocalhost:5432/db'
    with pytest.raises(ValueError):
        normalize_connection_string('')


@patch('ia.retrieval.vectorstore.PGVector')
def test_get_vector_store_mock(mock_pgvector):
    fake_emb = FakeEmbeddings(size=1536)
    store = get_vector_store(
        embedding_service=fake_emb,
        connection_string='postgresql+psycopg://u:p@host/db',
        collection_name='test_coll'
    )
    mock_pgvector.assert_called_once()


@patch('ia.retrieval.retriever.get_vector_store')
def test_get_vector_retriever(mock_get_store):
    mock_store_instance = Mock()
    dummy_retriever = DummyRetriever(docs=[Document(page_content='Test')])
    mock_store_instance.as_retriever.return_value = dummy_retriever
    mock_get_store.return_value = mock_store_instance

    retriever = get_vector_retriever(
        k=5,
        pillar='IMMIGRATION',
        collection_name='test_coll'
    )

    mock_store_instance.as_retriever.assert_called_once_with(
        search_type='similarity',
        search_kwargs={'k': 5, 'filter': {'pillar': 'IMMIGRATION'}}
    )
    assert retriever == dummy_retriever


@patch('ia.retrieval.retriever.get_vector_retriever')
def test_get_hybrid_retriever(mock_vector_retriever):
    dummy_v = DummyRetriever(docs=[Document(page_content='Lei 13445', metadata={'pillar': 'IMMIGRATION'})])
    mock_vector_retriever.return_value = dummy_v
    docs = [
        Document(page_content='Lei de Migração 13445', metadata={'pillar': 'IMMIGRATION'}),
        Document(page_content='Plataforma Carolina Bori', metadata={'pillar': 'EDUCATION'})
    ]

    hybrid_retriever = get_hybrid_retriever(
        documents=docs,
        k=2,
        pillar='IMMIGRATION',
        weights=[0.7, 0.3]
    )

    assert isinstance(hybrid_retriever, EnsembleHybridRetriever)
    assert hybrid_retriever.weights == [0.7, 0.3]


def test_ensemble_hybrid_retriever_rrf_execution():
    doc1 = Document(page_content='Doc 1')
    doc2 = Document(page_content='Doc 2')
    doc3 = Document(page_content='Doc 3')

    ret1 = DummyRetriever(docs=[doc1, doc2])
    ret2 = DummyRetriever(docs=[doc2, doc3])

    ensemble = EnsembleHybridRetriever(
        retrievers=[ret1, ret2],
        weights=[0.6, 0.4],
        k=2
    )
    results = ensemble.invoke('query')
    assert len(results) == 2
    assert results[0].page_content == 'Doc 2'
