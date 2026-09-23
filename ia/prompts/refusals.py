"""
Catálogo Padronizado de Respostas de Recusa e Fallback nos 5 Idiomas da Interface:
- Português (pt - padrão)
- Espanhol (es)
- Inglês (en)
- Francês (fr)
- Crioulo Haitiano (ht)
"""
from enum import Enum
from typing import Dict

DEFAULT_LANGUAGE = "pt"
SUPPORTED_UI_LANGUAGES = ["pt", "es", "en", "fr", "ht"]


class RefusalReason(str, Enum):
    """Motivos de recusa padronizados."""
    SECURITY_VIOLATION = "security_violation"
    OUT_OF_SCOPE = "out_of_scope"
    GOLDEN_RULE = "golden_rule"
    SYSTEM_ERROR = "system_error"


REFUSAL_CATALOG: Dict[RefusalReason, Dict[str, str]] = {
    RefusalReason.SECURITY_VIOLATION: {
        "pt": (
            "Esta solicitação não pode ser processada porque contém comandos que violam as "
            "diretrizes de segurança e escopo do MigrantIA. Como posso ajudar com questões sobre "
            "imigração, educação, nacionalidade ou rede de apoio?"
        ),
        "es": (
            "Esta solicitud no puede procesarse porque contiene instrucciones que infringen las "
            "políticas de seguridad y el alcance de MigrantIA. ¿Cómo puedo ayudarle con trámites "
            "de inmigración, educación, nacionalidad o redes de apoyo?"
        ),
        "en": (
            "This request cannot be processed because it contains instructions that violate "
            "MigrantIA's security guidelines and scope. How may I assist you with immigration, "
            "education, nationality, or community support?"
        ),
        "fr": (
            "Cette demande ne peut pas être traitée car elle contient des instructions contraires "
            "aux politiques de sécurité de MigrantIA. Comment puis-je vous aider concernant l'immigration, "
            "l'éducation, la nationalité ou le réseau de soutien ?"
        ),
        "ht": (
            "Demann sa a pa ka trete paske li gen enstriksyon ki vyole règ sekirite MigrantIA yo. "
            "Kijan mwen ka ede w ak kesyon sou imigrasyon, edikasyon, nasyonalite oswa rezo sipò?"
        ),
    },

    RefusalReason.OUT_OF_SCOPE: {
        "pt": (
            "Como assistente do MigrantIA, minha atuação é dedicada exclusivamente à orientação "
            "jurídica, documental, educacional e humanitária de migrantes e refugiados no Brasil. "
            "Por favor, envie sua dúvida sobre Imigração, Educação, Nacionalidade ou Rede de Apoio."
        ),
        "es": (
            "Como asistente de MigrantIA, mi labor está dedicada exclusivamente a la orientación "
            "jurídica, documental, educativa y humanitaria para personas migrantes y refugiadas en Brasil. "
            "Por favor, envíe su consulta sobre Inmigración, Educación, Nacionalidad o Red de Apoyo."
        ),
        "en": (
            "As MigrantIA assistant, my purpose is strictly dedicated to providing legal, "
            "documentary, educational, and humanitarian guidance for migrants and refugees in Brazil. "
            "Please send your question regarding Immigration, Education, Nationality, or Support Networks."
        ),
        "fr": (
            "En tant qu'assistant de MigrantIA, ma mission est exclusivement dédiée à l'orientation "
            "juridique, documentaire, éducative et humanitaire des migrants et réfugiés au Brésil. "
            "Veuillez poser votre question concernant l'Immigration, l'Éducation, la Nationalité ou le Réseau de Soutien."
        ),
        "ht": (
            "Kòm asistan MigrantIA, misyon mwen konsantre sèlman sou oryantasyon legal, dokiman, "
            "edikasyon ak sipò imanitè pou moun migran ak refijye nan peyi Brezil. "
            "Tanpri poze kesyon w sou Imigrasyon, Edikasyon, Nasyonalite oswa Rezo Sipò."
        ),
    },

    RefusalReason.GOLDEN_RULE: {
        "pt": (
            "Não encontrei essa informação nos canais oficiais consultados. "
            "Recomendo procurar diretamente uma das instituições de apoio cadastradas "
            "ou o órgão competente (DPU, ACNUR, Cáritas, Missão Paz, CRAI)."
        ),
        "es": (
            "No encontré esta información en las fuentes oficiales consultadas. "
            "Le recomiendo comunicarse diretamente con una de las instituciones de apoyo registradas "
            "o el organismo competente (DPU, ACNUR, Cáritas, Missão Paz, CRAI)."
        ),
        "en": (
            "I did not find this information in the official sources consulted. "
            "I recommend contacting one of the registered support organizations "
            "or the competent official authority directly (DPU, UNHCR, Caritas, Missão Paz, CRAI)."
        ),
        "fr": (
            "Je n'ai pas trouvé cette information dans les sources officielles consultées. "
            "Je vous recommande de vous adresser diretamente à l'une des organisations de soutien "
            "ou à l'autorité compétente (DPU, HCR, Caritas, Missão Paz, CRAI)."
        ),
        "ht": (
            "Mwen pa jwenn enfòmasyon sa a nan sous ofisyèl yo konsilte. "
            "Mwen rekòmande pou w kontakte dirèkteman youn nan enstitisyon sipò yo "
            "oswa ògàn konpetan an (DPU, ACNUR, Caritas, Missão Paz, CRAI)."
        ),
    },

    RefusalReason.SYSTEM_ERROR: {
        "pt": (
            "Ocorreu uma instabilidade temporária no processamento da sua solicitação. "
            "Por favor, tente novamente em alguns instantes."
        ),
        "es": (
            "Ocurrió un error temporal al procesar su solicitud. "
            "Por favor, inténtelo de nuevo en unos momentos."
        ),
        "en": (
            "A temporary error occurred while processing your request. "
            "Please try again in a few moments."
        ),
        "fr": (
            "Une erreur temporaire est survenue lors du traitement de votre demande. "
            "Veuillez réessayer dans quelques instants."
        ),
        "ht": (
            "Gen yon ti pwoblèm teknik ki pase pandan n ap trete demann ou an. "
            "Tanpri reye nan kèk moman."
        ),
    },
}


def get_refusal_message(reason: RefusalReason, ui_language: str = DEFAULT_LANGUAGE) -> str:
    """Retorna a mensagem de recusa padronizada no idioma da interface solicitado."""
    lang_key = (ui_language or DEFAULT_LANGUAGE).lower().strip()[:2]
    catalog = REFUSAL_CATALOG.get(reason, REFUSAL_CATALOG[RefusalReason.SECURITY_VIOLATION])
    return catalog.get(lang_key, catalog[DEFAULT_LANGUAGE])
