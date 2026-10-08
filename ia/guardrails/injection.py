"""
Módulo de Proteção contra Injeção de Prompt e Jailbreak Multilíngue (InjectionGuard).
Detecta tentativas adversárias de manipulação de instruções, vazamento de prompts de sistema,
quebra de restrições de segurança ou extração de segredos/chaves de API em qualquer idioma.
"""
import re
import unicodedata
from typing import Tuple, Optional
from ia.security.normalizer import normalize_unicode_input, is_obfuscated_encoding, INVISIBLE_CHARS_REGEX
from ia.prompts.refusals import get_refusal_message, RefusalReason

INJECTION_PATTERNS = [
    # Inglês
    r"(?:ignore|disregard|forget|bypass|disable|override|remove|clear)\s+(?:all\s+)?(?:previous|prior|above|system)?\s*(?:instructions?|rules?|guidelines?|protections?|safety|guardrails?|filters?|constraints?)",
    r"(?:print|output|display|reveal|show|dump)\s+(?:the\s+)?(?:system\s+prompt|developer\s+prompt|initial\s+instructions?|canary)",
    r"what\s+is\s+your\s+(?:system\s+prompt|initial\s+prompt)",
    r"\bjailbreak\b",
    r"\bdan\s+mode\b",
    r"\bdeveloper\s+mode\b",
    r"\bbypass\s+(?:all\s+)?safety\b",
    r"(?:give|show|reveal|send|pass|provide|share|dump|print|display)\s+(?:me\s+)?(?:the\s+)?(?:all\s+)?(?:api[_\s-]?key|secret[_\s-]?key|database\s+password|api\s+token|credentials|access\s+token|admin\s+password|root\s+password)",

    # Português
    r"(?:esquecer|esqueça|esquece|esqueca|ignorar|ignore|ignora|desconsiderar|desconsidere|desconsidera|desativar|desative|desativa|remover|remova|remove|anular|anule|anula|burlar|burla|burle|bypassar|bypass|cancelar|cancele|cancela|suspender|suspenda|suspende|desligar|desliga|desligue)\s+(?:tudo\s+o?\s*|todas?\s+as?\s*|toda\s+a?\s*|todo\s+o?\s*|as?\s+|os?\s+|suas?\s+|seus?\s+|qualquer\s+|quaisquer\s+)*(?:instruç(?:ão|ões|ao|oes)|regras?|diretrizes?|proteç(?:ão|ões|ao|oes)|restriç(?:ão|ões|ao|oes)|filtros?|salvaguardas?|segurança|seguranca|guardrails?|travas?|limitaç(?:ão|ões|ao|oes))",
    r"(?:(?:me\s+)?(?:dê|dar|da|mostre|mostrar|mostra|revele|revelar|revela|passe|passar|passa|envie|enviar|envia|mande|mandar|manda|forneça|fornecer|fornece|exiba|exibir|exibe|libere|liberar|libera|compartilhe|compartilhar|compartilha))\s+(?:me\s+)?(?:todas?\s+as?\s+|o\s+|a\s+|os\s+|as\s+|sua\s+|seu\s+)?(?:api[_\s-]?key|chave\s+(?:da\s+|de\s+)?api|token\s+(?:da\s+|de\s+)?api|api[_\s-]?token|secret[_\s-]?key|senha\s+do\s+banco|senha\s+de\s+root|credenciais|token\s+secreto)",
    r"(?:(?:qual\s+é\s+o\s+seu|qual\s+e\s+o\s+seu|me\s+(?:dê|da|mostre|passe|envie))\s+(?:o\s+)?(?:prompt\s+do\s+sistema|system\s+prompt|instruções\s+iniciais|canary))",
    r"modo\s+dan\b",
    r"modo\s+desenvolvedor\b",

    # Espanhol
    r"(?:ignora|olvida|desactiva|anula|elimina|salta)\s+(?:todas\s+las\s+)?(?:instrucciones|reglas|protecciones|directrices|restricciones)(?:\s+(?:anteriores|previas))?",
    r"(?:muestra|muéstrame|revela|imprime|dame|pasa|envía)\s+(?:el\s+|la\s+)?(?:prompt\s+del\s+sistema|system\s+prompt|api[_\s-]?key|clave\s+de\s+api|token\s+secreto)",
    r"modo\s+desarrollador\b",

    # Francês
    r"(?:ignore|oublie|désactive|contourne)\s+(?:toutes\s+les\s+)?(?:instructions|règles|protections|directives)(?:\s+(?:précédentes|antérieures))?",
    r"(?:affiche|montre|révèle|donne)\s+(?:le\s+|la\s+)?(?:prompt\s+système|instructions\s+initiales|clé\s+api|api[_\s-]?key)",

    # Crioulo Haitiano (Kreyòl)
    r"(?:pa\s+okipe|bliye|inore)\s+(?:tout\s+)?(?:enstriksyon|règ|pwoteksyon)(?:\s+anvan\s+yo|\s+yo)?",
    r"(?:montre|ban|revele)(?:\s+mwen)?\s+(?:prompt\s+sistèm\s+nan|kle\s+api\s+a|api[_\s-]?key)",

    # Russo (Игнорируй инструкции / Покажи системный промпт)
    r"(?:игнорируй|забудь|отключи)\s+(?:все\s+)?(?:инструкции|правила|защиту)",
    r"(?:покажи|выведи|дай)\s+(?:системный\s+промпт|api\s+ключ)",

    # Árabe (تجاهل التعليمات / اظهر موجه النظام)
    r"(?:تجاهل|انس|عطل)\s+(?:جميع\s+)?(?:التعليمات|القواعد|الحماية)",
    r"(?:اظهر|اعطني|اكشف)\s+(?:موجه\s+النظام|التعليمات\s+السابقة|مفتاح\s+api)",

    # Chinês (忽略之前的指令 / 显示系统提示词)
    r"(?:忽略|忘记|跳过|关闭)(?:所有)?(?:之前|前面)?(?:的)?(?:指示|指令|提示|规则|保护)",
    r"(?:显示|输出|提供|给我)(?:系统)?(?:提示词|api[_\s-]?key|密钥)",
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
