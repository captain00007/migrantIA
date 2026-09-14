"""
Filtros de governanca e seguranca para dominios homologados (Whitelist) do MigrantIA.
"""
from typing import List, Optional
from urllib.parse import urlparse


def extract_domain(url_or_domain: str) -> str:
    """Extrai o dominio limpo de uma URL ou string."""
    if not url_or_domain:
        return ""
    cleaned = url_or_domain.strip().lower()
    if not cleaned.startswith(("http://", "https://")):
        cleaned = "https://" + cleaned
    parsed = urlparse(cleaned)
    netloc = parsed.netloc or parsed.path
    if ":" in netloc:
        netloc = netloc.split(":")[0]
    return netloc


def is_domain_whitelisted(url: str, allowed_domains: List[str]) -> bool:
    """
    Verifica se a URL ou dominio pertence estritamente a whitelist homologada.
    Suporta correspondencia exata ou subdominios (ex: pf.gov.br dentro de gov.br).
    """
    if not url or not allowed_domains:
        return False

    target_domain = extract_domain(url)
    if not target_domain:
        return False

    for allowed in allowed_domains:
        clean_allowed = extract_domain(allowed)
        if not clean_allowed:
            continue
        if target_domain == clean_allowed or target_domain.endswith("." + clean_allowed):
            return True

    return False


def filter_whitelisted_sources(
    sources: List[dict],
    allowed_domains: List[str]
) -> List[dict]:
    """Filtra uma lista de fontes externas retendo apenas as pertencentes a whitelist."""
    filtered = []
    for src in sources:
        url = src.get("url", "")
        if is_domain_whitelisted(url, allowed_domains):
            filtered.append(src)
    return filtered
