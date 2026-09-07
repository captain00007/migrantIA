from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document


# =============================================================================
# 1. Base Document Splitter Interface
# =============================================================================

class BaseDocumentSplitter(ABC):
    """
    Interface abstrata base para divisores de texto e documentos do MigrantIA.
    """

    @abstractmethod
    def split_text(self, text: str, metadata: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Divide o texto puro em fragmentos enriquecidos com metadados contextuais.
        """
        pass

    @abstractmethod
    def split_documents(self, documents: List[Document]) -> List[Document]:
        """
        Divide uma lista de objetos Document do LangChain em fragmentos menores.
        """
        pass


# =============================================================================
# 2. Legal Document Splitter (Especializado em Textos Normativos e Governamentais)
# =============================================================================

class LegalDocumentSplitter(BaseDocumentSplitter):
    """
    Divisor de documentos especializado para a legislação brasileira, cartilhas,
    portarias e resoluções com foco em imigrantes e refugiados.
    
    Respeita hierarquias estruturais (Títulos, Artigos, Parágrafos §, Incisos e Seções Markdown).
    """

    DEFAULT_SEPARATORS: List[str] = [
        "\n\n### ",
        "\n\n## ",
        "\n\n# ",
        "\n\nArt. ",
        "\n\n§ ",
        "\n\n",
        "\n",
        ". ",
        " ",
        ""
    ]

    def __init__(
        self,
        chunk_size: int = 1000,
        chunk_overlap: int = 150,
        separators: Optional[List[str]] = None
    ):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.separators = separators or self.DEFAULT_SEPARATORS
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            separators=self.separators
        )

    def split_text(self, text: str, metadata: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Divide uma string de texto em pedaços (chunks) com metadados de paginação/ordenação.
        """
        if not text or not text.strip():
            return []

        chunks = self.splitter.split_text(text)
        base_meta = metadata or {}
        total = len(chunks)

        result = []
        for idx, chunk in enumerate(chunks):
            chunk_meta = dict(base_meta)
            chunk_meta['chunk_index'] = idx
            chunk_meta['total_chunks'] = total
            result.append({
                'content': chunk.strip(),
                'chunk_index': idx,
                'metadata': chunk_meta
            })
        return result

    def split_documents(self, documents: List[Document]) -> List[Document]:
        """
        Divide objetos Document do LangChain em fragmentos menores preservando e enriquecendo metadados.
        """
        if not documents:
            return []

        split_docs = self.splitter.split_documents(documents)
        for idx, doc in enumerate(split_docs):
            doc.metadata['chunk_index'] = idx
            doc.metadata['total_chunks'] = len(split_docs)
        return split_docs


# Alias principal para uso geral
DocumentSplitter = LegalDocumentSplitter


# =============================================================================
# 3. Funções de Conveniência e Retrocompatibilidade
# =============================================================================

def get_legal_text_splitter(chunk_size: int = 1000, chunk_overlap: int = 150) -> RecursiveCharacterTextSplitter:
    """
    Função utilitária legada: retorna a instância do RecursiveCharacterTextSplitter.
    """
    return LegalDocumentSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap).splitter


def split_document_text(text: str, metadata: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    """
    Função utilitária legada: divide o texto utilizando o LegalDocumentSplitter padrão.
    """
    splitter = LegalDocumentSplitter()
    return splitter.split_text(text, metadata=metadata)
