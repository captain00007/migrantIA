"""
Módulo de compatibilidade retroativa para a camada de ingestão do MigrantIA.
Re-exporta todos os loaders e utilitários de `ia.ingestion.loaders`.
"""

from ia.ingestion.loaders import (
    BaseDocumentLoader,
    ContentLoader,
    DEFAULT_USER_AGENT,
    DocxLoader,
    DocumentLoader,
    DocumentSource,
    fetch_and_clean_page,
    is_url_whitelisted,
    PDFLoader,
    WebLoader,
    WhitelistedWebLoader,
)

__all__ = [
    "BaseDocumentLoader",
    "DocumentSource",
    "DEFAULT_USER_AGENT",
    "WhitelistedWebLoader",
    "WebLoader",
    "is_url_whitelisted",
    "fetch_and_clean_page",
    "DocumentLoader",
    "PDFLoader",
    "DocxLoader",
    "ContentLoader",
]
