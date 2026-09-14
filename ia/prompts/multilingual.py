"""
Catálogo de idiomas e mensagens padronizadas do MigrantIA.
Suporta os 5 idiomas principais de interface e atendimento:
- Crioulo Haitiano (ht)
- Francês (fr)
- Espanhol (es)
- Inglês (en)
- Português (pt - padrão)
"""
import re
from typing import Dict, List

DEFAULT_LANGUAGE: str = "pt"

SUPPORTED_UI_LANGUAGES: List[str] = ["ht", "fr", "es", "en", "pt"]

GOLDEN_RULE_MESSAGES: Dict[str, str] = {
    "pt": (
        "Não encontrei essa informação nos canais oficiais consultados. "
        "Recomendo procurar diretamente uma das instituições de apoio cadastradas "
        "ou o órgão competente (DPU, ACNUR, Cáritas, Missão Paz, CRAI)."
    ),
    "ht": (
        "Mwen pa jwenn enfòmasyon sa a nan sous ofisyèl yo konsilte. "
        "Mwen rekòmande pou w kontakte dirèkteman youn nan enstitisyon sipò yo "
        "oswa ògàn konpetan an (DPU, ACNUR, Caritas, Missão Paz, CRAI)."
    ),
    "fr": (
        "Je n'ai pas trouvé cette information dans les sources officielles consultées. "
        "Je vous recommande de vous adresser directement à l'une des organisations de soutien "
        "ou à l'autorité compétente (DPU, HCR, Caritas, Missão Paz, CRAI)."
    ),
    "es": (
        "No encontré esta información en las fuentes oficiales consultadas. "
        "Le recomiendo comunicarse directamente con una de las instituciones de apoyo registradas "
        "o el organismo competente (DPU, ACNUR, Cáritas, Missão Paz, CRAI)."
    ),
    "en": (
        "I did not find this information in the official sources consulted. "
        "I recommend contacting one of the registered support organizations "
        "or the competent official authority directly (DPU, UNHCR, Caritas, Missão Paz, CRAI)."
    ),
}


def get_golden_rule_fallback(lang_code: str = DEFAULT_LANGUAGE) -> str:
    """Retorna a mensagem da Regra de Ouro no idioma solicitado."""
    if not lang_code:
        return GOLDEN_RULE_MESSAGES[DEFAULT_LANGUAGE]
    code = str(lang_code).lower().strip()[:2]
    return GOLDEN_RULE_MESSAGES.get(code, GOLDEN_RULE_MESSAGES[DEFAULT_LANGUAGE])


def detect_language_heuristic(text: str) -> str:
    """
    Detecta heuristicamente o idioma com base em padrões lexicais e palavras-chave.
    Rápido, sem overhead de modelos externos, com fallback para 'pt'.
    """
    if not text or not text.strip():
        return DEFAULT_LANGUAGE

    words = set(re.findall(r"\b\w+\b", text.lower()))

    # Marcadores fortes de Crioulo Haitiano (Kreyòl)
    kreyol_markers = {"mwen", "nou", "yo", "kijan", "koman", "ki", "nan", "pou", "gen", "fè", "pa", "se", "sa", "bagay", "vle"}
    if len(words & kreyol_markers) >= 2 or any(w in {"kijan", "koman", "mwen"} for w in words):
        return "ht"

    # Marcadores de Francês
    french_markers = {"bonjour", "comment", "pourquoi", "est-ce", "je", "vous", "nous", "avec", "pour", "dans", "carte", "titre", "séjour"}
    if len(words & french_markers) >= 2 or any(w in {"comment", "pourquoi", "bonjour"} for w in words):
        return "fr"

    # Marcadores de Espanhol
    spanish_markers = {"como", "donde", "cuando", "por", "favor", "necesito", "tramite", "solicitar", "permiso", "residencia", "extranjero"}
    if len(words & spanish_markers) >= 2 or any(w in {"necesito", "tramite", "solicitar"} for w in words):
        return "es"

    # Marcadores de Inglês
    english_markers = {"how", "what", "where", "when", "why", "can", "apply", "visa", "need", "document", "passport", "status"}
    if len(words & english_markers) >= 2 or any(w in {"how", "what", "where", "passport"} for w in words):
        return "en"

    return DEFAULT_LANGUAGE
