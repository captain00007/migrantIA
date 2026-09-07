"""
Módulo responsável exclusivamente pela ingestão de páginas Web e extração semântica.
Utiliza Trafilatura para extração limpa de conteúdo e remoção de boilerplate,
com enriquecimento semântico de Schema.org JSON-LD e validação de Whitelist.
"""

import json
import re
import urllib.parse
from typing import Any, Dict, List, Optional

import trafilatura
from bs4 import BeautifulSoup
from langchain_community.document_loaders import WebBaseLoader
from langchain_core.documents import Document

from ia.ingestion.loaders.base import (
    BaseDocumentLoader,
    DEFAULT_USER_AGENT,
    DocumentSource,
)


def is_url_whitelisted(url: str, allowed_domains: List[str]) -> bool:
    """
    Valida se o domínio da URL pertence à lista de domínios homologados da Whitelist.
    Garante que subdomínios oficiais (ex: pf.gov.br) sejam permitidos e domínios não autorizados bloqueados.
    """
    if not allowed_domains:
        return False

    try:
        parsed = urllib.parse.urlparse(str(url).strip())
        netloc = parsed.netloc.lower()
        if not netloc:
            return False
        if ":" in netloc:
            netloc = netloc.split(":")[0]

        for domain in allowed_domains:
            domain_clean = domain.lower().strip()
            if not domain_clean:
                continue
            if netloc == domain_clean or netloc.endswith("." + domain_clean):
                return True
        return False
    except Exception:
        return False


