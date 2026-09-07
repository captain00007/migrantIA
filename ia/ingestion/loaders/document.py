"""
Módulo responsável exclusivamente pela ingestão e normalização de arquivos/documentos.
"""

import contextlib
import io
import struct
import tempfile
import zipfile
import zlib
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Generator, List, Optional, Tuple, Type, Union

from langchain_community.document_loaders import (
    Docx2txtLoader,
    PyPDFLoader,
    TextLoader,
)
from langchain_community.document_loaders.base import BaseLoader
from langchain_core.documents import Document

from ia.ingestion.loaders.base import BaseDocumentLoader, DocumentSource

# Mapeamento declarativo de extensões para classes de loaders e tipos de fonte
_LOADERS: Dict[str, Tuple[Type[BaseLoader], str]] = {
    ".pdf": (PyPDFLoader, "pdf"),
    ".docx": (Docx2txtLoader, "docx"),
    ".doc": (Docx2txtLoader, "docx"),
    ".txt": (TextLoader, "text"),
    ".md": (TextLoader, "text"),
    ".markdown": (TextLoader, "text"),
    ".csv": (TextLoader, "text"),
    ".json": (TextLoader, "text"),
    ".html": (TextLoader, "text"),
    ".htm": (TextLoader, "text"),
}


def _resolve_loader_info(extension: str) -> Tuple[Type[BaseLoader], str]:
    """Resolve a classe do loader e o source_type a partir da extensão do arquivo."""
    ext = extension.lower().strip()
    if not ext.startswith("."):
        ext = f".{ext}"

    if ext in _LOADERS:
        return _LOADERS[ext]

    supported = ", ".join(sorted(_LOADERS.keys()))
    raise ValueError(
        f"Extensão de documento não suportada: '{ext}'. Extensões aceitas: {supported}"
    )


@dataclass(frozen=True)
class PreparedSource:
    """Estrutura imutável contendo as informações preparadas para execução do loader."""
    target_path: str
    extension: str
    title: str


