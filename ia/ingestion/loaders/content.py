"""
Módulo fachada unificada de ingestão para o MigrantIA.
Roteia automaticamente entre páginas web, arquivos remotos homologados e documentos locais/memória.
"""

import io
import re
import urllib.parse
from pathlib import Path
from typing import Any, Dict, List, Optional

import requests

from ia.ingestion.loaders.base import DocumentSource
from ia.ingestion.loaders.document import DocumentLoader
from ia.ingestion.loaders.web import WhitelistedWebLoader


class ContentLoader:
    """
    Fachada unificada e inteligente para carregamento de qualquer conteúdo no MigrantIA.
    Roteia automaticamente para WhitelistedWebLoader ou DocumentLoader (PyPDF, Docx2txt, TextLoader).
    """

    def __init__(
        self,
        allowed_domains: Optional[List[str]] = None,
        timeout: int = 15,
        user_agent: Optional[str] = None
    ) -> None:
        self.web_loader = WhitelistedWebLoader(
            allowed_domains=allowed_domains,
            timeout=timeout,
            user_agent=user_agent
        )
        self.doc_loader = DocumentLoader()

    @property
    def allowed_domains(self) -> List[str]:
        """Lista de domínios homologados para raspagem e download."""
        return self.web_loader.allowed_domains

    def is_url_whitelisted(self, url: str) -> bool:
        """Valida se uma URL pertence à lista de domínios homologados."""
        return self.web_loader.is_url_whitelisted(url)

    def load_web(self, url: str, **kwargs: Any) -> Dict[str, Any]:
        """Carrega página web via WebBaseLoader com validação de Whitelist."""
        return self.web_loader.load(url, **kwargs)

    def load_file(
        self,
        source: DocumentSource,
        file_type: Optional[str] = None,
        **kwargs: Any
    ) -> Dict[str, Any]:
        """Carrega qualquer arquivo/documento (PDF, DOCX, TXT, etc.) de forma unificada."""
        return self.doc_loader.load(source, file_type=file_type, **kwargs)

    def load_pdf(self, source: DocumentSource, **kwargs: Any) -> Dict[str, Any]:
        """Alias especializado para carregamento de PDF."""
        return self.load_file(source, file_type="pdf", **kwargs)

    def load_docx(self, source: DocumentSource, **kwargs: Any) -> Dict[str, Any]:
        """Alias especializado para carregamento de DOCX."""
        return self.load_file(source, file_type="docx", **kwargs)

    @staticmethod
    def _is_remote_url(source: Any) -> bool:
        """Verifica se a fonte informada é uma URL web (HTTP/HTTPS)."""
        if isinstance(source, (str, Path)):
            src_str = str(source).strip().lower()
            return src_str.startswith("http://") or src_str.startswith("https://")
        return False

    @staticmethod
    def _extract_remote_file_extension(url: str) -> Optional[str]:
        """
        Extrai a extensão do arquivo a partir de parsed.path,
        garantindo compatibilidade com URLs contendo query parameters.
        """
        parsed = urllib.parse.urlparse(str(url).strip())
        path_lower = parsed.path.lower()
        match = re.search(r"\.(pdf|docx|doc|txt|md|markdown|csv|json|html|htm)$", path_lower)
        return match.group(1) if match else None

    def _download_remote_file(self, url: str) -> bytes:
        """Valida a URL contra a Whitelist e faz o download seguro do arquivo."""
        if not self.is_url_whitelisted(url):
            raise ValueError(
                f"Segurança: URL de arquivo '{url}' não pertence à Whitelist!"
            )
        resp = requests.get(
            url,
            headers=self.web_loader.headers,
            timeout=self.web_loader.timeout
        )
        resp.raise_for_status()
        return resp.content

    def load(
        self,
        source: DocumentSource,
        loader_type: Optional[str] = None,
        **kwargs: Any
    ) -> Dict[str, Any]:
        """
        Método unificado e agnóstico de entrada:
        - Carrega URLs da web (HTML) via WhitelistedWebLoader.
        - Baixa e processa arquivos remotos (.pdf, .docx, etc.) de domínios homologados.
        - Carrega documentos locais e buffers de memória (.pdf, .docx, .txt) via DocumentLoader.
        """
        if loader_type:
            l_type = loader_type.lower().strip()
            if l_type == "web":
                return self.load_web(str(source), **kwargs)
            return self.load_file(source, file_type=l_type, **kwargs)

        if self._is_remote_url(source):
            url_str = str(source).strip()
            remote_ext = self._extract_remote_file_extension(url_str)
            if remote_ext:
                content_bytes = self._download_remote_file(url_str)
                return self.load_file(
                    io.BytesIO(content_bytes),
                    file_type=remote_ext,
                    url=url_str,
                    **kwargs
                )
            return self.load_web(url_str, **kwargs)

        if isinstance(source, (str, Path, bytes, io.BytesIO)):
            return self.load_file(source, **kwargs)

        raise ValueError(f"Não foi possível identificar o loader para a fonte: {source}")
