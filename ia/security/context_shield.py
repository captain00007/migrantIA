"""
Módulo de Isolamento Estrutural e Anti-RAG Poisoning (ContextShield).
Sanitiza fragmentos recuperados e os encapsula em blocos XML com tags CDATA,
estabelecendo uma fronteira rígida e determinística entre DADOS e INSTRUÇÕES.
"""
import re
from typing import List, Dict, Any
from langchain_core.documents import Document

# Marcadores de diálogo e instruções que podem ser usados em ataques de Injeção Indireta
INDIRECT_INJECTION_MARKERS = [
    r"\[(?:SYSTEM|INSTRUCTION|PROMPT|OVERRIDE|ADMIN)[^\]]*\]",
    r"^(?:System|Assistant|Human|User):\s*",
    r"---+\s*(?:Fonte|Contexto|Fim|Inicio)",
    r"===+\s*(?:Contexto|Oficial|Instrucoes)",
]
COMPILED_INDIRECT_INJECTION_REGEX = re.compile(
    "|".join(INDIRECT_INJECTION_MARKERS),
    re.IGNORECASE | re.MULTILINE
)


class ContextShield:
    """Escudo de contexto oficial contra RAG Poisoning e Indirect Prompt Injection."""

    @classmethod
    def sanitize_chunk_content(cls, content: str) -> str:
        """Remove marcadores de simulação de prompt e comandos de injeção indireta dentro do documento."""
        if not content:
            return ""
        # 1. Remove marcadores de simulação de sistema
        cleaned = COMPILED_INDIRECT_INJECTION_REGEX.sub("", content)
        # 2. Remove tags Markdown de imagens
        cleaned = re.sub(r"!\[(.*?)\]\([^)]+\)", r"[\1]", cleaned)
        # 3. Escape de tags de encerramento CDATA acidentais
        cleaned = cleaned.replace("]]>", "]]&gt;")
        return cleaned.strip()

    @classmethod
    def build_isolated_context(
        cls,
        local_docs: List[Document],
        web_results: List[Dict[str, Any]]
    ) -> str:
        """
        Gera uma estrutura XML estrita com blocos CDATA para isolar os dados passivos do contexto.
        """
        if not local_docs and not web_results:
            return "<official_knowledge_base status=\"empty\">(Nenhum documento oficial específico anexado para esta mensagem)</official_knowledge_base>"

        doc_elements: List[str] = []

        # Chunks locais
        for i, doc in enumerate(local_docs, 1):
            doc_id = f"local_doc_{i}"
            title = doc.metadata.get("title", f"Documento Local {i}")
            url = doc.metadata.get("url", "")
            page = doc.metadata.get("page")
            page_label = doc.metadata.get("page_label")
            pillar = doc.metadata.get("pillar", "")

            page_attr = f' page="{page_label or (page + 1 if isinstance(page, int) else page)}"' if (page is not None or page_label is not None) else ""
            url_attr = f' url="{url}"' if url else ""
            pillar_attr = f' pillar="{pillar}"' if pillar else ""

            safe_content = cls.sanitize_chunk_content(doc.page_content)
            doc_elements.append(
                f'  <document id="{doc_id}" source="LOCAL" title="{title}"{page_attr}{url_attr}{pillar_attr}>\n'
                f'    <![CDATA[\n{safe_content}\n    ]]>\n'
                f'  </document>'
            )

        # Chunks da Web Homologada
        for j, res in enumerate(web_results, 1):
            doc_id = f"web_doc_{j}"
            title = res.get("title", f"Fonte Web {j}")
            url = res.get("url", "")
            safe_content = cls.sanitize_chunk_content(res.get("content", ""))

            doc_elements.append(
                f'  <document id="{doc_id}" source="WEB_OFFICIAL" title="{title}" url="{url}">\n'
                f'    <![CDATA[\n{safe_content}\n    ]]>\n'
                f'  </document>'
            )

        xml_body = "\n".join(doc_elements)
        return (
            f"<official_knowledge_base count=\"{len(local_docs) + len(web_results)}\">\n"
            f"{xml_body}\n"
            f"</official_knowledge_base>"
        )

    @classmethod
    def format_user_query(cls, query: str) -> str:
        """Encapsula a pergunta do usuário em tag XML CDATA segura."""
        safe_query = query.replace("]]>", "]]&gt;").strip()
        return f"<user_query>\n  <![CDATA[\n{safe_query}\n  ]]>\n</user_query>"
