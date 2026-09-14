from unittest.mock import Mock, patch
import pytest
from ia.retrieval.filters import extract_domain, is_domain_whitelisted, filter_whitelisted_sources
from ia.retrieval.search import WhitelistSearchTool


def test_extract_domain():
    assert extract_domain("https://www.gov.br/pf/pt-br") == "www.gov.br"
    assert extract_domain("http://dpu.def.br:8080/path") == "dpu.def.br"
    assert extract_domain("acnur.org/brasil") == "acnur.org"
    assert extract_domain("") == ""


def test_is_domain_whitelisted():
    allowed = ["gov.br", "dpu.def.br", "acnur.org"]
    assert is_domain_whitelisted("https://www.gov.br/pf", allowed) is True
    assert is_domain_whitelisted("https://dpu.def.br/ajuda", allowed) is True
    assert is_domain_whitelisted("https://help.acnur.org/brasil", allowed) is True
    assert is_domain_whitelisted("https://blog-fake-noticias.com/pf", allowed) is False
    assert is_domain_whitelisted("https://gov.br.attacker.com", allowed) is False


def test_filter_whitelisted_sources():
    allowed = ["gov.br", "dpu.def.br"]
    sources = [
        {"title": "PF", "url": "https://www.gov.br/pf"},
        {"title": "Blog", "url": "https://random-site.com/visto"},
        {"title": "DPU", "url": "https://dpu.def.br/migrantes"}
    ]
    filtered = filter_whitelisted_sources(sources, allowed)
    assert len(filtered) == 2
    assert filtered[0]["title"] == "PF"
    assert filtered[1]["title"] == "DPU"


def test_whitelist_search_tool_empty():
    tool = WhitelistSearchTool(api_key=None)
    results = tool.search("Como tirar CPF?", allowed_domains=["gov.br"])
    assert results == []
