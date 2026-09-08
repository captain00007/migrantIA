"""
Módulo de Embeddings do MigrantIA.
"""

from ia.embeddings.base import BaseEmbeddingService
from ia.embeddings.service import (
    EmbeddingService,
    get_embedding_service,
)

__all__ = [
    "BaseEmbeddingService",
    "EmbeddingService",
    "get_embedding_service",
]