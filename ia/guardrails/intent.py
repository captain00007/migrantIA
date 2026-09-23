"""
Módulo de Intenção e Roteamento Semântico do MigrantIA.
Define as categorias de intenção de consultas sem depender de listas estáticas frágeis.
"""
from enum import Enum


class QueryIntent(str, Enum):
    """Categorias conceituais de intenção de mensagens."""
    KNOWLEDGE_QUERY = "knowledge_query"      # Dúvidas procedimentais, documentais ou de direitos
    CHITCHAT_GREETING = "chitchat_greeting"  # Saudações, apresentações, escopo e capacidades
    OUT_OF_SCOPE = "out_of_scope"            # Temas flagrantemente fora dos 4 Pilares


class IntentClassifier:
    """
    Classificador de intenção com delegação semântica unificada.
    Elimina a necessidade de manter listas manuais e regexes hardcoded,
    delegando a compreensão contextual e multilíngue ao motor semântico do RAG.
    """

    @staticmethod
    def classify(text: str) -> QueryIntent:
        """
        Por padrão, encaminha a consulta para o pipeline semântico unificado do RAG,
        garantindo que qualquer pergunta, saudação ou dúvida em qualquer idioma seja
        interpretada dinamicamente pelo modelo com o System Prompt e o ContextShield.
        """
        if not text or not text.strip():
            return QueryIntent.CHITCHAT_GREETING

        return QueryIntent.KNOWLEDGE_QUERY
