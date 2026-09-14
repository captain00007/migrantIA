from unittest.mock import Mock, patch
import pytest
from ia.llm.factory import normalize_llm_provider_name, LLMFactory, get_llm


def test_normalize_llm_provider_name():
    assert normalize_llm_provider_name("gpt") == "openai"
    assert normalize_llm_provider_name("OPENAI") == "openai"
    assert normalize_llm_provider_name("llama3") == "ollama"
    assert normalize_llm_provider_name("google-genai") == "google"
    assert normalize_llm_provider_name(None) is None


def test_resolve_provider_valid():
    assert LLMFactory.resolve_provider("openai") == "openai"
    assert LLMFactory.resolve_provider("ollama") == "ollama"
    assert LLMFactory.resolve_provider("google") == "google"
    with pytest.raises(ValueError):
        LLMFactory.resolve_provider("invalid_provider_xyz")


@patch("ia.llm.factory.create_openai_chat")
def test_create_llm_openai(mock_create):
    mock_llm = Mock()
    mock_create.return_value = mock_llm

    llm = get_llm(provider="openai", model="gpt-4o-mini", temperature=0.0)
    mock_create.assert_called_once_with(model="gpt-4o-mini", temperature=0.0)
    assert llm == mock_llm


@patch("ia.llm.factory.create_google_chat")
def test_create_llm_google(mock_create):
    mock_llm = Mock()
    mock_create.return_value = mock_llm

    llm = get_llm(provider="google", model="gemini-1.5-flash", temperature=0.2)
    mock_create.assert_called_once_with(model="gemini-1.5-flash", temperature=0.2)
    assert llm == mock_llm


@patch("ia.llm.factory.create_ollama_chat")
def test_create_llm_ollama(mock_create):
    mock_llm = Mock()
    mock_create.return_value = mock_llm

    llm = get_llm(provider="ollama", model="llama3.1:8b", temperature=0.0)
    mock_create.assert_called_once_with(model="llama3.1:8b", temperature=0.0)
    assert llm == mock_llm
