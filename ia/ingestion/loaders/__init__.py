"""
Subpacote de loaders de documentos para o MigrantIA.
"""

from ia.ingestion.loaders.base import (
    BaseDocumentLoader,
    DEFAULT_USER_AGENT,
    DocumentSource,
)
from ia.ingestion.loaders.content import ContentLoader
from ia.ingestion.loaders.document import (
    DocxLoader,
    DocumentLoader,
    PDFLoader,
)
from ia.ingestion.loaders.web import (
    fetch_and_clean_page,
    is_url_whitelisted,
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
