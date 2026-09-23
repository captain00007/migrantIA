"""
Módulo de Normalização de Entrada e Desobfuscação (Input Normalizer).
Aplica normalização Unicode NFKC, remoção de caracteres invisíveis/zero-width,
normalização de homóglifos (cirílico/grego) e detecção de codificações adversárias (Base64/Hex).
"""
import base64
import binascii
import re
import unicodedata
from typing import Tuple, Optional

# Caracteres invisíveis, formatadores e controles bidirecionais perigosos
INVISIBLE_CHARS_REGEX = re.compile(
    r"[\u200B-\u200F\uFEFF\u00AD\u2060-\u206F\u202A-\u202E\uFFF0-\uFFFF]",
    re.UNICODE
)

# Mapa de substituição de Homóglifos Cirílicos e Gregos para caracteres Latinos correspondentes
HOMOGLYPH_MAP = {
    # Cirílico minúsculo
    "а": "a", "е": "e", "о": "o", "р": "p", "с": "c", "у": "y", "х": "x",
    "і": "i", "ј": "j", "ѕ": "s", "ԁ": "d", "ԛ": "q", "ԝ": "w",
    # Cirílico maiúsculo
    "А": "A", "В": "B", "Е": "E", "К": "K", "М": "M", "Н": "H", "О": "O",
    "Р": "P", "С": "C", "Т": "T", "Х": "X", "І": "I", "Ј": "J", "Ѕ": "S",
    # Grego
    "α": "a", "ο": "o", "ν": "v", "ρ": "p", "τ": "t", "κ": "k",
    "Α": "A", "Β": "B", "Ε": "E", "Ζ": "Z", "Η": "H", "Ι": "I",
    "Κ": "K", "Μ": "M", "Ν": "N", "Ο": "O", "Ρ": "P", "Τ": "T", "Χ": "X",
}

HOMOGLYPH_TRANSLATION_TABLE = str.maketrans(HOMOGLYPH_MAP)

SUSPICIOUS_DECODED_KEYWORDS = [
    r"\bignore\b", r"\bsystem\b", r"\bprompt\b", r"\bpassword\b",
    r"\bsecret\b", r"\badmin\b", r"\bbypass\b", r"\bjailbreak\b",
    r"\binstruções\b", r"\binstrucciones\b", r"\binstructions\b"
]
COMPILED_SUSPICIOUS_REGEX = re.compile(
    "|".join(SUSPICIOUS_DECODED_KEYWORDS),
    re.IGNORECASE
)


def normalize_unicode_input(text: str) -> str:
    """
    Normaliza a entrada do usuário removendo ofuscações:
    1. Remove caracteres invisíveis, zero-width e marcadores de override bidirecionais.
    2. Converte caracteres Full-Width e variações para ASCII/Compatibilidade via NFKC.
    3. Normaliza homóglifos conhecidos (Cirílico/Grego) para seus equivalentes latinos.
    4. Colapsa espaços e quebras de linha duplicadas.
    """
    if not text:
        return ""

    # 1. Remover caracteres invisíveis e de controle
    cleaned = INVISIBLE_CHARS_REGEX.sub("", text)

    # 2. Normalização de Compatibilidade (NFKC)
    cleaned = unicodedata.normalize("NFKC", cleaned)

    # 3. Transliteração de homóglifos conhecidos
    cleaned = cleaned.translate(HOMOGLYPH_TRANSLATION_TABLE)

    # 4. Colapso de múltiplos espaços
    cleaned = re.sub(r"\s+", " ", cleaned).strip()

    return cleaned


def is_obfuscated_encoding(text: str) -> Tuple[bool, Optional[str]]:
    """
    Detecta se o texto contém blocos Base64 ou Hexadecimais suspeitos contendo comandos adversários.
    Retorna (is_malicious, detected_reason).
    """
    if not text or len(text) < 12:
        return False, None

    # 1. Checagem de Base64
    b64_matches = re.findall(r"[A-Za-z0-9+/]{12,}={0,2}", text)
    for match in b64_matches:
        try:
            decoded_bytes = base64.b64decode(match, validate=True)
            decoded_str = decoded_bytes.decode("utf-8", errors="ignore").lower()
            if COMPILED_SUSPICIOUS_REGEX.search(decoded_str):
                return True, "base64_injection_payload"
        except (binascii.Error, ValueError):
            pass

    # 2. Checagem de Hexadecimal (ex: 69676e6f7265...)
    hex_matches = re.findall(r"\b(?:[0-9a-fA-F]{2}){8,}\b", text)
    for match in hex_matches:
        try:
            decoded_bytes = bytes.fromhex(match)
            decoded_str = decoded_bytes.decode("utf-8", errors="ignore").lower()
            if COMPILED_SUSPICIOUS_REGEX.search(decoded_str):
                return True, "hex_injection_payload"
        except (ValueError, binascii.Error):
            pass

    return False, None
