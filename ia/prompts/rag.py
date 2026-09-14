"""
Templates de Prompts para o Pipeline RAG do MigrantIA.
"""
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from ia.prompts.system import MIGRANTIA_SYSTEM_PROMPT

RAG_USER_PROMPT_TEMPLATE = """=== CONTEXTO OFICIAL AUDITADO ===
{context}

=== PERGUNTA DO USUÁRIO ===
{question}

Instruções finais:
- Responda no mesmo idioma da pergunta.
- Baseie-se estritamente no contexto oficial acima.
- Se o contexto não responder com segurança, aplique a Regra de Ouro (não invente e recomende as ONGs/Defensorias).
"""


def get_rag_prompt_template() -> ChatPromptTemplate:
    """Retorna o ChatPromptTemplate configurado para a chain de RAG."""
    return ChatPromptTemplate.from_messages([
        ("system", MIGRANTIA_SYSTEM_PROMPT),
        MessagesPlaceholder(variable_name="chat_history", optional=True),
        ("human", RAG_USER_PROMPT_TEMPLATE),
    ])
