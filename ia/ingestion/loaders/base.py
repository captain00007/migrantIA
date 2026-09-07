"""
Módulo base para contratos e tipos compartilhados dos loaders do MigrantIA.
"""

import io
import os
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, Union

# Define USER_AGENT padrão no ambiente para suprimir avisos do LangChain
DEFAULT_USER_AGENT = os.getenv(
    "USER_AGENT",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36 (compatible; MigrantIABot/1.0; +https://migrantia.com; contato@migrantia.com)"
)
os.environ.setdefault("USER_AGENT", DEFAULT_USER_AGENT)

# Tipo unificado para representar fontes de dados aceitas pelos loaders
DocumentSource = Union[str, Path, bytes, io.BytesIO]


class BaseDocumentLoader(ABC):
    """
    Interface abstrata base para carregadores de documentos do MigrantIA.
    """

    @abstractmethod
    def load(
        self,
        source: DocumentSource,
        **kwargs: Any
    ) -> Dict[str, Any]:
        """
        Carrega e normaliza o documento da fonte informada, retornando um dicionário padronizado:
        {
            'title': str,
            'text': str,
            'source_type': str,  # 'web', 'pdf', 'docx', 'text'
            'url': Optional[str],
            'metadata': Dict[str, Any],
            'documents': List[Document]
        }
        """
        pass
