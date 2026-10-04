"""
Filtros de governança, segurança e deduplicação semântica do MigrantIA.
Inclui:
1. Proteção contra SEO Poisoning, invasão de subdomínios (bets/cassinos) e filtro por score.
2. Deduplicação em 2 Camadas (R$ 0,00):
   - Camada 1: Estrutural (Quase-Idêntico / Shingling 3-grams & Jaccard)
   - Camada 2: Sentido Puro (Similaridade de Cosseno entre Embeddings Vetoriais)
"""
import re
import math
import logging
from typing import List, Optional, Dict, Any, Set
from urllib.parse import urlparse
from langchain_core.documents import Document

logger = logging.getLogger(__name__)

# Padrões e termos comuns de SEO Poisoning, invasões de subdomínios, apostas, cassinos e spam
SPAM_KEYWORDS = [
    "bet", "bets", "aposta", "apostas", "cassino", "casino", "slot", "slots",
    "fortune tiger", "jogo do bicho", "pg soft", "roleta", "poker", "palpites",
    "odds", "odd", "bonus de cadastro", "bônus de cadastro", "baixar app",
    "app download", "apk download", "resultado do jogo", "estatísticas de",
    "estatisticas de", "borussia", "mönchengladbach", "jogos online",
    "links patrocinados", "tigrinho", "mines", "aviator", "spaceman", "crash game",
    "acompanhante", "acompanhantes", "sexo", "porno", "porn", "casa de aposta"
]

DEFAULT_MIN_SEARCH_SCORE: float = 0.50
DEFAULT_MAX_SEMANTIC_SIMILARITY: float = 0.88


def extract_domain(url_or_domain: str) -> str:
    """Extrai o domínio limpo de uma URL ou string."""
    if not url_or_domain:
        return ""
    cleaned = url_or_domain.strip().lower()
    if not cleaned.startswith(("http://", "https://")):
        cleaned = "https://" + cleaned
    parsed = urlparse(cleaned)
    netloc = parsed.netloc or parsed.path
    if ":" in netloc:
        netloc = netloc.split(":")[0]
    return netloc


def is_domain_whitelisted(url: str, allowed_domains: List[str]) -> bool:
    """
    Verifica se a URL ou domínio pertence estritamente à whitelist homologada.
    Suporta correspondência exata ou subdomínios (ex: pf.gov.br dentro de gov.br).
    """
    if not url or not allowed_domains:
        return False

    target_domain = extract_domain(url)
    if not target_domain:
        return False

    for allowed in allowed_domains:
        clean_allowed = extract_domain(allowed)
        if not clean_allowed:
            continue
        if target_domain == clean_allowed or target_domain.endswith("." + clean_allowed):
            return True

    return False


def is_spam_or_irrelevant(title: str, url: str, content: str = "") -> bool:
    """
    Verifica se um resultado de busca web contém indícios de spam, SEO poisoning ou invasão de subdomínio.
    """
    text_to_check = f"{title} {url} {content[:300]}".lower()

    for kw in SPAM_KEYWORDS:
        if kw in url.lower():
            logger.warning(f"[AntiSpam] Resultado bloqueado (termo na URL: '{kw}'): {url}")
            return True
        pattern = r'(?:\b|_|-)' + re.escape(kw) + r'(?:\b|_|-)'
        if re.search(pattern, text_to_check):
            logger.warning(f"[AntiSpam] Resultado bloqueado (termo detectado: '{kw}'): {title} - {url}")
            return True

    return False


def filter_whitelisted_sources(
    sources: List[Dict[str, Any]],
    allowed_domains: List[str],
    min_score: float = DEFAULT_MIN_SEARCH_SCORE,
    filter_spam: bool = True,
) -> List[Dict[str, Any]]:
    """
    Filtra uma lista de fontes externas:
    1. Retém apenas domínios pertencentes à whitelist.
    2. Descarta resultados com pontuação de relevância abaixo de min_score.
    3. Descarta resultados identificados como spam / SEO poisoning.
    """
    filtered: List[Dict[str, Any]] = []
    seen_urls: Set[str] = set()

    for src in sources:
        url = src.get("url", "")
        if not is_domain_whitelisted(url, allowed_domains):
            continue

        if url in seen_urls:
            continue

        score = src.get("score")
        if score is not None and score < min_score:
            logger.info(f"[Filter] Resultado descartado por score baixo ({score} < {min_score}): {url}")
            continue

        if filter_spam:
            title = src.get("title", "")
            content = src.get("content", "")
            if is_spam_or_irrelevant(title, url, content):
                continue

        seen_urls.add(url)
        filtered.append(src)

    return filtered


# =============================================================================
# Deduplicação Semântica de Chunks (Camada 1: Quase-Idêntico + Camada 2: Sentido Puro)
# =============================================================================

