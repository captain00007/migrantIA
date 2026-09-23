"""
Moderador Unificado de Entrada (InputModerator).
Executa as etapas de segurança em cascata:
1. Normalização de Entrada (NFKC, Homoglyphs, Zero-Width Strip)
2. PII Masking (LGPD)
3. InjectionGuard (Prompt Injection, Jailbreaks & Encoding Obfuscation)
4. IntentClassifier (Roteamento inteligente de consultas)
"""
from dataclasses import dataclass
from typing import Optional, Dict, Any

from ia.security.normalizer import normalize_unicode_input
from apps.chat.privacy import sanitize_pii
from ia.guardrails.injection import InjectionGuard
from ia.guardrails.intent import IntentClassifier, QueryIntent


@dataclass
class GuardrailResult:
    """Resultado da inspeção de segurança e moderação de entrada."""
    is_safe: bool
    intent: QueryIntent
    sanitized_text: str
    refusal_message: Optional[str] = None
    reason: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class InputModerator:
    """Moderador de entrada e guardrails pré-retrieval."""

    def __init__(
        self,
        injection_guard: Optional[InjectionGuard] = None,
        intent_classifier: Optional[IntentClassifier] = None,
    ):
        self.injection_guard = injection_guard or InjectionGuard()
        self.intent_classifier = intent_classifier or IntentClassifier()

    def inspect(
        self,
        text: str,
        ui_language: str = "pt",
        language: Optional[str] = None
    ) -> GuardrailResult:
        """
        Executa a verificação completa da pergunta do usuário.
        """
        effective_lang = language or ui_language or "pt"

        # 1. Normalização Unicode e desobfuscação
        normalized = normalize_unicode_input(text or "")

        # 2. PII Masking (LGPD)
        sanitized = sanitize_pii(normalized)

        # 3. Verificação de Jailbreak / Prompt Injection / Ofuscação
        is_safe, refusal, reason = self.injection_guard.inspect(text or "", ui_language=effective_lang)
        if not is_safe:
            return GuardrailResult(
                is_safe=False,
                intent=QueryIntent.OUT_OF_SCOPE,
                sanitized_text=sanitized,
                refusal_message=refusal,
                reason=reason,
                metadata={"blocked_by": "injection_guard", "reason": reason}
            )

        # 4. Classificação de Intenção
        intent = self.intent_classifier.classify(sanitized)

        return GuardrailResult(
            is_safe=True,
            intent=intent,
            sanitized_text=sanitized,
            refusal_message=None,
            reason=None,
            metadata={"intent": intent.value}
        )
