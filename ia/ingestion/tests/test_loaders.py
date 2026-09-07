"""
Testes unitários e de integração para o subpacote de loaders do MigrantIA.
"""

import io
import zipfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import docx
import pypdf
import pytest
from bs4 import BeautifulSoup

from ia.ingestion.loaders import (
    BaseDocumentLoader,
    ContentLoader,
    DocxLoader,
    DocumentLoader,
    DocumentSource,
    fetch_and_clean_page,
    is_url_whitelisted,
    PDFLoader,
    WebLoader,
    WhitelistedWebLoader,
)
import ia.ingestion.loader as legacy_loader_module


# =============================================================================
# 1. Tests for Web Loader & Whitelist Security
# =============================================================================

def test_web_loader_whitelist_validation():
    allowed = ["gov.br", "planalto.gov.br", "dpu.def.br", "acnur.org"]
    loader = WebLoader(allowed_domains=allowed)

    # Valid domains and subdomains
    assert loader.is_url_whitelisted("https://www.gov.br/pf/pt-br/assuntos/imigracao") is True
    assert loader.is_url_whitelisted("http://planalto.gov.br/ccivil_03/leis/l13445.htm") is True
    assert loader.is_url_whitelisted("https://atendimento.dpu.def.br/portal") is True
    assert loader.is_url_whitelisted("https://help.acnur.org/brazil/") is True

    # Subdomains with port numbers and case-insensitivity
    assert loader.is_url_whitelisted("HTTPS://WWW.GOV.BR:8080/servicos") is True

    # Invalid / spoofing attempts
    assert loader.is_url_whitelisted("https://blog-falso-vistos.com/noticias") is False
    assert loader.is_url_whitelisted("https://facebook.com/grupo-migrantes") is False
    assert loader.is_url_whitelisted("https://gov.br.attacker.com/scam") is False
    assert loader.is_url_whitelisted("https://evilgov.br/portal") is False
    assert loader.is_url_whitelisted("invalid_url_without_schema") is False


def test_is_url_whitelisted_empty_and_edge_cases():
    assert is_url_whitelisted("https://gov.br", []) is False
    assert is_url_whitelisted("", ["gov.br"]) is False
    assert is_url_whitelisted("https://gov.br", ["   ", ""]) is False


def test_web_loader_security_exception_on_unauthorized_domain():
    loader = WebLoader(allowed_domains=["gov.br"])
    with pytest.raises(ValueError, match="não pertence aos domínios homologados"):
        loader.load("https://site-nao-autorizado.com/pagina")


