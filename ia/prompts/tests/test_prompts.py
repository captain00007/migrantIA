import pytest
from ia.prompts.multilingual import (
    get_golden_rule_fallback,
    SUPPORTED_UI_LANGUAGES,
    GOLDEN_RULE_MESSAGES,
    detect_language_heuristic,
    DEFAULT_LANGUAGE,
)
from ia.prompts.rag import get_rag_prompt_template


def test_supported_ui_languages():
    assert "ht" in SUPPORTED_UI_LANGUAGES
    assert "fr" in SUPPORTED_UI_LANGUAGES
    assert "es" in SUPPORTED_UI_LANGUAGES
    assert "en" in SUPPORTED_UI_LANGUAGES
    assert "pt" in SUPPORTED_UI_LANGUAGES


def test_golden_rule_fallback_messages():
    for lang in SUPPORTED_UI_LANGUAGES:
        msg = get_golden_rule_fallback(lang)
        assert len(msg) > 20
        assert msg == GOLDEN_RULE_MESSAGES[lang]


def test_detect_language_heuristic():
    assert detect_language_heuristic("Kijan mwen ka fè CPF nan Brezil?") == "ht"
    assert detect_language_heuristic("Bonjour, comment obtenir le titre de séjour?") == "fr"
    assert detect_language_heuristic("Necesito solicitar mi permiso de residencia") == "es"
    assert detect_language_heuristic("How can I get my passport registered?") == "en"
    assert detect_language_heuristic("Como faço para tirar a carteira de trabalho?") == "pt"
    assert detect_language_heuristic("") == DEFAULT_LANGUAGE


def test_rag_prompt_template():
    prompt = get_rag_prompt_template()
    formatted = prompt.format_messages(
        context="Informações sobre CPF",
        question="Como emitir CPF?",
        chat_history=[]
    )
    assert len(formatted) == 2
    assert "Informações sobre CPF" in formatted[1].content
    assert "Como emitir CPF?" in formatted[1].content
