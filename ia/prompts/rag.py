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
- Responda no mesmo idioma da mensagem atual do usuário.
- USO DO HISTÓRICO E CONTEXTO: Analise a mensagem atual em conjunto com o `chat_history`. Se a mensagem fizer referência a informações, fatos, nomes ou perguntas anteriores do diálogo, responda dinamicamente com base nesse histórico, mantendo sempre o direcionamento para o apoio nos 4 Pilares.
- VERIFICAÇÃO DE ESCOPO: Se a mensagem for sobre temas totalmente alheios à finalidade do assistente (ex: esportes, piadas, entretenimento geral), recuse com empatia e redirecione para os 4 Pilares.
- SE HOUVER CONTEXTO OFICIAL RELEVANTE: responda fundamentando-se nele e mencione o nome do documento oficial / página.
- SE FOR UMA DÚVIDA PROCEDIMENTAL SEM CONTEXTO OFICIAL DISPONÍVEL: declare com transparência que não possui essa informação oficial no momento e indique a Defensoria Pública da União (DPU) ou ONGs da rede de apoio.
"""


def get_rag_prompt_template() -> ChatPromptTemplate:
    """Retorna o ChatPromptTemplate configurado para a chain de RAG."""
    return ChatPromptTemplate.from_messages([
        ("system", MIGRANTIA_SYSTEM_PROMPT),
        MessagesPlaceholder(variable_name="chat_history", optional=True),
        ("human", RAG_USER_PROMPT_TEMPLATE),
    ])
