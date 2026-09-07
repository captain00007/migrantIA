import os
import hashlib
import numpy as np
from typing import List


class MockEmbeddingModel:
    """
    Gerador determinístico de embeddings vetoriais (1536 dimensões) para
    ambientes de desenvolvimento e teste quando OPENAI_API_KEY não estiver configurada.
    """
    def __init__(self, dimensions: int = 1536):
        self.dimensions = dimensions

    def embed_query(self, text: str) -> List[float]:
        # Gera vetor determinístico a partir do hash sha256 do texto
        seed = int(hashlib.sha256(text.encode('utf-8')).hexdigest()[:8], 16)
        rng = np.random.default_rng(seed)
        vec = rng.standard_normal(self.dimensions)
        norm = np.linalg.norm(vec)
        if norm > 0:
            vec = vec / norm
        return vec.tolist()

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return [self.embed_query(t) for t in texts]


def get_embedding_service():
    """
    Retorna o serviço de embeddings configurado.
    Se OPENAI_API_KEY estiver presente, utiliza LangChain OpenAIEmbeddings.
    Caso contrário, utiliza MockEmbeddingModel seguro para desenvolvimento.
    """
    api_key = os.environ.get('OPENAI_API_KEY')
    if api_key and api_key.strip():
        try:
            from langchain_openai import OpenAIEmbeddings
            return OpenAIEmbeddings(
                model="text-embedding-3-small",
                openai_api_key=api_key
            )
        except Exception as e:
            print(f"Aviso: Não foi possível instanciar OpenAIEmbeddings ({e}). Usando fallback mock.")
            return MockEmbeddingModel()
    else:
        return MockEmbeddingModel()
