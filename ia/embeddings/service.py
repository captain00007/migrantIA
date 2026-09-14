"""
Serviço central de geração de Embeddings para o MigrantIA.
Padrão 100% orientado às configurações do .env / django.conf.settings.
"""
from typing import Any, Dict, List, Optional
from django.conf import settings
from langchain_core.embeddings import Embeddings

# Mapeamento canônico de provedores
PROVIDER_ALIASES = {
    "openai": "openai",
    "gpt": "openai",
    "chatgpt": "openai",
    "google": "google",
    "gemini": "google",
    "google-genai": "google",
    "ollama": "ollama",
    "llama": "ollama",
    "llama3": "ollama",
    "local": "ollama",
}


def normalize_provider_name(provider_name: Optional[str]) -> Optional[str]:
    """Normaliza o nome do provedor para um identificador canônico."""
    if not provider_name:
        return None
    normalized = provider_name.strip().lower()
    return PROVIDER_ALIASES.get(normalized, normalized)


class EmbeddingService(Embeddings):
    """
    Fachada central de embeddings que encapsula os provedores suportados.
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
        # Prioridade 1: Modelo genérico AI_EMBEDDING_MODEL
        if general_model := getattr(settings, "AI_EMBEDDING_MODEL", None):
            return general_model

        # Prioridade 2: Variáveis específicas de provedor
        provider_key = f"{provider.upper()}_EMBEDDING_MODEL"
        if specific_model := getattr(settings, provider_key, None):
            return specific_model

        if provider == "google":
            if gemini_model := getattr(settings, "GEMINI_EMBEDDING_MODEL", None):
                return gemini_model

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

    # -------------------------------------------------------------------------
    # Implementação da Interface LangChain Embeddings
    # -------------------------------------------------------------------------

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Gera vetores para uma lista de textos delegando para o provedor encapsulado."""
        return self.provider.embed_documents(texts)

    def embed_query(self, text: str) -> List[float]:
        """Gera o vetor para uma consulta delegando para o provedor encapsulado."""
        return self.provider.embed_query(text)

    # -------------------------------------------------------------------------
    # Construção do Provedor Fixo Suportado
    # -------------------------------------------------------------------------

    def _build_provider_instance(self) -> Embeddings:
        factories = {
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
        if "dimensions" in self.kwargs:
            factory_kwargs["dimensions"] = self.kwargs["dimensions"]

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
