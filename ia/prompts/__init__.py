from ia.prompts.system import MIGRANTIA_SYSTEM_PROMPT
from ia.prompts.multilingual import (
    SUPPORTED_UI_LANGUAGES,
    GOLDEN_RULE_MESSAGES,
    get_golden_rule_fallback,
)
from ia.prompts.rag import get_rag_prompt_template, RAG_USER_PROMPT_TEMPLATE

__all__ = [
    "MIGRANTIA_SYSTEM_PROMPT",
    "SUPPORTED_UI_LANGUAGES",
    "GOLDEN_RULE_MESSAGES",
    "get_golden_rule_fallback",
    "get_rag_prompt_template",
    "RAG_USER_PROMPT_TEMPLATE",
]