class WhitelistedWebLoader(BaseDocumentLoader):
    """
    Carregador web oficial utilizando Trafilatura e WebBaseLoader com enforcement
    rígido de Whitelist de domínios homologados e enriquecimento semântico (JSON-LD / Schema.org).
    """

    def __init__(
        self,
        allowed_domains: Optional[List[str]] = None,
        timeout: int = 15,
        user_agent: Optional[str] = None
    ) -> None:
        self.allowed_domains = [d.lower().strip() for d in (allowed_domains or []) if d.strip()]
        self.timeout = timeout
        self.user_agent = user_agent or DEFAULT_USER_AGENT
        self.headers = {
            "User-Agent": self.user_agent,
            "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
        }

    def set_allowed_domains(self, allowed_domains: List[str]) -> None:
        """Atualiza a lista de domínios permitidos em tempo de execução."""
        self.allowed_domains = [d.lower().strip() for d in allowed_domains if d.strip()]

    def is_url_whitelisted(self, url: str) -> bool:
        """Valida se a URL pertence aos domínios autorizados."""
        return is_url_whitelisted(url, self.allowed_domains)

    def _validate_url(self, url: str) -> None:
        """Valida a conformidade da URL contra a Whitelist homologada."""
        if not self.is_url_whitelisted(url):
            raise ValueError(
                f"Segurança Constitucional: A URL '{url}' não pertence aos domínios homologados da Whitelist!"
            )

    def _scrape(self, url: str, timeout: int) -> BeautifulSoup:
        """Realiza a raspagem do conteúdo HTML utilizando WebBaseLoader."""
        loader = WebBaseLoader(
            web_paths=(url,),
            header_template=self.headers,
            requests_kwargs={"timeout": timeout},
        )
        return loader.scrape()

    def _extract_json_ld_faqs(self, soup: BeautifulSoup) -> str:
        """Extrai perguntas frequentes estruturadas em Schema.org JSON-LD."""
        faq_items: List[str] = []
        for script in soup.find_all("script", type="application/ld+json"):
            if not script.string:
                continue
            try:
                data = json.loads(script.string.strip())
                items = data if isinstance(data, list) else [data]
                for item in items:
                    if isinstance(item, dict) and item.get("@type") == "FAQPage":
                        for entity in item.get("mainEntity", []):
                            q = entity.get("name") or entity.get("question", "")
                            a_obj = entity.get("acceptedAnswer") or entity.get("answer", {})
                            a = a_obj.get("text", "") if isinstance(a_obj, dict) else str(a_obj)
                            if q and a:
                                a_clean = BeautifulSoup(a, "html.parser").get_text(separator=" ", strip=True)
                                faq_items.append(f"**Pergunta**: {q}\n**Resposta**: {a_clean}")
            except Exception:
                continue

        if faq_items:
            return "\n\n### Perguntas Frequentes Homologadas (FAQ):\n\n" + "\n\n".join(faq_items)
        return ""

    def _extract_title(self, soup: BeautifulSoup, custom_title: Optional[str], fallback_url: str) -> str:
        """Extrai o título a partir do HTML ou utiliza fallback."""
        if custom_title:
            return custom_title
        if soup.title and soup.title.string:
            return soup.title.string.strip()
        return fallback_url

    def _clean_html(self, soup: BeautifulSoup) -> None:
        """Remove tags irrelevantes e de navegação que poluem o conteúdo textual."""
        for tag in soup(["script", "style", "nav", "footer", "header", "aside", "noscript", "iframe"]):
            tag.decompose()

    def _extract_body_text(self, html_content: str, soup: BeautifulSoup) -> str:
        """
        Extrai o texto principal utilizando Trafilatura (state-of-the-art para remoção de boilerplate),
        com fallback inteligente via BeautifulSoup.
        """
        extracted = trafilatura.extract(
            html_content,
            include_tables=True,
            include_links=False,
            output_format="txt",
            favor_precision=True,
        )

        if extracted and extracted.strip():
            return extracted.strip()

        # Fallback estrutural via BeautifulSoup caso o Trafilatura retorne vazio (fragmentos curtos)
        self._clean_html(soup)
        main_elem = (
            soup.find("main")
            or soup.find("article")
            or soup.find("div", class_=re.compile(r"content|corpo|materia|document-body|main"))
            or soup.body
        )
        body_text = (
            main_elem.get_text(separator="\n", strip=True)
            if main_elem
            else soup.get_text(separator="\n", strip=True)
        )
        return re.sub(r"\n{3,}", "\n\n", body_text).strip()

    def _build_full_text(self, body_text: str, faq_text: str) -> str:
        """Combina o corpo de texto principal com os blocos de FAQ extraídos."""
        return (body_text + (faq_text if faq_text else "")).strip()

    def _build_result(self, url: str, title: str, full_text: str) -> Dict[str, Any]:
        """Constrói o dicionário padronizado de retorno da ingestão."""
        doc_meta = {
            "source": url,
            "title": title,
            "source_type": "web",
            "content_length": len(full_text),
        }
        docs = [Document(page_content=full_text, metadata=doc_meta)]
        return {
            "title": title,
            "text": full_text,
            "source_type": "web",
            "url": url,
            "metadata": doc_meta,
            "documents": docs,
        }

    def load(
        self,
        source: DocumentSource,
        *,
        title: Optional[str] = None,
        timeout: Optional[int] = None,
        **kwargs: Any
    ) -> Dict[str, Any]:
        """
        Carrega o conteúdo da página web via WebBaseLoader e Trafilatura após validar a Whitelist.
        """
        url = str(source).strip()
        self._validate_url(url)

        req_timeout = timeout or self.timeout
        soup = self._scrape(url, req_timeout)
        raw_html = str(soup)

        faq_text = self._extract_json_ld_faqs(soup)
        page_title = self._extract_title(soup, title, url)
        body_text = self._extract_body_text(raw_html, soup)
        full_text = self._build_full_text(body_text, faq_text)

        return self._build_result(url, page_title, full_text)


# Aliases para retrocompatibilidade
WebLoader = WhitelistedWebLoader


def fetch_and_clean_page(url: str, allowed_domains: List[str], timeout: int = 10) -> Optional[Dict[str, Any]]:
    """Função utilitária legada para carregar e limpar página web."""
    loader = WhitelistedWebLoader(allowed_domains=allowed_domains, timeout=timeout)
    try:
        return loader.load(url)
    except Exception as e:
        print(f"Erro ao carregar URL {url}: {e}")
        return None
