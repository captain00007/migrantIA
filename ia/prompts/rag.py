"""
Templates de Prompts para o Pipeline RAG do MigrantIA.
"""
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from ia.prompts.system import MIGRANTIA_SYSTEM_PROMPT

RAG_USER_PROMPT_TEMPLATE = """=== CONTEXTO OFICIAL AUDITADO (BANCO VETORIAL) ===
{context}

=== MENSAGEM DO USUÁRIO ===
{question}

Instruções de Hierarquia e Decisão:
1. Se a pergunta for sobre o usuário, dados pessoais ou histórico do diálogo, responda diretamente pelo `chat_history` no idioma da pergunta.
2. Se a pergunta for sobre procedimentos ou leis, utilize o `<official_knowledge_base>`. Se este estiver vazio ou sem dados suficientes, aplique a Regra de Ouro com transparência no idioma da pergunta.
3. Responda SEMPRE no mesmo idioma da mensagem atual do usuário.
"""


def get_rag_prompt_template() -> ChatPromptTemplate:
    """Retorna o ChatPromptTemplate configurado para a chain de RAG."""
    return ChatPromptTemplate.from_messages([
        ("system", MIGRANTIA_SYSTEM_PROMPT),
        MessagesPlaceholder(variable_name="chat_history", optional=True),
        ("human", RAG_USER_PROMPT_TEMPLATE),
    ])