def test_web_loader_extraction_with_json_ld_faqs():
    sample_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Portal de Serviços de Imigração - Governo Federal</title>
        <script type="application/ld+json">
        {
            "@context": "https://schema.org",
            "@type": "FAQPage",
            "mainEntity": [{
                "@type": "Question",
                "name": "Quem tem direito ao visto humanitário?",
                "acceptedAnswer": {
                    "@type": "Answer",
                    "text": "Nacionais do Haiti e pessoas apátridas afetadas pela crise institucional."
                }
            }]
        }
        </script>
    </head>
    <body>
        <nav><a href="/home">Home</a> | <a href="/menu">Menu</a></nav>
        <header><h1>Barra de Navegação do Governo</h1></header>
        <main>
            <article>
                <h2>Autorização de Residência por Acolhida Humanitária</h2>
                <p>O processo de autorização de residência para haitianos é regido pela Portaria Interministerial MJSP/MRE nº 37/2023.</p>
                <p>O prazo inicial da residência é de 2 anos, podendo ser renovado para prazo indeterminado.</p>
            </article>
        </main>
        <footer><p>Todos os direitos reservados - Governo Federal 2026</p></footer>
    </body>
    </html>
    """
    loader = WebLoader(allowed_domains=["gov.br"])

    with patch("langchain_community.document_loaders.WebBaseLoader.scrape") as mock_scrape:
        mock_scrape.return_value = BeautifulSoup(sample_html, "html.parser")

        result = loader.load("https://www.gov.br/servicos/acolhida-humanitaria")

        assert result["source_type"] == "web"
        assert "Autorização de Residência por Acolhida Humanitária" in result["text"]
        assert "Portaria Interministerial" in result["text"]
        assert "Quem tem direito ao visto humanitário?" in result["text"]
        assert "Nacionais do Haiti e pessoas apátridas" in result["text"]
        assert result["title"] == "Portal de Serviços de Imigração - Governo Federal"
        assert len(result["documents"]) > 0


def test_web_loader_fallback_title_and_clean_tags():
    sample_html = """
    <html>
    <body>
        <script>var x = 10;</script>
        <style>body { color: red; }</style>
        <aside>Publicidade Lateral</aside>
        <main>
            <p>Texto útil sem título formal na página.</p>
        </main>
    </body>
    </html>
    """
    loader = WhitelistedWebLoader(allowed_domains=["gov.br"])
    with patch("langchain_community.document_loaders.WebBaseLoader.scrape") as mock_scrape:
        mock_scrape.return_value = BeautifulSoup(sample_html, "html.parser")
        result = loader.load("https://www.gov.br/noticia-sem-titulo")

        assert result["title"] == "https://www.gov.br/noticia-sem-titulo"
        assert "Texto útil sem título" in result["text"]
        assert "var x = 10" not in result["text"]
        assert "Publicidade Lateral" not in result["text"]


def test_fetch_and_clean_page_helper():
    sample_html = "<html><head><title>Titulo Teste</title></head><body><main><p>Conteúdo</p></main></body></html>"
    with patch("langchain_community.document_loaders.WebBaseLoader.scrape") as mock_scrape:
        mock_scrape.return_value = BeautifulSoup(sample_html, "html.parser")
        res = fetch_and_clean_page("https://www.gov.br/teste", allowed_domains=["gov.br"])
        assert res is not None
        assert res["title"] == "Titulo Teste"

    # Unauthorized domain returns None and logs error without crashing
    res_unauth = fetch_and_clean_page("https://unauth.com", allowed_domains=["gov.br"])
    assert res_unauth is None


# =============================================================================
# 2. Tests for DocumentLoader (PDF, DOCX, TXT, MD, CSV, JSON, HTML)
# =============================================================================

def test_document_loader_pdf_bytes_io():
    writer = pypdf.PdfWriter()
    writer.add_blank_page(width=200, height=200)

    pdf_bytes_io = io.BytesIO()
    writer.write(pdf_bytes_io)
    pdf_bytes_io.seek(0)

    loader = DocumentLoader()
    result = loader.load(pdf_bytes_io, title="Cartilha Oficial de Teste")

    assert result["source_type"] == "pdf"
    assert result["title"] == "Cartilha Oficial de Teste"
    assert result["metadata"]["total_pages"] == 1
    assert len(result["documents"]) == 1


def test_document_loader_docx_bytes_io():
    doc = docx.Document()
    doc.add_heading("Guia de Revalidação de Diplomas", level=1)
    doc.add_paragraph("Este é o parágrafo explicativo da Plataforma Carolina Bori.")

    table = doc.add_table(rows=2, cols=2)
    table.rows[0].cells[0].text = "Pilar"
    table.rows[0].cells[1].text = "Responsável"
    table.rows[1].cells[0].text = "Educação"
    table.rows[1].cells[1].text = "MEC"

    docx_io = io.BytesIO()
    doc.save(docx_io)
    docx_io.seek(0)

    loader = DocumentLoader()
    result = loader.load(docx_io, title="Guia MEC Teste")

    assert result["source_type"] == "docx"
    assert result["title"] == "Guia MEC Teste"
    assert "Guia de Revalidação de Diplomas" in result["text"]
    assert "Plataforma Carolina Bori" in result["text"]
    assert len(result["documents"]) >= 1


def test_document_loader_txt_and_md(tmp_path):
    txt_file = tmp_path / "instrucoes_cpf.txt"
    txt_file.write_text("Instruções oficiais da Receita Federal para emissão de CPF para estrangeiros.", encoding="utf-8")

    loader = DocumentLoader()
    result = loader.load(txt_file)

    assert result["source_type"] == "text"
    assert "Instruções oficiais da Receita Federal" in result["text"]
    assert len(result["documents"]) == 1
    assert result["title"] == "Instrucoes Cpf"

    md_file = tmp_path / "manual.md"
    md_file.write_text("# Manual de Regularização\nPasso 1: Agendamento.", encoding="utf-8")
    result_md = loader.load(md_file)
    assert result_md["source_type"] == "text"
    assert "Manual de Regularização" in result_md["text"]


def test_document_loader_format_detection_zip_vs_docx():
    # 1. Cria um arquivo ZIP genérico (não DOCX)
    non_docx_zip = io.BytesIO()
    with zipfile.ZipFile(non_docx_zip, "w") as zf:
        zf.writestr("test.txt", "Texto de arquivo genérico em ZIP.")
    non_docx_zip.seek(0)

    loader = DocumentLoader()
    # Sem file_type explícito, deve rejeitar classificar ZIP genérico como DOCX
    with pytest.raises(ValueError, match="Não foi possível identificar com segurança o formato"):
        loader.load(non_docx_zip)

    # 2. Cria um ZIP com estrutura OOXML (DOCX via word/document.xml)
    docx_zip = io.BytesIO()
    with zipfile.ZipFile(docx_zip, "w") as zf:
        zf.writestr("word/document.xml", "<w:document></w:document>")
    docx_zip.seek(0)

    detected = DocumentLoader._detect_format_from_bytes(docx_zip.getvalue())
    assert detected == "docx"

    # 3. Cria um ZIP com estrutura OOXML (DOCX via [Content_Types].xml)
    docx_ct_zip = io.BytesIO()
    with zipfile.ZipFile(docx_ct_zip, "w") as zf:
        zf.writestr("[Content_Types].xml", '<Types xmlns="..."><Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/></Types>')
    docx_ct_zip.seek(0)

    detected_ct = DocumentLoader._detect_format_from_bytes(docx_ct_zip.getvalue())
    assert detected_ct == "docx"


def test_document_loader_detect_format_edge_cases():
    # PDF
    assert DocumentLoader._detect_format_from_bytes(b"%PDF-1.4 sample content") == "pdf"

    # Corrompido com cabeçalho ZIP (não deve quebrar e deve retornar 'unknown')
    assert DocumentLoader._detect_format_from_bytes(b"PK\x03\x04corrupted_header_data_without_zip_directory") == "unknown"

    # Texto UTF-8 puro
    assert DocumentLoader._detect_format_from_bytes("Documento oficial em Português / Español".encode("utf-8")) == "text"

    # Dados binários contendo bytes nulos (não deve ser detectado como texto plano)
    binary_data = b"\x00\x01\x02\x03\xff\xfe\x00\x55"
    assert DocumentLoader._detect_format_from_bytes(binary_data) == "unknown"

    # Bytes inválidos não-UTF-8
    invalid_utf8 = b"\x80\x81\x82\x83\x84\x85"
    assert DocumentLoader._detect_format_from_bytes(invalid_utf8) == "unknown"


def test_document_loader_file_not_found_and_unsupported_extension(tmp_path):
    loader = DocumentLoader()

    # Arquivo não existente
    with pytest.raises(FileNotFoundError, match="Arquivo não encontrado"):
        loader.load(tmp_path / "arquivo_inexistente.pdf")

    # Extensão não suportada
    unsupported = tmp_path / "planilha.xlsx"
    unsupported.write_text("dados", encoding="utf-8")
    with pytest.raises(ValueError, match="Extensão de documento não suportada"):
        loader.load(unsupported)

    # Tipo inválido
    with pytest.raises(TypeError, match="Tipo de fonte inválido"):
        loader.load(12345)


def test_document_loader_temp_file_cleanup_on_error():
    loader = DocumentLoader()
    pdf_bytes = b"%PDF-1.4 invalid content that causes parser error"

    # Mock _load_documents to raise an Exception and verify temp file is cleaned
    with patch.object(loader, "_load_documents", side_effect=RuntimeError("Simulated parse error")):
        with pytest.raises(RuntimeError, match="Simulated parse error"):
            loader.load(pdf_bytes)


# =============================================================================
# 3. Tests for ContentLoader (Unified Facade & Auto-Routing)
# =============================================================================

def test_content_loader_facade_routing(tmp_path):
    content_loader = ContentLoader(allowed_domains=["gov.br"])

    # 1. Carregamento DOCX via ContentLoader
    doc = docx.Document()
    doc.add_paragraph("Conteúdo de acolhimento aos imigrantes.")
    docx_file = tmp_path / "acolhimento.docx"
    doc.save(str(docx_file))

    result_docx = content_loader.load(docx_file)
    assert result_docx["source_type"] == "docx"
    assert "Conteúdo de acolhimento aos imigrantes." in result_docx["text"]

    # 2. Carregamento PDF via ContentLoader
    writer = pypdf.PdfWriter()
    writer.add_blank_page(width=100, height=100)
    pdf_file = tmp_path / "resolucao.pdf"
    with open(pdf_file, "wb") as f:
        writer.write(f)

    result_pdf = content_loader.load(pdf_file)
    assert result_pdf["source_type"] == "pdf"
    assert result_pdf["metadata"]["total_pages"] == 1

    # 3. Carregamento TXT via ContentLoader
    txt_file = tmp_path / "guia.md"
    txt_file.write_text("# Guia de Direitos\nDireito ao SUS e Educação.", encoding="utf-8")
    result_txt = content_loader.load(txt_file)
    assert result_txt["source_type"] == "text"
    assert "Direito ao SUS e Educação." in result_txt["text"]


def test_content_loader_remote_file_with_query_params():
    content_loader = ContentLoader(allowed_domains=["gov.br"])

    writer = pypdf.PdfWriter()
    writer.add_blank_page(width=100, height=100)
    pdf_io = io.BytesIO()
    writer.write(pdf_io)
    pdf_bytes = pdf_io.getvalue()

    with patch("requests.get") as mock_get:
        mock_resp = MagicMock()
        mock_resp.content = pdf_bytes
        mock_resp.raise_for_status = MagicMock()
        mock_get.return_value = mock_resp

        # URL com query parameter
        url = "https://www.gov.br/documento.pdf?version=2&download=true"
        result = content_loader.load(url)

        assert result["source_type"] == "pdf"
        assert result["url"] == url
        assert result["metadata"]["total_pages"] == 1


def test_content_loader_remote_file_unauthorized_domain():
    content_loader = ContentLoader(allowed_domains=["gov.br"])
    unauthorized_url = "https://malicious.com/documento.pdf"
    with pytest.raises(ValueError, match="não pertence à Whitelist"):
        content_loader.load(unauthorized_url)


# =============================================================================
# 4. Backward Compatibility Aliases & Module Imports
# =============================================================================

def test_backward_compatibility_aliases():
    # Confirma que os aliases legados funcionam como esperado
    assert PDFLoader is DocumentLoader
    assert DocxLoader is DocumentLoader
    assert WebLoader is WhitelistedWebLoader

    # Confirma que o módulo legado re-exporta todas as entidades
    assert legacy_loader_module.ContentLoader is ContentLoader
    assert legacy_loader_module.WhitelistedWebLoader is WhitelistedWebLoader
    assert legacy_loader_module.DocumentLoader is DocumentLoader
    assert legacy_loader_module.WebLoader is WebLoader
    assert legacy_loader_module.PDFLoader is PDFLoader
    assert legacy_loader_module.DocxLoader is DocxLoader
    assert legacy_loader_module.BaseDocumentLoader is BaseDocumentLoader
    assert legacy_loader_module.is_url_whitelisted is is_url_whitelisted
    assert legacy_loader_module.fetch_and_clean_page is fetch_and_clean_page

def test_web_loader_trafilatura_extraction_and_boilerplate_removal():
    sample_html = """
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <title>Orientações de Refúgio - CONARE</title>
    </head>
    <body>
        <div class="header-menu">
            <a href="/home">Início</a>
            <a href="/contato">Fale Conosco</a>
        </div>
        <div class="sidebar-ads">
            <p>Publicidade e Links Patrocinados</p>
        </div>
        <main>
            <article>
                <h1>Solicitação de Reconhecimento da Condição de Refugiado</h1>
                <p>O processo de solicitação de refúgio no Brasil é totalmente gratuito e deve ser realizado pelo sistema Sisconare.</p>
                <p>Durante a análise do pedido pelo CONARE, o solicitante tem direito a documento provisório de identificação e carteira de trabalho.</p>
            </article>
        </main>
        <div class="footer-copyright">
            <p>© 2026 Ministério da Justiça e Segurança Pública - Todos os direitos reservados.</p>
        </div>
    </body>
    </html>
    """
    loader = WhitelistedWebLoader(allowed_domains=["gov.br"])
    with patch("langchain_community.document_loaders.WebBaseLoader.scrape") as mock_scrape:
        mock_scrape.return_value = BeautifulSoup(sample_html, "html.parser")
        result = loader.load("https://www.gov.br/conare/refugio")

        assert result["source_type"] == "web"
        assert "Solicitação de Reconhecimento da Condição de Refugiado" in result["text"]
        assert "Sisconare" in result["text"]
        assert "Publicidade e Links Patrocinados" not in result["text"]
