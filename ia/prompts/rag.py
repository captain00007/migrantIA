"""
Templates de Prompts para o Pipeline RAG do MigrantIA.
"""
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from ia.prompts.system import MIGRANTIA_SYSTEM_PROMPT

RAG_USER_PROMPT_TEMPLATE = """=== CONTEXTO OFICIAL AUDITADO (BANCO VETORIAL) ===
{context}

=== MENSAGEM ATUAL DO USUÁRIO ===
{question}

Instruções para geração da resposta:
- Responda no mesmo idioma da mensagem do usuário.
- VERIFICAÇÃO DE ESCOPO: Se a mensagem do usuário for sobre assuntos alheios ao escopo do MigrantIA (como futebol, esportes, celebridades, etc.), recuse educadamente explicando sua finalidade e redirecione para os 4 Pilares de acolhimento e regularização de migrantes no Brasil.
- SE A MENSAGEM FOR UMA DÚVIDA DOS 4 PILARES E HOUVER CONTEXTO OFICIAL: responda fundamentando-se exclusivamente nele e mencione o nome do documento e a página (ex: "conforme o documento X (pág. Y)...").
- SE FOR SAUDAÇÃO OU MUDANÇA DE ASSUNTO: responda cordialmente e relembre os 4 temas de apoio em que você é especialista.
- SE FOR UMA DÚVIDA TÉCNICA SEM CONTEXTO OFICIAL DISPONÍVEL: declare com transparência que não possui essa informação oficial no momento e indique a Defensoria Pública da União (DPU) ou ONGs parceiras.
"""


def get_rag_prompt_template() -> ChatPromptTemplate:
    """Retorna o ChatPromptTemplate configurado para a chain de RAG."""
    return ChatPromptTemplate.from_messages([
        ("system", MIGRANTIA_SYSTEM_PROMPT),
        MessagesPlaceholder(variable_name="chat_history", optional=True),
        ("human", RAG_USER_PROMPT_TEMPLATE),
    ])
