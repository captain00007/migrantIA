"""
Provedores de Modelos de Linguagem (LLM) do MigrantIA.
Implementa adaptadores para OpenAI, Google Gemini e Ollama utilizando LangChain.
"""
from typing import Any, Dict, Optional
from django.conf import settings
from langchain_core.language_models.chat_models import BaseChatModel


def create_openai_chat(
    model: str,
    temperature: float = 0.0,
    **kwargs: Any
) -> BaseChatModel:
    """Instancia o cliente ChatOpenAI."""
    from langchain_openai import ChatOpenAI

    api_key = getattr(settings, "OPENAI_API_KEY", None)
    if not api_key:
        raise ValueError("OPENAI_API_KEY não configurada no settings para o provedor 'openai'.")

    return ChatOpenAI(
        model=model,
        temperature=temperature,
        openai_api_key=api_key,
        **kwargs
    )


def create_google_chat(
    model: str,
    temperature: float = 0.0,
    **kwargs: Any
) -> BaseChatModel:
    """Instancia o cliente ChatGoogleGenerativeAI."""
    from langchain_google_genai import ChatGoogleGenerativeAI

    api_key = getattr(settings, "GEMINI_API_KEY", None)
    if not api_key:
        raise ValueError("GEMINI_API_KEY não configurada no settings para o provedor 'google'.")

    return ChatGoogleGenerativeAI(
        model=model,
        temperature=temperature,
        google_api_key=api_key,
        **kwargs
    )


def create_ollama_chat(
    model: str,
    temperature: float = 0.0,
    **kwargs: Any
) -> BaseChatModel:
    """Instancia o cliente ChatOllama."""
    from langchain_community.chat_models import ChatOllama

    base_url = (
        getattr(settings, "OLLAMA_BASE_URL", None)
        or getattr(settings, "OLLAMA_HOST", None)
        or "http://localhost:11434"
    )

    return ChatOllama(
        model=model,
        temperature=temperature,
        base_url=base_url,
        **kwargs,
    )
