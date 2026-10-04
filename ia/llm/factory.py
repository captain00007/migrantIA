"""
Fábrica de Modelos de Linguagem (LLM) do MigrantIA.
Resolve o provedor (OpenAI, Gemini, Ollama) e instancia a classe de chat correspondente.
"""
from typing import Any, Optional
from django.conf import settings
from langchain_core.language_models.chat_models import BaseChatModel
from ia.llm.providers import (
    create_openai_chat,
    create_google_chat,
    create_ollama_chat,
)

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


def normalize_llm_provider_name(provider_name: Optional[str]) -> Optional[str]:
    """Normaliza o nome do provedor para um identificador canônico."""
    if not provider_name:
        return None
    normalized = provider_name.strip().lower()
    return PROVIDER_ALIASES.get(normalized, normalized)


class LLMFactory:
    """Fábrica para obtenção de instâncias de LLM configuradas."""

    @classmethod
    def resolve_provider(cls, provider: Optional[str] = None) -> str:
        """Resolve o nome do provedor considerando defaults e variáveis de ambiente."""
        raw = provider or getattr(settings, "AI_PROVIDER", "openai")
        normalized = normalize_llm_provider_name(raw)
        valid_providers = {"openai", "google", "ollama"}
        if normalized not in valid_providers:
            raise ValueError(
                f"Provedor de LLM inválido '{provider}'. "
                f"Provedores suportados: {sorted(list(valid_providers))}"
            )
        return normalized

    @classmethod
    def get_chat_model(
        cls,
        provider: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.3,
        **kwargs: Any,
    ) -> BaseChatModel:
        """
        Instancia e retorna o BaseChatModel correspondente ao provedor.
        """
        resolved_provider = cls.resolve_provider(provider)

        if resolved_provider == "openai":
            selected_model = model or getattr(settings, "AI_MODEL", "gpt-4o-mini")
            return create_openai_chat(model=selected_model, temperature=temperature, **kwargs)

        elif resolved_provider == "google":
            selected_model = model or getattr(settings, "AI_MODEL", "gemini-1.5-flash")
            return create_google_chat(model=selected_model, temperature=temperature, **kwargs)

        elif resolved_provider == "ollama":
            selected_model = model or getattr(settings, "AI_MODEL", "llama3.1:8b")
            return create_ollama_chat(model=selected_model, temperature=temperature, **kwargs)

        raise ValueError(f"Provedor não suportado: {resolved_provider}")


def get_llm(
    provider: Optional[str] = None,
    model: Optional[str] = None,
    temperature: float = 0.3,
    **kwargs: Any,
) -> BaseChatModel:
    """Função utilitária de conveniência para obter o LLM."""
    return LLMFactory.get_chat_model(
        provider=provider, model=model, temperature=temperature, **kwargs
    )
