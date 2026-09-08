import pytest
from langchain_core.documents import Document

from ia.ingestion.cleaners import BaseCleaner, TextCleaner


def test_unicode_and_invisible_characters():
    cleaner = TextCleaner()
    # Texto com caracteres invisíveis (zero-width, soft-hyphen, non-breaking space)
    raw = "Acolhida\u200b humanit\u00e1ria\u00ad para\u00a0refugiados\ufeff."
    cleaned = cleaner.clean(raw)
    assert cleaned == "Acolhida humanitária para refugiados."


def test_html_entities_and_tags_removal():
    cleaner = TextCleaner()
    raw = "<p>Direitos &amp; Deveres dos <b>Migrantes</b> &quot;Lei 13.445&quot;</p>"
    cleaned = cleaner.clean(raw)
    assert cleaned == 'Direitos & Deveres dos Migrantes "Lei 13.445"'


def test_hyphenation_linebreak_repair():
    cleaner = TextCleaner()
    # Hifenação típica de final de linha em páginas de PDF
    raw = "A política inter-\n nacional garante o acolhi-\n   mento dos cidadãos."
    cleaned = cleaner.clean(raw)
    assert "internacional" in cleaned
    assert "acolhimento" in cleaned


def test_page_number_removal():
    cleaner = TextCleaner()
    raw = "Informações sobre CPF.\n\nPágina 1 de 15\n\nDocumentos necessários:\n1. Passaporte"
    cleaned = cleaner.clean(raw)
    assert "Página 1 de 15" not in cleaned
    assert "Informações sobre CPF." in cleaned
    assert "Documentos necessários:" in cleaned


def test_legal_citations_normalization():
    cleaner = TextCleaner()
    raw = "Artigo 1o O visto será concedido. Art 2º Conforme parágrafo 1o e § unico."
    cleaned = cleaner.clean(raw)
    assert "Art. 1º" in cleaned
    assert "Art. 2º" in cleaned
    assert "§ 1º" in cleaned
    assert "Parágrafo único" in cleaned


def test_whitespace_and_newlines_condensing():
    cleaner = TextCleaner(max_consecutive_newlines=2)
    raw = "Texto     com    muitos      espaços.\n\n\n\n\nNova seção.   \t"
    cleaned = cleaner.clean(raw)
    assert cleaned == "Texto com muitos espaços.\n\nNova seção."


def test_clean_document():
    cleaner = TextCleaner()
    doc = Document(
        page_content="  Artigo 5o   Direito &amp; Acesso  \n\n\n\n",
        metadata={"source": "lei.pdf", "author": "MJSP"}
    )
    cleaned_doc = cleaner.clean_document(doc)

    assert cleaned_doc.page_content == "Art. 5º Direito & Acesso"
    assert cleaned_doc.metadata["source"] == "lei.pdf"
    assert cleaned_doc.metadata["author"] == "MJSP"
    assert cleaned_doc.metadata["is_cleaned"] is True
    assert cleaned_doc.metadata["content_length"] == len(cleaned_doc.page_content)


def test_clean_documents_filters_empty():
    cleaner = TextCleaner()
    docs = [
        Document(page_content="   \u200b   ", metadata={"id": 1}),
        Document(page_content="Conteúdo relevante.", metadata={"id": 2}),
    ]
    cleaned_list = cleaner.clean_documents(docs)
    assert len(cleaned_list) == 1
    assert cleaned_list[0].metadata["id"] == 2
    assert cleaned_list[0].page_content == "Conteúdo relevante."


def test_clean_loaded_result():
    cleaner = TextCleaner()
    loaded_result = {
        "title": "  <b>Cartilha de Direitos</b>  ",
        "text": "Artigo 1o   Regularização   &amp; Acolhimento.\n\nPág. 2/10\n\nTexto final.",
        "source_type": "pdf",
        "url": "https://gov.br/cartilha.pdf",
        "metadata": {"source_path": "/tmp/cartilha.pdf"},
        "documents": [
            Document(page_content="Artigo 1o Regularização &amp; Acolhimento.", metadata={"page": 1}),
            Document(page_content="Pág. 2/10\nTexto final.", metadata={"page": 2})
        ]
    }

    cleaned_result = cleaner.clean_loaded_result(loaded_result)

    assert cleaned_result["title"] == "Cartilha de Direitos"
    assert "Art. 1º Regularização & Acolhimento." in cleaned_result["text"]
    assert "Pág. 2/10" not in cleaned_result["text"]
    assert cleaned_result["metadata"]["is_cleaned"] is True
    assert cleaned_result["metadata"]["content_length"] == len(cleaned_result["text"])
    assert len(cleaned_result["documents"]) == 2
    assert cleaned_result["documents"][0].metadata["is_cleaned"] is True


def test_cleaner_class_methods():
    text_cleaned = TextCleaner.clean_text("  Texto   &amp; Teste  ")
    assert text_cleaned == "Texto & Teste"

    doc_cleaned = TextCleaner.clean_docs([Document(page_content="  Artigo 1o  ", metadata={})])
    assert doc_cleaned[0].page_content == "Art. 1º"

    result_cleaned = TextCleaner.clean_result({"text": "  Olá   Mundo  ", "metadata": {}})
    assert result_cleaned["text"] == "Olá Mundo"
    assert result_cleaned["metadata"]["is_cleaned"] is True


def test_empty_input():
    cleaner = TextCleaner()
    assert cleaner.clean("") == ""
    assert cleaner.clean_documents([]) == []
    assert cleaner.clean_loaded_result({}) == {}
