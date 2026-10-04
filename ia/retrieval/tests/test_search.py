from unittest.mock import Mock, patch
import pytest
from langchain_core.documents import Document
from langchain_core.embeddings import FakeEmbeddings
from ia.retrieval.filters import (
    extract_domain,
    is_domain_whitelisted,
    filter_whitelisted_sources,
    is_spam_or_irrelevant,
    deduplicate_documents,
    calculate_jaccard_similarity,
    calculate_containment,
    calculate_cosine_similarity
)
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


def test_filter_whitelisted_sources_and_spam():
    allowed = ["gov.br", "dpu.def.br"]
    sources = [
        {"title": "PF Agendamento", "url": "https://www.gov.br/pf", "score": 0.85},
        {"title": "Blog Aleatorio", "url": "https://random-site.com/visto", "score": 0.90},
        {"title": "DPU Migrantes", "url": "https://dpu.def.br/migrantes", "score": 0.75},
        {"title": "777 Ola Bet", "url": "https://natal.rn.gov.br/777-ola-bet", "score": 0.60},
        {"title": "Estatísticas de Borussia", "url": "https://conab.gov.br/borussia", "score": 0.55},
        {"title": "Portal Baixo Score", "url": "https://www.gov.br/baixo", "score": 0.20},
    ]
    filtered = filter_whitelisted_sources(sources, allowed, min_score=0.40, filter_spam=True)
    assert len(filtered) == 2
    assert filtered[0]["title"] == "PF Agendamento"
    assert filtered[1]["title"] == "DPU Migrantes"


def test_is_spam_or_irrelevant():
    assert is_spam_or_irrelevant("777 Ola Bet - Quick Entry", "https://natal.rn.gov.br/bet") is True
    assert is_spam_or_irrelevant("Estatísticas de borussia x borussia mönchengladbach", "https://sisdep.conab.gov.br/apps") is True
    assert is_spam_or_irrelevant("Cassino Online Fortune Tiger", "https://voltaredonda.rj.gov.br/game") is True
    assert is_spam_or_irrelevant("Como solicitar a Carteira de Registro Nacional Migratório", "https://www.gov.br/pf/rnm") is False


def test_whitelist_search_tool_empty():
    tool = WhitelistSearchTool(api_key="")
    results = tool.search("Como tirar CPF?", allowed_domains=["gov.br"])
    assert results == []


def test_deduplicate_documents_structural_near_duplicates():
    doc1 = Document(
        page_content="Para solicitar o CPF, o imigrante deve comparecer à Receita Federal com passaporte e comprovante de endereço.",
        metadata={"title": "Guia CPF 1", "page": 1}
    )
    doc2 = Document(
        page_content="Para solicitar o CPF, o imigrante deve comparecer à Receita Federal portando passaporte e comprovante de endereço.",
        metadata={"title": "Guia CPF 2", "page": 1}
    )
    doc3 = Document(
        page_content="A revalidação de diplomas estrangeiros é realizada por meio da Plataforma Carolina Bori nas universidades públicas.",
        metadata={"title": "Guia Diplomas", "page": 5}
    )

    docs = [doc1, doc2, doc3]
    deduped = deduplicate_documents(docs, max_jaccard=0.70)

    assert len(deduped) == 2
    assert deduped[0].page_content == doc1.page_content
    assert deduped[1].page_content == doc3.page_content


def test_deduplicate_documents_pure_semantic_cosine():
    doc1 = Document(
        page_content="O estrangeiro necessita comparecer ao fisco portando seu documento de viagem.",
        metadata={"title": "Doc A"}
    )
    doc2 = Document(
        page_content="O migrante precisa ir à Receita Federal com o passaporte.",
        metadata={"title": "Doc B"}
    )
    doc3 = Document(
        page_content="A matrícula escolar para crianças migrantes na rede pública independe da situação documental dos pais.",
        metadata={"title": "Doc C"}
    )

    # Mock de embeddings onde doc1 e doc2 têm vetores com cosseno 0.95 (mesmo sentido puro)
    # e doc3 tem vetor ortogonal
    mock_emb = Mock()
    mock_emb.embed_documents.return_value = [
        [1.0, 0.0, 0.0],
        [0.98, 0.02, 0.0],  # Cosseno ~ 0.99 com doc1
        [0.0, 1.0, 0.0],    # Ortogonal
    ]

    docs = [doc1, doc2, doc3]
    deduped = deduplicate_documents(docs, embedding_service=mock_emb, max_semantic_similarity=0.88)

    # doc2 deve ser descartado por similaridade de sentido puro com doc1
    assert len(deduped) == 2
    assert deduped[0].page_content == doc1.page_content
    assert deduped[1].page_content == doc3.page_content


def test_calculate_cosine_similarity():
    v1 = [1.0, 0.0]
    v2 = [1.0, 0.0]
    v3 = [0.0, 1.0]
    assert calculate_cosine_similarity(v1, v2) == pytest.approx(1.0)
    assert calculate_cosine_similarity(v1, v3) == pytest.approx(0.0)
