"""
Módulo de Limpeza e Normalização de Textos e Documentos para o MigrantIA.

Este módulo é executado imediatamente APÓS o carregamento (Loaders) e ANTES
do particionamento em chunks (DocumentSplitter).

Responsabilidades:
1. Normalização Unicode (NFKC, remoção de caracteres invisíveis e soft hyphens).
2. Remoção de ruídos de OCR, números de páginas e cabeçalhos repetitivos de PDFs.
3. Decodificação de entidades HTML e remoção de tags residuais.
4. Correção de hifenação em quebras de linha de PDFs/documentos digitalizados.
5. Padronização de citações legislativas e normativas (Art., §, Incisos).
6. Limpeza e consolidação de quebras de linha e espaços em branco.
"""

import html
import re
import unicodedata
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union

from langchain_core.documents import Document


# =============================================================================
# 1. Base Cleaner Interface
# =============================================================================

class BaseCleaner(ABC):
    """
    Interface abstrata base para limpadores e normalizadores de conteúdo do MigrantIA.
    """

    @abstractmethod
    def clean(self, text: str) -> str:
        """Limpa e normaliza uma string de texto."""
        pass

    @abstractmethod
    def clean_document(self, document: Document) -> Document:
        """Limpa e normaliza um objeto Document do LangChain."""
        pass

    @abstractmethod
    def clean_documents(self, documents: List[Document]) -> List[Document]:
        """Limpa e normaliza uma lista de objetos Document do LangChain."""
        pass

    @abstractmethod
    def clean_loaded_result(self, loaded_result: Dict[str, Any]) -> Dict[str, Any]:
        """Limpa o dicionário estruturado retornado pelos Loaders."""
        pass


# =============================================================================
# 2. Text Cleaner (Implementação Canônica)
# =============================================================================

