"""
Módulo de Proteção contra Injeção de Prompt e Jailbreak Multilíngue (InjectionGuard).
Detecta tentativas adversárias de manipulação de instruções, vazamento de prompts de sistema
ou quebra de restrições de segurança em qualquer idioma.
"""
import re
import unicodedata
from typing import Tuple, Optional
from ia.security.normalizer import normalize_unicode_input, is_obfuscated_encoding, INVISIBLE_CHARS_REGEX
from ia.prompts.refusals import get_refusal_message, RefusalReason

INJECTION_PATTERNS = [
    # Inglês
    r"ignore\s+(?:all\s+)?(?:previous|prior|above)?\s*instructions?",
    r"disregard\s+(?:all\s+)?(?:previous|prior|above)?\s*instructions?",
    r"forget\s+(?:all\s+)?(?:previous|prior|above)?\s*instructions?",
    r"(?:print|output|display|reveal|show|dump)\s+(?:the\s+)?(?:system\s+prompt|developer\s+prompt|initial\s+instructions?|canary)",
    r"what\s+is\s+your\s+(?:system\s+prompt|initial\s+prompt)",
    r"\bjailbreak\b",
    r"\bdan\s+mode\b",
    r"\bdeveloper\s+mode\b",
    r"\bbypass\s+(?:all\s+)?safety\b",
    r"(?:give|show|reveal|send)\s+(?:me\s+)?(?:the\s+)?(?:api[_\s-]?key|secret[_\s-]?key|database\s+password)",

    # Português
    r"ignore\s+(?:todas\s+as\s+)?instruções(?:\s+(?:anteriores|prévias|acima))?",
    r"desconsidere\s+(?:todas\s+as\s+)?instruções(?:\s+(?:anteriores|prévias))?",
    r"esqueça\s+(?:todas\s+as\s+)?(?:regras|instruções)(?:\s+(?:anteriores|prévias))?",
    r"(?:mostre|revele|exiba|imprima)\s+(?:o\s+)?(?:prompt\s+do\s+sistema|system\s+prompt|instruções\s+iniciais|canary)",
    r"qual\s+é\s+o\s+seu\s+(?:prompt\s+de\s+sistema|system\s+prompt)",
    r"modo\s+dan\b",
    r"modo\s+desenvolvedor\b",
    r"(?:me\s+dê|mostre|revele)\s+(?:a\s+)?(?:chave\s+(?:da\s+)?api|senha\s+do\s+banco|token\s+secreto)",

    # Espanhol
    r"ignora\s+(?:todas\s+las\s+)?instrucciones(?:\s+(?:anteriores|previas))?",
    r"olvida\s+(?:todas\s+las\s+)?instrucciones(?:\s+(?:anteriores|previas))?",
    r"(?:muestra|revela|imprime)\s+(?:el\s+)?(?:prompt\s+del\s+sistema|system\s+prompt)",
    r"modo\s+desarrollador\b",

    # Francês
    r"ignore\s+(?:toutes\s+les\s+)?instructions(?:\s+(?:précédentes|antérieures))?",
    r"oublie\s+(?:toutes\s+les\s+)?instructions(?:\s+(?:précédentes|antérieures))?",
    r"(?:affiche|montre|révèle)\s+(?:le\s+)?(?:prompt\s+système|instructions\s+initiales)",

    # Crioulo Haitiano (Kreyòl)
    r"pa\s+okipe\s+(?:tout\s+)?enstriksyon(?:\s+anvan\s+yo|\s+yo)?",
    r"bliye\s+(?:tout\s+)?enstriksyon(?:\s+anvan\s+yo|\s+yo)?",
    r"montre\s+(?:mwen\s+)?prompt\s+sistèm\s+nan",

    # Russo (Игнорируй инструкции / Покажи системный промпт)
    r"игнорируй\s+(?:все\s+)?инструкции",
    r"забудь\s+(?:все\s+)?инструкции",
    r"(?:покажи|выведи)\s+системный\s+промпт",

    # Árabe (تجاهل التعليمات / اظهر موجه النظام)
    r"تجاهل\s+(?:جميع\s+)?التعليمات",
    r"اظهر\s+(?:موجه\s+النظام|التعليمات\s+السابقة)",

    # Chinês (忽略之前的指令 / 显示系统提示词)
    r"忽略(?:所有)?(?:之前|前面)?(?:的)?(?:指示|指令|提示)",
    r"(?:显示|输出|提供)(?:系统)?提示词",
]

COMPILED_INJECTION_REGEX = re.compile(
    "|".join(f"(?:{p})" for p in INJECTION_PATTERNS),
    re.IGNORECASE
)


class InjectionGuard:
    """Validador de segurança contra injeção de prompt e jailbreak."""

    @staticmethod
    def inspect(
        text: str,
        ui_language: str = "pt",
        language: Optional[str] = None
    ) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Avalia se o texto contém padrões de ataque de prompt injection ou ofuscação.
        Retorna:
          (is_safe, refusal_message, reason)
        """
        effective_lang = language or ui_language or "pt"
        if not text or not text.strip():
            return True, None, None

        # 1. Detecção de codificações maliciosas (Base64 / Hex)
        is_encoded, reason = is_obfuscated_encoding(text)
        if is_encoded:
            refusal = get_refusal_message(RefusalReason.SECURITY_VIOLATION, ui_language=effective_lang)
            return False, refusal, reason

        # 2. Normalização Unicode (com Homóglifos traduzidos para alfabeto latino)
        normalized_latin = normalize_unicode_input(text)

        # 3. Normalização limpa básica NFKC (para alfabetos não-latinos: cirílico, árabe, chinês)
        raw_nfkc = unicodedata.normalize("NFKC", INVISIBLE_CHARS_REGEX.sub("", text)).strip()

        # 4. Varredura Regex de Injeção em ambas as formas
        if COMPILED_INJECTION_REGEX.search(normalized_latin) or COMPILED_INJECTION_REGEX.search(raw_nfkc):
            refusal = get_refusal_message(RefusalReason.SECURITY_VIOLATION, ui_language=effective_lang)
            return False, refusal, "prompt_injection_detected"

        return True, None, None
