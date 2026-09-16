"""
Módulo de Armazenamento de Documentos do MigrantIA.
Gerencia o armazenamento unificado do arquivo original (upload) e do conteúdo limpo
em uma pasta única indexada pelo hash SHA-256 do documento (media/documents/<hash>/).
"""
import io
import os
import shutil
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
from django.conf import settings
from langchain_core.documents import Document

logger = logging.getLogger(__name__)


def get_documents_storage_dir() -> Path:
    """Retorna o diretório base de armazenamento de documentos."""
    storage_dir = getattr(settings, "DOCUMENTS_STORAGE_DIR", None)
    if not storage_dir:
        media_root = getattr(settings, "MEDIA_ROOT", Path(settings.BASE_DIR) / "media")
        storage_dir = Path(media_root) / "documents"
    else:
        storage_dir = Path(storage_dir)

    storage_dir.mkdir(parents=True, exist_ok=True)
    return storage_dir


def save_document_bundle(
    content_hash: str,
    cleaned_docs: List[Document],
    source_file: Optional[Union[str, Path, bytes, io.BytesIO]] = None,
    original_filename: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Salva o arquivo original e o texto limpo dentro do diretório único do hash:
    media/documents/<content_hash>/
      ├── <original_filename>  (ex: portaria_mjsp.pdf)
      └── cleaned.md           (texto limpo com metadados)

    Retorna um dicionário com os caminhos dos arquivos gravados.
    """
    if not content_hash:
        raise ValueError("content_hash é obrigatório para salvar o pacote de documentos.")

    base_storage = get_documents_storage_dir()
    bundle_dir = base_storage / content_hash
    bundle_dir.mkdir(parents=True, exist_ok=True)

    result_paths = {
        "bundle_dir": str(bundle_dir),
        "raw_file_path": None,
        "cleaned_file_path": None,
    }

    # 1. Salvar o arquivo original (raw)
    if source_file is not None:
        filename = original_filename or "document_original"
        dest_raw_path = bundle_dir / filename

        try:
            if isinstance(source_file, (str, Path)):
                source_path = Path(source_file)
                if source_path.exists() and source_path.resolve() != dest_raw_path.resolve():
                    shutil.copy2(source_path, dest_raw_path)
            elif isinstance(source_file, bytes):
                dest_raw_path.write_bytes(source_file)
            elif isinstance(source_file, io.BytesIO):
                dest_raw_path.write_bytes(source_file.getvalue())

            if dest_raw_path.exists():
                result_paths["raw_file_path"] = str(dest_raw_path)
                logger.info(f"Arquivo original salvo em: {dest_raw_path}")
        except Exception as e:
            logger.warning(f"Erro ao salvar arquivo original no bundle {content_hash}: {e}")

    # 2. Salvar o conteúdo limpo (cleaned.md)
    if cleaned_docs:
        cleaned_file_path = bundle_dir / "cleaned.md"
        try:
            header = [
                f"# Conteúdo Normalizado (Hash: {content_hash})",
                f"Total de Fragmentos/Páginas: {len(cleaned_docs)}",
                "=" * 60,
                "",
            ]
            content_blocks = []
            for i, doc in enumerate(cleaned_docs, 1):
                page_info = f" [Página {doc.metadata.get('page', i)}]" if "page" in doc.metadata else ""
                content_blocks.append(
                    f"<!-- Início do Bloco {i}{page_info} -->\n{doc.page_content}\n<!-- Fim do Bloco {i} -->"
                )

            full_cleaned_text = "\n".join(header) + "\n\n".join(content_blocks)
            cleaned_file_path.write_text(full_cleaned_text, encoding="utf-8")

            result_paths["cleaned_file_path"] = str(cleaned_file_path)
            logger.info(f"Texto limpo salvo em: {cleaned_file_path}")
        except Exception as e:
            logger.warning(f"Erro ao salvar texto limpo no bundle {content_hash}: {e}")

    return result_paths
