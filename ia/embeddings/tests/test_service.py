"""
Testes unitários para o serviço de Embeddings do MigrantIA.
Validando a arquitetura 100% orientada ao .env / django.conf.settings.
"""

import sys
from unittest.mock import MagicMock, patch

import pytest
from django.conf import settings

from ia.embeddings.service import (
    EmbeddingService,
    get_embedding_service,
    normalize_provider_name,
)


def test_normalize_provider_name_aliases():
    assert normalize_provider_name("llama") == "ollama"
    assert normalize_provider_name("llama3") == "ollama"
    assert normalize_provider_name("local") == "ollama"
    assert normalize_provider_name("gpt") == "openai"
    assert normalize_provider_name("gemini") == "google"
    assert normalize_provider_name("google-genai") == "google"
    assert normalize_provider_name(None) is None


def test_ai_embedding_provider_switch_from_settings(monkeypatch):
    monkeypatch.setattr(settings, "OLLAMA_BASE_URL", "http://localhost:11434")
    monkeypatch.setattr(settings, "OLLAMA_EMBEDDING_MODEL", "nomic-embed-text")
    monkeypatch.setattr(settings, "AI_EMBEDDING_MODEL", None)

    # Se AI_EMBEDDING_PROVIDER=llama, normaliza para ollama
    monkeypatch.setattr(settings, "AI_EMBEDDING_PROVIDER", "llama")
    with patch("langchain_community.embeddings.OllamaEmbeddings"):
        service = EmbeddingService()
        assert service.provider_name == "ollama"
        assert service.model_name == "nomic-embed-text"

    # Se AI_EMBEDDING_PROVIDER=gemini, normaliza para google
    monkeypatch.setattr(settings, "AI_EMBEDDING_PROVIDER", "gemini")
    monkeypatch.setattr(settings, "GOOGLE_API_KEY", "ai-test-key")
    monkeypatch.setattr(settings, "GOOGLE_EMBEDDING_MODEL", "models/text-embedding-004")
    mock_google_mod = MagicMock()
    with patch.dict(sys.modules, {"langchain_google_genai": mock_google_mod}):
        service = EmbeddingService()
        assert service.provider_name == "google"
        assert service.model_name == "models/text-embedding-004"

    # Se AI_EMBEDDING_PROVIDER=gpt, normaliza para openai
    monkeypatch.setattr(settings, "AI_EMBEDDING_PROVIDER", "gpt")
    monkeypatch.setattr(settings, "OPENAI_API_KEY", "sk-test-key")
    monkeypatch.setattr(settings, "OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
    with patch("langchain_openai.OpenAIEmbeddings"):
        service = EmbeddingService()
        assert service.provider_name == "openai"
        assert service.model_name == "text-embedding-3-small"


def test_provider_specific_model_resolution(monkeypatch):
    monkeypatch.setattr(settings, "AI_EMBEDDING_PROVIDER", "ollama")
    monkeypatch.setattr(settings, "OLLAMA_BASE_URL", "http://localhost:11434")
    monkeypatch.setattr(settings, "OLLAMA_EMBEDDING_MODEL", "bge-large-pt")
    monkeypatch.setattr(settings, "AI_EMBEDDING_MODEL", None)

    with patch("langchain_community.embeddings.OllamaEmbeddings"):
        service = EmbeddingService()
        assert service.model_name == "bge-large-pt"

    # Se houver override direto via AI_EMBEDDING_MODEL no settings, tem prioridade
    monkeypatch.setattr(settings, "AI_EMBEDDING_MODEL", "custom-override-model")
    with patch("langchain_community.embeddings.OllamaEmbeddings"):
        service = EmbeddingService()
        assert service.model_name == "custom-override-model"


def test_no_provider_configured_raises_error(monkeypatch):
    monkeypatch.setattr(settings, "AI_EMBEDDING_PROVIDER", None)

    with pytest.raises(ValueError, match="Provedor de embedding não configurado"):
        EmbeddingService()


def test_no_model_configured_raises_error(monkeypatch):
    monkeypatch.setattr(settings, "AI_EMBEDDING_PROVIDER", "openai")
    monkeypatch.setattr(settings, "OPENAI_API_KEY", "sk-key")
    monkeypatch.setattr(settings, "AI_EMBEDDING_MODEL", None)
    monkeypatch.setattr(settings, "OPENAI_EMBEDDING_MODEL", None)

    with pytest.raises(ValueError, match="Nenhum modelo de embedding configurado"):
        EmbeddingService()


def test_unsupported_provider_raises_error(monkeypatch):
    monkeypatch.setattr(settings, "AI_EMBEDDING_PROVIDER", "provedor_inexistente_xyz")
    monkeypatch.setattr(settings, "AI_EMBEDDING_MODEL", "some-model")

    with pytest.raises(ValueError, match="não suportado"):
        EmbeddingService()


def test_openai_provider_factory(monkeypatch):
    monkeypatch.setattr(settings, "AI_EMBEDDING_PROVIDER", "openai")
    monkeypatch.setattr(settings, "OPENAI_API_KEY", "sk-fake-test-key")
    monkeypatch.setattr(settings, "OPENAI_EMBEDDING_MODEL", "text-embedding-3-large")
    monkeypatch.setattr(settings, "AI_EMBEDDING_MODEL", None)

    with patch("langchain_openai.OpenAIEmbeddings") as mock_openai_cls:
        mock_instance = MagicMock()
        mock_openai_cls.return_value = mock_instance

        service = get_embedding_service()
        assert service.provider == mock_instance
        mock_openai_cls.assert_called_once_with(
            model="text-embedding-3-large",
            openai_api_key="sk-fake-test-key"
        )


def test_ollama_provider_factory(monkeypatch):
    monkeypatch.setattr(settings, "AI_EMBEDDING_PROVIDER", "llama")
    monkeypatch.setattr(settings, "OLLAMA_BASE_URL", "http://192.168.1.100:11434")
    monkeypatch.setattr(settings, "OLLAMA_EMBEDDING_MODEL", "bge-m3")
    monkeypatch.setattr(settings, "AI_EMBEDDING_MODEL", None)

    with patch("langchain_community.embeddings.OllamaEmbeddings") as mock_cls:
        mock_instance = MagicMock()
        mock_cls.return_value = mock_instance

        service = get_embedding_service()
        assert service.provider == mock_instance
        mock_cls.assert_called_once_with(
            model="bge-m3",
            base_url="http://192.168.1.100:11434"
        )


def test_google_provider_factory(monkeypatch):
    monkeypatch.setattr(settings, "AI_EMBEDDING_PROVIDER", "gemini")
    monkeypatch.setattr(settings, "GOOGLE_API_KEY", "fake-gemini-key")
    monkeypatch.setattr(settings, "GOOGLE_EMBEDDING_MODEL", "models/text-embedding-004")
    monkeypatch.setattr(settings, "AI_EMBEDDING_MODEL", None)

    mock_google_cls = MagicMock()
    mock_instance = MagicMock()
    mock_google_cls.return_value = mock_instance

    mock_module = MagicMock()
    mock_module.GoogleGenerativeAIEmbeddings = mock_google_cls

    with patch.dict(sys.modules, {"langchain_google_genai": mock_module}):
        service = get_embedding_service()
        assert service.provider == mock_instance
        mock_google_cls.assert_called_once_with(
            model="models/text-embedding-004",
            google_api_key="fake-gemini-key"
        )