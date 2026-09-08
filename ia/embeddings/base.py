"""
Módulo base para contratos e tipos compartilhados do serviço de embeddings do MigrantIA.
"""

from abc import ABC, abstractmethod
from typing import List

from langchain_core.embeddings import Embeddings


class BaseEmbeddingService(Embeddings, ABC):
    """
    Interface abstrata base para serviços e adaptadores de embeddings do MigrantIA.
    Padroniza a geração de vetores semânticos através do contrato do LangChain.
    """

    @abstractmethod
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """
        Gera vetores densos para uma lista de fragmentos/documentos textuais.

        Args:
            texts: Lista de strings a serem vetorizadas.

        Returns:
            Lista de vetores (listas de floats com dimensão fixa).
        """
        pass

    @abstractmethod
    def embed_query(self, text: str) -> List[float]:
        """
        Gera o vetor denso para uma consulta de busca textual do usuário.

        Args:
            text: Consulta textual a ser vetorizada.

        Returns:
            Vetor denso (lista de floats) para comparação por similaridade no pgvector.
        """
        pass