def tokenize_words(text: str) -> Set[str]:
    """Extrai conjunto de palavras normalizadas para cálculo de sobreposição."""
    if not text:
        return set()
    cleaned = re.sub(r"[^\w\s]", " ", text.lower())
    return set(w for w in cleaned.split() if len(w) > 1)


def get_shingles(text: str, n: int = 3) -> Set[str]:
    """Gera n-gramas (shingles) de palavras para capturar ordem estrutural do texto."""
    if not text:
        return set()
    cleaned = re.sub(r"[^\w\s]", " ", text.lower())
    words = [w for w in cleaned.split() if len(w) > 1]
    if len(words) < n:
        return set([" ".join(words)])
    return set(" ".join(words[i : i + n]) for i in range(len(words) - n + 1))


def calculate_jaccard_similarity(set_a: Set[str], set_b: Set[str]) -> float:
    """Calcula a similaridade de Jaccard entre dois conjuntos (|A ∩ B| / |A ∪ B|)."""
    if not set_a or not set_b:
        return 0.0
    intersection = len(set_a.intersection(set_b))
    union = len(set_a.union(set_b))
    if union == 0:
        return 0.0
    return intersection / union


def calculate_containment(set_a: Set[str], set_b: Set[str]) -> float:
    """Calcula a taxa de contenção entre dois conjuntos (|A ∩ B| / min(|A|, |B|))."""
    if not set_a or not set_b:
        return 0.0
    min_len = min(len(set_a), len(set_b))
    if min_len == 0:
        return 0.0
    return len(set_a.intersection(set_b)) / min_len


def calculate_cosine_similarity(vec_a: List[float], vec_b: List[float]) -> float:
    """Calcula a similaridade de cosseno pura entre dois vetores de embedding."""
    if not vec_a or not vec_b or len(vec_a) != len(vec_b):
        return 0.0
    dot_product = sum(a * b for a, b in zip(vec_a, vec_b))
    norm_a = math.sqrt(sum(a * a for a in vec_a))
    norm_b = math.sqrt(sum(b * b for b in vec_b))
    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0
    return dot_product / (norm_a * norm_b)


def deduplicate_documents(
    documents: List[Document],
    max_jaccard: float = 0.70,
    max_containment: float = 0.85,
    embedding_service: Optional[Any] = None,
    max_semantic_similarity: float = DEFAULT_MAX_SEMANTIC_SIMILARITY,
) -> List[Document]:
    """
    Deduplicação Completa em 2 Camadas (Custo R$ 0,00):
    1. Camada 1 (Quase-Idêntico): Shingling 3-grams + Jaccard + Contenção Léxica.
    2. Camada 2 (Sentido Puro): Similaridade de Cosseno entre Embeddings Vetoriais.
    """
    if not documents:
        return []

    # --- Camada 1: Quase-Idêntico (Estrutural) ---
    unique_docs: List[Document] = []
    shingles_cache: List[Set[str]] = []
    words_cache: List[Set[str]] = []

    for doc in documents:
        content = doc.page_content or ""
        doc_shingles = get_shingles(content, n=3)
        doc_words = tokenize_words(content)

        if not doc_words:
            continue

        is_duplicate = False
        for prev_shingles, prev_words in zip(shingles_cache, words_cache):
            jaccard = calculate_jaccard_similarity(doc_shingles, prev_shingles)
            containment = calculate_containment(doc_words, prev_words)

            if jaccard >= max_jaccard or containment >= max_containment:
                logger.info(
                    f"[Deduplication - Quase Idêntico] Chunk redundante descartado (Jaccard: {jaccard:.2f}, Containment: {containment:.2f}): "
                    f"'{content[:60]}...'"
                )
                is_duplicate = True
                break

        if not is_duplicate:
            unique_docs.append(doc)
            shingles_cache.append(doc_shingles)
            words_cache.append(doc_words)

    # --- Camada 2: Sentido Puro (Vetorial) ---
    if embedding_service is not None and len(unique_docs) > 1:
        try:
            texts = [d.page_content for d in unique_docs]
            vectors = embedding_service.embed_documents(texts)

            semantic_unique_docs: List[Document] = []
            accepted_vectors: List[List[float]] = []

            for doc, vec in zip(unique_docs, vectors):
                is_semantically_redundant = False
                for prev_vec in accepted_vectors:
                    cos_sim = calculate_cosine_similarity(vec, prev_vec)
                    if cos_sim >= max_semantic_similarity:
                        logger.info(
                            f"[Deduplication - Sentido Puro] Chunk redundante descartado por similaridade de cosseno ({cos_sim:.2f} >= {max_semantic_similarity}): "
                            f"'{doc.page_content[:60]}...'"
                        )
                        is_semantically_redundant = True
                        break

                if not is_semantically_redundant:
                    semantic_unique_docs.append(doc)
                    accepted_vectors.append(vec)

            return semantic_unique_docs
        except Exception as exc:
            logger.warning(f"[Deduplication] Camada de sentido puro ignorada por erro: {exc}")

    return unique_docs
