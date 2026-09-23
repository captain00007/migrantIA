"""
Módulo de Segurança e Sanitização de Saída (OutputGuard).
Protege o cliente contra Data Exfiltration via Markdown, injeção de HTML/Scripts,
vazamento de links não homologados e vazamento de Canary Tokens ou PII.
"""
import re
from typing import Tuple, Optional, Set
from ia.security.canary import CanaryManager

# Esquemas de URL perigosos
DANGEROUS_PROTOCOLS_REGEX = re.compile(
    r"\b(?:javascript|data|vbscript|file|about):",
    re.IGNORECASE
)

# Tags HTML perigosas
HTML_TAG_REGEX = re.compile(r"<[^>]+>", re.IGNORECASE)

# Markdown Image Tag: ![alt](url) -> Vetor clássico de exfiltração de dados
MARKDOWN_IMAGE_REGEX = re.compile(r"!\[(.*?)\]\([^)]+\)")

# Markdown Link Regex suportando URLs com parênteses aninhados (ex: javascript:alert(1))
MARKDOWN_LINK_REGEX = re.compile(r"\[([^\]]+)\]\(((?:[^()\s]+|\([^()\s]*\))+)\)")


class OutputGuard:
    """Filtro de segurança e higienização pós-geração."""

    @classmethod
    def sanitize(
        cls,
        output_text: str,
        canary_token: Optional[str] = None
    ) -> Tuple[str, bool, Optional[str]]:
        """
        Aplica sanitização estrita no texto gerado pelo LLM:
        1. Verifica vazamento de Canary Token.
        2. Neutraliza tags de imagem Markdown (![alt](url) -> [alt]).
        3. Remove tags HTML potencialmente maliciosas.
        4. Neutraliza URLs com protocolos perigosos em links Markdown.
        5. Re-aplica PII Masking para prevenir vazamento residual.

        Retorna:
          (sanitized_text, is_safe, violation_reason)
        """
        if not output_text:
            return "", True, None

        # 1. Detecção de vazamento do Canary Token
        if canary_token and CanaryManager.check_leakage(output_text, canary_token):
            return "", False, "canary_leakage_detected"

        sanitized = output_text

        # 2. Neutralização de tags de imagem Markdown (Anti-Data Exfiltration)
        sanitized = MARKDOWN_IMAGE_REGEX.sub(r"[\1]", sanitized)

        # 3. Remoção de tags HTML perigosas
        sanitized = HTML_TAG_REGEX.sub("", sanitized)

        # 4. Neutralização de protocolos maliciosos em links Markdown
        def sanitize_link(match):
            text = match.group(1)
            url = match.group(2).strip()
            if DANGEROUS_PROTOCOLS_REGEX.search(url):
                return text  # Remove o link inseguro, mantém apenas o texto
            return f"[{text}]({url})"

        sanitized = MARKDOWN_LINK_REGEX.sub(sanitize_link, sanitized)

        # 5. Redação residual de PII (import local para evitar import circular)
        from apps.chat.privacy import sanitize_pii
        sanitized = sanitize_pii(sanitized)

        return sanitized, True, None
