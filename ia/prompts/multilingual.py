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
from typing import Dict, List, Set

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

GREETING_MESSAGES: Dict[str, str] = {
    "pt": (
        "Olá! Sou o MigrantIA, seu assistente oficial e seguro de apoio no Brasil. "
        "Como posso ajudar você hoje com documentação, CPF, refúgio, trabalho ou educação?"
    ),
    "ht": (
        "Bonjou! Mwen se MigrantIA, asistan ofisyèl ou pou sipòte w nan Brezil. "
        "Kijan mwen ka ede w jodi a ak papye, CPF, refij, travay oswa edikasyon?"
    ),
    "fr": (
        "Bonjour ! Je suis MigrantIA, votre assistant officiel de soutien au Brésil. "
        "Comment puis-je vous aider aujourd'hui avec vos documents, CPF, asile, travail ou études ?"
    ),
    "es": (
        "¡Hola! Soy MigrantIA, tu asistente oficial de apoyo en Brasil. "
        "¿Cómo puedo ayudarte hoy con trámites, CPF, refugio, trabajo o educación?"
    ),
    "en": (
        "Hello! I am MigrantIA, your official support assistant in Brazil. "
        "How can I help you today with legal documents, CPF, asylum, work, or education?"
    ),
}

GREETING_PHRASES: Set[str] = {
    "ola", "olá", "oi", "oie", "bom dia", "boa tarde", "boa noite", "ola migrantia", "oi migrantia",
    "bonjour", "bonsoir", "salut", "bonjour migrantia",
    "hola", "buenos dias", "buenos días", "buenas tardes", "buenas noches", "hola migrantia",
    "hello", "hi", "hey", "good morning", "good afternoon", "good evening", "hello migrantia",
    "bonjou", "bonswa", "sak pase", "koman ou ye", "koman ou ye?", "alo", "alô",
}


def get_golden_rule_fallback(lang_code: str = DEFAULT_LANGUAGE) -> str:
    """Retorna a mensagem da Regra de Ouro no idioma solicitado."""
    if not lang_code:
        return GOLDEN_RULE_MESSAGES[DEFAULT_LANGUAGE]
    code = str(lang_code).lower().strip()[:2]
    return GOLDEN_RULE_MESSAGES.get(code, GOLDEN_RULE_MESSAGES[DEFAULT_LANGUAGE])


def get_greeting_message(lang_code: str = DEFAULT_LANGUAGE) -> str:
    """Retorna a mensagem acolhedora de boas-vindas no idioma solicitado."""
    if not lang_code:
        return GREETING_MESSAGES[DEFAULT_LANGUAGE]
    code = str(lang_code).lower().strip()[:2]
    return GREETING_MESSAGES.get(code, GREETING_MESSAGES[DEFAULT_LANGUAGE])


def is_greeting_message(text: str) -> bool:
    """Verifica se a mensagem do usuário é apenas uma saudação inicial."""
    if not text:
        return False
    normalized = re.sub(r"[^\w\s]", "", text.strip().lower())
    return normalized in GREETING_PHRASES or text.strip().lower() in GREETING_PHRASES


def detect_language_heuristic(text: str) -> str:
    """
    Detecta heuristicamente o idioma com base em padrões lexicais e palavras-chave.
    Rápido, sem overhead de modelos externos, com fallback para 'pt'.
    """
    if not text or not text.strip():
        return DEFAULT_LANGUAGE

    words = set(re.findall(r"\b\w+\b", text.lower()))

    # Marcadores fortes de Crioulo Haitiano (Kreyòl)
    kreyol_markers = {"mwen", "nou", "yo", "kijan", "koman", "ki", "nan", "pou", "gen", "fè", "pa", "se", "sa", "bagay", "vle", "bonjou", "bonswa", "pase"}
    if len(words & kreyol_markers) >= 2 or any(w in {"kijan", "koman", "mwen", "bonjou", "bonswa"} for w in words):
        return "ht"

    # Marcadores de Francês
    french_markers = {"bonjour", "bonsoir", "salut", "comment", "pourquoi", "est-ce", "je", "vous", "nous", "avec", "pour", "dans", "carte", "titre", "séjour"}
    if len(words & french_markers) >= 2 or any(w in {"comment", "pourquoi", "bonjour", "bonsoir"} for w in words):
        return "fr"

    # Marcadores de Espanhol
    spanish_markers = {"hola", "buenos", "dias", "tardes", "como", "donde", "cuando", "por", "favor", "necesito", "tramite", "solicitar", "permiso", "residencia", "extranjero"}
    if len(words & spanish_markers) >= 2 or any(w in {"necesito", "tramite", "solicitar", "hola"} for w in words):
        return "es"

    # Marcadores de Inglês
    english_markers = {"hello", "hi", "hey", "how", "what", "where", "when", "why", "can", "apply", "visa", "need", "document", "passport", "status"}
    if len(words & english_markers) >= 2 or any(w in {"how", "what", "where", "passport", "hello"} for w in words):
        return "en"

    return DEFAULT_LANGUAGE
