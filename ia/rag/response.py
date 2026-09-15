"""
Modelos de dados de resposta do Pipeline RAG do MigrantIA.
"""
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class RAGSource(BaseModel):
    """Representação estruturada de uma fonte oficial citada."""
    title: str = ""
    url: str = ""
    snippet: str = ""
    source_type: str = "LOCAL"  # LOCAL, WEB, PARTNER
    pillar: Optional[str] = None
    page: Optional[int] = None
    pages: List[int] = Field(default_factory=list)


class RAGResponse(BaseModel):
    """Resposta final estruturada do pipeline RMG do MigrantIA."""
    content: str
    sources: List[RAGSource] = Field(default_factory=list)
    language_detected: str = "pt"
    golden_rule_triggered: bool = False
    metadata: Dict[str, Any] = Field(default_factory=dict)