class TextCleaner(BaseCleaner):
    """
    Limpador e normalizador de textos e documentos do MigrantIA.
    Executado no pipeline após a etapa de Load (PDF, DOCX, Web, TXT).
    """

    # Expressões regulares pré-compiladas para alta performance
    RE_ZERO_WIDTH = re.compile(r"[\u200B-\u200D\uFEFF\u00AD\u2060]")
    RE_CONTROL_CHARS = re.compile(r"[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]")
    RE_HTML_TAGS = re.compile(r"<[^>]+>")
    RE_PAGE_NUMBERS = re.compile(
        r"(?i)(?:p[aá]gina|p[aá]g\.?|page)\s+\d+(?:\s*(?:de|/|of)\s*\d+)?\b"
    )
    RE_HYPHENATED_LINEBREAK = re.compile(r"(\b[a-zA-ZÀ-ÿ]+)-\s*\n\s*([a-zA-ZÀ-ÿ]+\b)")
    RE_MULTIPLE_SPACES = re.compile(r"[^\S\n\r]+")
    RE_TRAILING_WHITESPACE = re.compile(r"[ \t]+$", re.MULTILINE)
    RE_MULTIPLE_NEWLINES = re.compile(r"\n{3,}")

    # Padrões para normalização legislativa brasileira
    RE_LEGAL_ART = re.compile(r"(?i)\b(?:artigo|art)\.?\s*(\d+)\s*(?:[ºo°ª]|\b)", re.IGNORECASE)
    RE_LEGAL_PARAGRAPH = re.compile(r"(?i)(?:par[aá]grafo|§)\s*(?:[úu]nico|unico)\b", re.IGNORECASE)
    RE_LEGAL_PARAGRAPH_NUM = re.compile(r"(?i)(?:par[aá]grafo|§)\s*(\d+)\s*(?:[ºo°ª]|\b)", re.IGNORECASE)

    def __init__(
        self,
        normalize_unicode: bool = True,
        remove_control_chars: bool = True,
        decode_html_entities: bool = True,
        remove_html_tags: bool = True,
        fix_hyphenation: bool = True,
        remove_page_numbers: bool = True,
        normalize_legal_citations: bool = True,
        clean_whitespace: bool = True,
        max_consecutive_newlines: int = 2,
    ) -> None:
        self.normalize_unicode = normalize_unicode
        self.remove_control_chars = remove_control_chars
        self.decode_html_entities = decode_html_entities
        self.remove_html_tags = remove_html_tags
        self.fix_hyphenation = fix_hyphenation
        self.remove_page_numbers = remove_page_numbers
        self.normalize_legal_citations = normalize_legal_citations
        self.clean_whitespace = clean_whitespace
        self.max_consecutive_newlines = max_consecutive_newlines

    def clean(self, text: str) -> str:
        """
        Executa a sequência completa de limpeza e normalização sobre uma string de texto.
        """
        if not text:
            return ""

        cleaned = str(text)

        # 1. Normalização Unicode (NFKC) e remoção de caracteres invisíveis
        if self.normalize_unicode:
            cleaned = unicodedata.normalize("NFKC", cleaned)
            cleaned = self.RE_ZERO_WIDTH.sub("", cleaned)
            # Substitui non-breaking spaces por espaço comum
            cleaned = cleaned.replace("\u00A0", " ").replace("\u202F", " ")

        # 2. Remoção de caracteres de controle binários
        if self.remove_control_chars:
            cleaned = self.RE_CONTROL_CHARS.sub("", cleaned)

        # 3. Decodificação de entidades HTML e remoção de tags soltas
        if self.decode_html_entities:
            cleaned = html.unescape(cleaned)
        if self.remove_html_tags:
            cleaned = self.RE_HTML_TAGS.sub("", cleaned)

        # 4. Correção de quebra de palavras por hifenação em fim de linha (comum em PDFs)
        if self.fix_hyphenation:
            cleaned = self.RE_HYPHENATED_LINEBREAK.sub(r"\1\2", cleaned)

        # 5. Remoção de numeração de páginas isoladas ("Página 1 de 10")
        if self.remove_page_numbers:
            cleaned = self.RE_PAGE_NUMBERS.sub("", cleaned)

        # 6. Normalização legislativa brasileira (Artigos e Parágrafos)
        if self.normalize_legal_citations:
            cleaned = self.RE_LEGAL_ART.sub(r"Art. \1º", cleaned)
            cleaned = self.RE_LEGAL_PARAGRAPH.sub("Parágrafo único", cleaned)
            cleaned = self.RE_LEGAL_PARAGRAPH_NUM.sub(r"§ \1º", cleaned)

        # 7. Limpeza e consolidação de espaçamentos e quebras de linha
        if self.clean_whitespace:
            # Converte carriage return para quebra padrão
            cleaned = cleaned.replace("\r\n", "\n").replace("\r", "\n")
            # Remove múltiplos espaços horizontais (mantém newlines)
            cleaned = self.RE_MULTIPLE_SPACES.sub(" ", cleaned)
            # Remove espaços no fim de cada linha
            cleaned = self.RE_TRAILING_WHITESPACE.sub("", cleaned)
            # Limita quebras de linha consecutivas
            target_newlines = "\n" * max(1, self.max_consecutive_newlines)
            cleaned = self.RE_MULTIPLE_NEWLINES.sub(target_newlines, cleaned)

        return cleaned.strip()

    def clean_document(self, document: Document) -> Document:
        """
        Limpa o conteúdo de um Document do LangChain, preservando e atualizando seus metadados.
        """
        cleaned_content = self.clean(document.page_content)
        new_metadata = dict(document.metadata)
        new_metadata["content_length"] = len(cleaned_content)
        new_metadata["is_cleaned"] = True
        return Document(page_content=cleaned_content, metadata=new_metadata)

    def clean_documents(self, documents: List[Document]) -> List[Document]:
        """
        Limpa uma lista de objetos Document, descartando fragmentos que resultarem vazios após a limpeza.
        """
        if not documents:
            return []

        cleaned_docs: List[Document] = []
        for doc in documents:
            cleaned_doc = self.clean_document(doc)
            if cleaned_doc.page_content.strip():
                cleaned_docs.append(cleaned_doc)
        return cleaned_docs

    def clean_loaded_result(self, loaded_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Limpa o resultado de carregamento retornado pelos Loaders (DocumentLoader, WebLoader, etc.).
        Garante sincronização entre o texto unificado e os objetos Document internos.
        """
        if not loaded_result:
            return {}

        result = dict(loaded_result)

        # 1. Limpa o texto agregado
        if "text" in result:
            result["text"] = self.clean(result.get("text", ""))

        # 2. Limpa o título se presente
        if "title" in result and isinstance(result["title"], str):
            result["title"] = self.clean(result["title"])

        # 3. Limpa a lista de Documents encapsulados
        if "documents" in result and isinstance(result["documents"], list):
            result["documents"] = self.clean_documents(result["documents"])

        # 4. Atualiza metadados
        meta = dict(result.get("metadata", {}))
        meta["content_length"] = len(result.get("text", ""))
        meta["is_cleaned"] = True
        if "documents" in result:
            meta["total_documents"] = len(result["documents"])
        result["metadata"] = meta

        return result

    # -------------------------------------------------------------------------
    # Métodos de Classe para Execução Direta
    # -------------------------------------------------------------------------

    @classmethod
    def clean_text(cls, text: str, **kwargs: Any) -> str:
        """Método de classe utilitário para limpar texto diretamente sem instanciar."""
        cleaner = cls(**kwargs)
        return cleaner.clean(text)

    @classmethod
    def clean_result(cls, loaded_result: Dict[str, Any], **kwargs: Any) -> Dict[str, Any]:
        """Método de classe utilitário para limpar o resultado do loader diretamente."""
        cleaner = cls(**kwargs)
        return cleaner.clean_loaded_result(loaded_result)

    @classmethod
    def clean_docs(cls, documents: List[Document], **kwargs: Any) -> List[Document]:
        """Método de classe utilitário para limpar documentos LangChain diretamente."""
        cleaner = cls(**kwargs)
        return cleaner.clean_documents(documents)
