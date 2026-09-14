"""
Módulo de Vector Store do MigrantIA.
Encapsula o gerenciamento do PGVector no PostgreSQL para indexação e busca semântica.
"""
import logging
from typing import Optional, Any, Dict
from django.conf import settings
from langchain_core.embeddings import Embeddings
from langchain_community.vectorstores.pgvector import PGVector
from ia.embeddings.service import get_embedding_service

logger = logging.getLogger(__name__)

DEFAULT_COLLECTION_NAME = "migrantia_knowledge"


def normalize_connection_string(url: Optional[str]) -> str:
    """
    Normaliza URLs de conexão do Django para o formato compatível com SQLLoader/psycopg3.
    """
    if not url:
        raise ValueError("DATABASE_URL não configurada no settings.")

    url = url.strip()
    if url.startswith("postgres://"):
        return "postgresql+psycopg://" + url[len("postgres://"):]
    elif url.startswith("postgresql://") and not url.startswith("postgresql+"):
        return "postgresql+psycopg://" + url[len("postgresql://"):]
    return url


def get_vector_store(
    collection_name: str = DEFAULT_COLLECTION_NAME,
    embedding_service: Optional[Any] = None,
    connection_string: Optional[str] = None,
    pre_delete_collection: bool = False,
    **kwargs: Any,
) -> PGVector:
    """
    Inicializa e retorna uma instância do PGVector VectorStore configurada
    para o banco PostgreSQL do MigrantIA.
    """
    if embedding_service is None:
        emb_svc = get_embedding_service()
        embedding_fn: Embeddings = emb_svc.provider
    elif hasattr(embedding_service, "provider"):
        embedding_fn = embedding_service.provider
    else:
        embedding_fn = embedding_service

    raw_db_url = getattr(settings, "DATABASE_URL", None)
    conn_str = connection_string or normalize_connection_string(raw_db_url)

    return PGVector(
        connection_string=conn_str,
        embedding_function=embedding_fn,
        collection_name=collection_name,
        use_jsonb=True,
        pre_delete_collection=pre_delete_collection,
        **kwargs,
    )
