import logging
from typing import Optional, Dict, Any, List, Callable

from django.conf import settings
from langchain_core.embeddings import Embeddings
from ia.embeddings.base import BaseEmbeddingService

logger = logging.getLogger(__name__)


def normalize_provider_name(name: Optional[str]) -> Optional[str]:
    """
    Normaliza aliases de provedores para os nomes canônicos suportados.
    """
    if not name:
        return None
    cleaned = str(name).lower().strip().replace("_", "-")
    alias_map = {
        "llama": "ollama",
        "llama3": "ollama",
        "ollama": "ollama",
        "local": "ollama",
        "gpt": "openai",
        "openai": "openai",
        "gemini": "google",
        "google": "google",
        "google-genai": "google",
    }
    return alias_map.get(cleaned, cleaned)


class EmbeddingService(BaseEmbeddingService):
    """
    Serviço de Embeddings do MigrantIA.
    100% configurado a partir do django.conf.settings / .env (OpenAI, Google Gemini, Ollama).
    """

    def __init__(self, **kwargs: Any) -> None:
        # 1. Resolve o Provedor Ativo estritamente do settings
        self.provider_name = self._resolve_provider()

        # 2. Resolve o Modelo estritamente do settings
        self.model_name = self._resolve_model(self.provider_name)

        # 3. Resolve as Dimensões dos Vetores
        self.dimensions = self._resolve_dimensions()

        self.kwargs = kwargs
        self._provider = self._build_provider_instance()

    # -------------------------------------------------------------------------
    # Métodos de Resolução (via django.conf.settings)
    # -------------------------------------------------------------------------

    def _resolve_provider(self) -> str:
        raw_provider = getattr(settings, "AI_EMBEDDING_PROVIDER", None)
        canonical = normalize_provider_name(raw_provider)
        if not canonical:
            raise ValueError(
                "Provedor de embedding não configurado. "
                "Defina 'AI_EMBEDDING_PROVIDER' no seu arquivo .env / settings."
            )
        return canonical

    def _resolve_model(self, provider: str) -> str:
        if generic_model := getattr(settings, "AI_EMBEDDING_MODEL", None):
            return generic_model

        provider_key = f"{provider.upper()}_EMBEDDING_MODEL"
        if provider_model := getattr(settings, provider_key, None):
            return provider_model

        raise ValueError(
            f"Nenhum modelo de embedding configurado para o provedor '{provider}'. "
            f"Defina 'AI_EMBEDDING_MODEL' ou '{provider_key}' no seu arquivo .env / settings."
        )

    def _resolve_dimensions(self) -> Optional[int]:
        dim_val = getattr(settings, "AI_EMBEDDING_DIMENSIONS", None)
        if isinstance(dim_val, int):
            return dim_val
        if isinstance(dim_val, str) and dim_val.strip().isdigit():
            return int(dim_val.strip())
        return None

    @property
    def provider(self) -> Embeddings:
        """Retorna a instância concreta do provedor de embeddings."""
        return self._provider

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Gera vetores para uma lista de textos delegando para o provedor encapsulado."""
        return self._provider.embed_documents(texts)

    def embed_query(self, text: str) -> List[float]:
        """Gera o vetor para uma consulta delegando para o provedor encapsulado."""
        return self._provider.embed_query(text)

    # -------------------------------------------------------------------------
    # Construção do Provedor Fixo Suportado
    # -------------------------------------------------------------------------

    def _build_provider_instance(self) -> Embeddings:

        """Instancia o provedor configurado no .env."""
        factories: Dict[str, Callable[..., Embeddings]] = {
            "openai": self._create_openai,
            "google": self._create_google,
            "ollama": self._create_ollama,
        }

        factory = factories.get(self.provider_name)
        if not factory:
            supported = ", ".join(sorted(factories.keys()))
            raise ValueError(
                f"Provedor de embedding '{self.provider_name}' não suportado. "
                f"Provedores suportados: {supported}."
            )

        factory_kwargs: Dict[str, Any] = {
            "model": self.model_name,
            **self.kwargs
        }
        if self.dimensions:
            factory_kwargs["dimensions"] = self.dimensions

        return factory(**factory_kwargs)

    # -------------------------------------------------------------------------
    # Fábricas Especializadas dos Provedores Suportados
    # -------------------------------------------------------------------------

    @staticmethod
    def _create_openai(
        model: str,
        dimensions: Optional[int] = None,
        **kwargs: Any
    ) -> Embeddings:
        from langchain_openai import OpenAIEmbeddings

        key = getattr(settings, "OPENAI_API_KEY", None)
        if not key:
            raise ValueError("OPENAI_API_KEY não configurada no settings para 'openai'.")

        params: Dict[str, Any] = {"model": model, "openai_api_key": key, **kwargs}
        if dimensions:
            params["dimensions"] = dimensions
        return OpenAIEmbeddings(**params)

    @staticmethod
    def _create_google(
        model: str,
        **kwargs: Any
    ) -> Embeddings:
        from langchain_google_genai import GoogleGenerativeAIEmbeddings

        key = getattr(settings, "GEMINI_API_KEY", None)
        if not key:
            raise ValueError("GEMINI_API_KEY não configurada no settings para 'google'.")

        return GoogleGenerativeAIEmbeddings(model=model, api_key=key, **kwargs)

    @staticmethod
    def _create_ollama(
        model: str,
        **kwargs: Any
    ) -> Embeddings:
        from langchain_community.embeddings import OllamaEmbeddings

        url = (
            getattr(settings, "OLLAMA_BASE_URL", None)
            or getattr(settings, "OLLAMA_HOST", None)
            or "http://localhost:11434"
        )
        return OllamaEmbeddings(model=model, base_url=url, **kwargs)


def get_embedding_service(**kwargs: Any) -> EmbeddingService:
    """
    Obtém a instância de EmbeddingService configurada a partir do .env / settings.
    """
    return EmbeddingService(**kwargs)
