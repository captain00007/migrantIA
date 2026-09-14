"""
Ferramenta de Busca Externa com Whitelist Estrita do MigrantIA.
Executa buscas na web exclusivamente filtradas pelos domínios homologados de WhitelistDomain.
"""
import logging
from typing import List, Dict, Any, Optional
from django.conf import settings
from apps.sources.models import WhitelistDomain
from ia.retrieval.filters import is_domain_whitelisted, filter_whitelisted_sources

logger = logging.getLogger(__name__)


class WhitelistSearchTool:
    """
    Ferramenta de busca web com restrição constitucional forçada de domínios.
    """

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or getattr(settings, "TAVILY_API_KEY", None)

    def get_active_whitelist_domains(self) -> List[str]:
        """Obtém a lista atual de domínios homologados ativos no banco."""
        try:
            return list(
                WhitelistDomain.objects.filter(is_active=True).values_list("domain", flat=True)
            )
        except Exception as e:
            logger.warning(f"Não foi possível carregar domínios do banco: {e}")
            return ["gov.br", "planalto.gov.br", "dpu.def.br", "acnur.org", "iom.int"]

    def search(
        self,
        query: str,
        max_results: int = 5,
        allowed_domains: Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Executa a busca na web com filtro estrito de domínios homologados.
        """
        domains = allowed_domains or self.get_active_whitelist_domains()
        if not domains or not query or not query.strip():
            return []

        if self.api_key:
            try:
                from tavily import TavilyClient
                client = TavilyClient(api_key=self.api_key)
                response = client.search(
                    query=query,
                    max_results=max_results,
                    include_domains=domains,
                    search_depth="advanced"
                )
                raw_results = response.get("results", [])
                formatted = [
                    {
                        "title": r.get("title", ""),
                        "url": r.get("url", ""),
                        "content": r.get("content", ""),
                        "score": r.get("score", 0.0),
                    }
                    for r in raw_results
                ]
                return filter_whitelisted_sources(formatted, domains)
            except Exception as exc:
                logger.error(f"Erro na busca Tavily: {exc}")

        logger.info(f"[SearchTool] Busca externa solicitada para '{query}' com {len(domains)} domínios.")
        return []


def get_search_tool() -> WhitelistSearchTool:
    """Retorna uma instância da ferramenta de busca na whitelist."""
    return WhitelistSearchTool()
