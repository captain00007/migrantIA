"""
Módulo de Proteção de Dados e Governança LGPD do MigrantIA.
Detecta e higieniza automaticamente dados pessoais sensíveis (PII) antes da persistência
e antes do envio para provedores externos de LLM.
"""
import re
from ia.security.normalizer import normalize_unicode_input

# 1. E-mail
EMAIL_REGEX = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b")

# 2. CPF formatado (ex: 123.456.789-00 ou 123 . 456 . 789 - 00)
CPF_FORMATTED_REGEX = re.compile(r"\b\d{3}\s*\.\s*\d{3}\s*\.\s*\d{3}\s*-\s*\d{2}\b")

# 3. Telefone celular / fixo brasileiro / internacional (ex: +55 11 98765-4321, (11) 98765-4321, 11988887777, +509 1234 5678)
PHONE_REGEX = re.compile(
    r"(?:\+?\d{1,3}[\s-]?)?(?:\(?([1-9]{2})\)?[\s-]?)?(?:9\s?\d{4}[-\s]?\d{4}|[2-8]\d{3}[-\s]?\d{4}|\b\d{4}[-\s]?\d{4})\b"
)

# 4. CPF não formatado (11 dígitos contínuos)
CPF_RAW_REGEX = re.compile(r"\b\d{11}\b")

# 5. Documentos de identificação (Passaporte, RNM / RNE)
PASSPORT_REGEX = re.compile(r"\b[A-Z]{2}\s*\d{6,7}\b", re.IGNORECASE)
RNM_RNE_REGEX = re.compile(r"\b[A-Z]\s*\d{6,7}\s*[A-Z0-9]?\b", re.IGNORECASE)


def sanitize_pii(text: str) -> str:
    """
    Substitui dados pessoais identificáveis (PII) por marcadores anônimos seguros.
    Aplica normalização Unicode prévia para capturar caracteres Full-Width e variações.
    """
    if not text:
        return ""

    # Normaliza antes de aplicar as regexes para capturar １２３ e caracteres homóglifos
    sanitized = normalize_unicode_input(text)

    # 1. Sanitiza Email
    sanitized = EMAIL_REGEX.sub("[EMAIL_REDACTED]", sanitized)

    # 2. Sanitiza CPF formatado (123.456.789-00)
    sanitized = CPF_FORMATTED_REGEX.sub("[CPF_REDACTED]", sanitized)

    # 3. Sanitiza Passaporte
    sanitized = PASSPORT_REGEX.sub("[PASSPORT_REDACTED]", sanitized)

    # 4. Sanitiza Telefones
    sanitized = PHONE_REGEX.sub("[PHONE_REDACTED]", sanitized)

    # 5. Sanitiza CPF não formatado remanescente
    sanitized = CPF_RAW_REGEX.sub("[CPF_REDACTED]", sanitized)

    # 6. Sanitiza RNM / RNE
    sanitized = RNM_RNE_REGEX.sub("[RNM_REDACTED]", sanitized)

    return sanitized


def has_pii(text: str) -> bool:
    """
    Verifica se o texto contém dados pessoais sensíveis detectáveis.
    """
    if not text:
        return False

    normalized = normalize_unicode_input(text)
    return bool(
        EMAIL_REGEX.search(normalized)
        or CPF_FORMATTED_REGEX.search(normalized)
        or PASSPORT_REGEX.search(normalized)
        or PHONE_REGEX.search(normalized)
        or CPF_RAW_REGEX.search(normalized)
        or RNM_RNE_REGEX.search(normalized)
    )
