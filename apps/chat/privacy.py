"""
Módulo de Proteção de Dados e Governança LGPD do MigrantIA.
Detecta e higieniza automaticamente dados pessoais sensíveis (PII) antes da persistência
e antes do envio para provedores externos de LLM.
"""
import re

# 1. E-mail
EMAIL_REGEX = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b")

# 2. CPF formatado (ex: 123.456.789-00)
CPF_FORMATTED_REGEX = re.compile(r"\b\d{3}\.\d{3}\.\d{3}-\d{2}\b")

# 3. Telefone celular / fixo brasileiro (com ou sem DDD, com ou sem formatação, ex: (11) 98765-4321, 11988887777, +55 11 98765-4321)
PHONE_REGEX = re.compile(
    r"(?:\+?55\s?)?(?:\(?([1-9]{2})\)?\s?)?(?:9\s?\d{4}[-\s]?\d{4}|[2-8]\d{3}[-\s]?\d{4})\b"
)

# 4. CPF não formatado (11 dígitos contínuos que não correspondam a padrão típico de celular com DDD)
CPF_RAW_REGEX = re.compile(r"\b\d{11}\b")

# 5. Documentos de identificação (Passaporte, RNM / RNE)
PASSPORT_REGEX = re.compile(r"\b[A-Z]{2}\d{6,7}\b", re.IGNORECASE)
RNM_RNE_REGEX = re.compile(r"\b[A-Z]\d{6,7}[A-Z0-9]?\b", re.IGNORECASE)


def sanitize_pii(text: str) -> str:
    """
    Substitui dados pessoais identificáveis (PII) por marcadores anônimos seguros.
    A ordem de execução previne falsos positivos entre telefones e CPFs não formatados.
    """
    if not text:
        return ""

    sanitized = text

    # 1. Sanitiza Email
    sanitized = EMAIL_REGEX.sub("[EMAIL_REDACTED]", sanitized)

    # 2. Sanitiza CPF formatado (123.456.789-00)
    sanitized = CPF_FORMATTED_REGEX.sub("[CPF_REDACTED]", sanitized)

    # 3. Sanitiza Passaporte
    sanitized = PASSPORT_REGEX.sub("[PASSPORT_REDACTED]", sanitized)

    # 4. Sanitiza Telefones (ex: 11988887777, (11) 98888-7777, etc)
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

    return bool(
        EMAIL_REGEX.search(text)
        or CPF_FORMATTED_REGEX.search(text)
        or PASSPORT_REGEX.search(text)
        or PHONE_REGEX.search(text)
        or CPF_RAW_REGEX.search(text)
        or RNM_RNE_REGEX.search(text)
    )
