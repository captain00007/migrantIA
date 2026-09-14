from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document


# ===========================================================================
# 1. Base Document Splitter Interface
# ===========================================================================

class BaseDocumentSplitter(ABC):
    """
    Interface abstrata base para divisores de texto e documentos do MigrantIA.
    """

    @abstractmethod
    def split_text(
        self,
        text: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Divide o texto puro em fragmentos enriquecidos com metadatos contextuais.
        """
        pass

    @abstractmethod
    def split_documents(
        self,
        documents: List[Document]
    ) -> List[Document]:
        """
        Divide uma lista de objetos Document do LangChain em fragmentos menores.
        """
        pass


# ===========================================================================
# 2. Document Splitter
# ===========================================================================

class DocumentSplitter(BaseDocumentSplitter):
    """
    Divisor de documentos especializado para a legislacao brasileira, cartilhas,
    portarias e resolucoes com foco em imigrantes e refugiados.
    
    Respeita hierarquias estruturais (Titulos, Artigos, Paragrafos §, Incisos e Secoes Markdown).
    """

    DEFAULT_CHUNK_SIZE: int = 1000
    DEFAULT_CHUNK_OVERLAP: int = 150
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
        chunk_size: int = DEFAULT_CHUNK_SIZE,
        chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
        separators: Optional[List[str]] = None
    ):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.separators = separators or self.DEFAULT_SEPARATORS
        self._splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            separators=self.separators
        )

    @property
    def splitter(self) -> RecursiveCharacterTextSplitter:
        """Retorna a instancia subjacente do RecursiveCharacterTextSplitter."""
        return self._splitter

    def split_text(
        self,
        text: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Divide uma string de texto em pedacos (chunks) com metadatos de paginacao/ordenacao.
        """
        if not text or not text.strip():
            return []

        chunks = self.splitter.split_text(text)
        base_meta = metadata or {}
        total = len(chunks)

        result = []
        for idx, chunk in enumerate(chunks):
            chunk_meta = dict(base_meta)
            chunk_meta["chunk_index"] = idx
            chunk_meta["total_chunks"] = total
            result.append({
                "content": chunk.strip(),
                "chunk_index": idx,
                "metadata": chunk_meta
            })
        return result

    def split_documents(
        self,
        documents: List[Document]
    ) -> List[Document]:
        """
        Divide objetos Document do LangChain em fragmentos menores preservando e enriquecendo metadatos.
        """
        if not documents:
            return []

        result_docs: List[Document] = []
        for doc in documents:
            chunks = self.splitter.split_documents([doc])
            total = len(chunks)
            for idx, chunk in enumerate(chunks):
                chunk.metadata["chunk_index"] = idx
                chunk.metadata["total_chunks"] = total
                result_docs.append(chunk)
        return result_docs