class DocumentLoader(BaseDocumentLoader):
    """
    Carregador unificado de arquivos de documentos (PDF, DOCX, TXT, MD, CSV, JSON, HTML)
    utilizando loaders especializados da comunidade LangChain:
    - PyPDFLoader para .pdf
    - Docx2txtLoader para .docx / .doc
    - TextLoader para .txt, .md, .csv, .json, .html

    Agnóstico quanto ao tipo de entrada: aceita caminhos no disco (str, Path),
    ou fluxos de bytes em memória (bytes, io.BytesIO) com auto-detecção de formato.
    """

    @staticmethod
    def _is_docx_bytes(data: bytes) -> bool:
        """
        Verifica se os bytes correspondem a uma estrutura OOXML/DOCX válida.
        Inspeciona os metadados do pacote ZIP sem utilizar blocos pass em exceções.
        """
        try:
            with zipfile.ZipFile(io.BytesIO(data)) as zf:
                names = set(zf.namelist())
                if "word/document.xml" in names or any(n.startswith("word/") for n in names):
                    return True
                if "[Content_Types].xml" in names:
                    content_types = zf.read("[Content_Types].xml")
                    return b"wordprocessingml" in content_types or b"document" in content_types
        except (zipfile.BadZipFile, KeyError, zlib.error, struct.error, EOFError):
            return False

        return False

    @staticmethod
    def _is_utf8_text_bytes(data: bytes) -> bool:
        """
        Verifica se a amostra de bytes é decodificável em UTF-8 e não possui caracteres nulos binários.
        """
        if not data:
            return False
        sample = data[:4096]
        if b"\x00" in sample:
            return False
        try:
            sample.decode("utf-8")
            return True
        except UnicodeDecodeError:
            return False

    @classmethod
    def _detect_format_from_bytes(cls, data: bytes) -> str:
        """
        Identifica com segurança o formato do documento a partir dos bytes.
        Diferencia contêineres ZIP genéricos de arquivos DOCX/OOXML reais.
        """
        if data.startswith(b"%PDF"):
            return "pdf"

        # Pacotes com cabeçalho ZIP: valida se é DOCX real ou container genérico/desconhecido
        if data.startswith(b"PK\x03\x04"):
            return "docx" if cls._is_docx_bytes(data) else "unknown"

        if cls._is_utf8_text_bytes(data):
            return "text"

        return "unknown"

    def _prepare_file_source(
        self,
        path: Union[str, Path],
        file_type: Optional[str],
        custom_title: Optional[str]
    ) -> PreparedSource:
        """Prepara e valida fontes baseadas em arquivos no disco."""
        file_path = Path(path)
        if not file_path.exists():
            raise FileNotFoundError(f"Arquivo não encontrado: {file_path}")

        ext = f".{file_type.lstrip('.').lower()}" if file_type else file_path.suffix.lower()
        title = custom_title or file_path.stem.replace("_", " ").replace("-", " ").title()
        return PreparedSource(target_path=str(file_path), extension=ext, title=title)

    @contextmanager
    def _open_memory_source(
        self,
        source: Union[bytes, io.BytesIO],
        file_type: Optional[str],
        custom_title: Optional[str]
    ) -> Generator[PreparedSource, None, None]:
        """
        Prepara buffers em memória (bytes/io.BytesIO):
        - Detecta o formato quando não informado explicitamente.
        - Cria um arquivo temporário no disco para os loaders do LangChain.
        - Garante a limpeza segura do arquivo temporário no descarte do contexto.
        """
        content_bytes = source.getvalue() if isinstance(source, io.BytesIO) else source

        if file_type:
            ext = f".{file_type.lstrip('.').lower()}"
        else:
            detected_format = self._detect_format_from_bytes(content_bytes)
            if detected_format == "unknown":
                raise ValueError(
                    "Não foi possível identificar com segurança o formato do arquivo a partir dos bytes fornecidos. "
                    "Forneça o parâmetro 'file_type' explicitamente."
                )
            ext = f".{detected_format}"

        title = custom_title or f"Documento {ext.upper().replace('.', '')}"

        with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as tmp:
            tmp.write(content_bytes)
            temp_file_path = tmp.name

        try:
            yield PreparedSource(target_path=temp_file_path, extension=ext, title=title)
        finally:
            with contextlib.suppress(OSError):
                Path(temp_file_path).unlink(missing_ok=True)

    @contextmanager
    def _open_source(
        self,
        source: DocumentSource,
        file_type: Optional[str] = None,
        custom_title: Optional[str] = None
    ) -> Generator[PreparedSource, None, None]:
        """
        Roteia e gerencia o ciclo de vida da fonte de documento (disco ou memória).
        """
        if isinstance(source, (str, Path)):
            yield self._prepare_file_source(source, file_type, custom_title)
        elif isinstance(source, (bytes, io.BytesIO)):
            with self._open_memory_source(source, file_type, custom_title) as prep:
                yield prep
        else:
            raise TypeError(
                f"Tipo de fonte inválido para DocumentLoader: {type(source)}. "
                f"Esperado: str, Path, bytes ou io.BytesIO."
            )

    def _load_documents(
        self,
        target_path: str,
        loader_cls: Type[BaseLoader],
        encoding: str
    ) -> List[Document]:
        """Executa a leitura e extração dos objetos Document do LangChain."""
        if loader_cls is TextLoader:
            loader = loader_cls(target_path, encoding=encoding)
        else:
            loader = loader_cls(target_path)
        return loader.load()

    def _build_result(
        self,
        docs: List[Document],
        source: DocumentSource,
        source_type: str,
        title: str,
        url: Optional[str]
    ) -> Dict[str, Any]:
        """Normaliza e agrega os documentos extraídos e seus metadados."""
        page_contents = [d.page_content for d in docs if d.page_content]
        full_text = "\n\n".join(page_contents).strip()

        metadata: Dict[str, Any] = {
            "source_type": source_type,
            "total_documents": len(docs),
            "content_length": len(full_text),
            "source_path": str(source) if isinstance(source, (str, Path)) else None,
            "url": url,
        }

        if docs:
            metadata.update({k: v for k, v in docs[0].metadata.items() if k not in metadata})

        if source_type == "pdf":
            metadata["total_pages"] = len(docs)

        return {
            "title": title,
            "text": full_text,
            "source_type": source_type,
            "url": url,
            "metadata": metadata,
            "documents": docs,
        }

    def load(
        self,
        source: DocumentSource,
        file_type: Optional[str] = None,
        *,
        title: Optional[str] = None,
        url: Optional[str] = None,
        encoding: str = "utf-8",
        **kwargs: Any
    ) -> Dict[str, Any]:
        """
        Carrega qualquer tipo de documento de forma unificada e transparente.
        """
        with self._open_source(source, file_type=file_type, custom_title=title) as prep:
            loader_cls, source_type = _resolve_loader_info(prep.extension)
            docs = self._load_documents(prep.target_path, loader_cls, encoding=encoding)
            return self._build_result(docs, source, source_type, prep.title, url)


# Aliases para retrocompatibilidade
PDFLoader = DocumentLoader
DocxLoader = DocumentLoader
