"""
Filtros de governança, segurança e deduplicação semântica do MigrantIA.
Inclui:
1. Proteção contra SEO Poisoning, invasão de subdomínios (bets/cassinos) e filtro por score.
2. Normalização e Deduplicação de URLs e Snippets de Busca Web.
3. Deduplicação em 2 Camadas (R$ 0,00):
   - Camada 1: Estrutural & Léxica (Exato + Shingling 3-grams & Jaccard + Contenção) com fusão de metadados de páginas.
   - Camada 2: Sentido Puro (Similaridade de Cosseno entre Embeddings Vetoriais na CPU).
"""
import re
import math
import logging
from typing import List, Optional, Dict, Any, Set
from urllib.parse import urlparse, urlunparse
from langchain_core.documents import Document

logger = logging.getLogger(__name__)

# Palavras-chave associadas a apostas, cassinos e SEO poisoning em subdomínios governamentais
SPAM_KEYWORDS = [
    "bet", "bets", "bet365", "betano", "blaze", "cassino", "casino",
    "slot", "slots", "fortune tiger", "tigrinho", "roleta", "apostas",
    "aposta", "jogo do bicho", "palpite", "odds", "green", "pixbet",
    "1xbet", "sportingbet", "kto", "f12", "esportes da sorte", "vai de bet",
    "jackpot", "poker", "baccarat", "blackjack", "crash game", "mines",
    "aviator", "spaceman", "ganhar dinheiro facil", "renda extra telegram",
    "urubu do pix", "renda facil", "plataforma pagando", "bug do pix",
    "borussia", "mönchengladbach", "estatísticas de", "futebol", "escalação", "jogos de hoje"
]

DEFAULT_MIN_SEARCH_SCORE: float = 0.50
DEFAULT_MAX_SEMANTIC_SIMILARITY: float = 0.88


def extract_domain(url_or_domain: str) -> str:
    """Extrai o hostname / domínio limpo de uma URL ou string de domínio."""
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


def normalize_url(url: str) -> str:
    """Normaliza uma URL removendo parâmetros de rastreamento, fragmentos e barras extras."""
    if not url:
        return ""
    cleaned = url.strip()
    if not cleaned.startswith(("http://", "https://")):
        cleaned = "https://" + cleaned
    parsed = urlparse(cleaned)
    
    # Remove fragmentos e normaliza caminho
    path = parsed.path.rstrip("/")
    # Mantém apenas a URL limpa (esquema, domínio e caminho base)
    normalized = urlunparse((parsed.scheme.lower(), parsed.netloc.lower(), path, "", "", ""))
    return normalized


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
    Filtra e deduplica uma lista de fontes externas (Tavily/Web):
    1. Retém apenas domínios pertencentes à whitelist.
    2. Descarta URLs duplicadas ou normalizadas idênticas.
    3. Descarta resultados com pontuação de relevância abaixo de min_score.
    4. Descarta resultados identificados como spam / SEO poisoning.
    5. Deduplica snippets estruturalmente quase idênticos.
    """
    filtered: List[Dict[str, Any]] = []
    seen_urls: Set[str] = set()
    seen_shingles: List[Set[str]] = []

    for src in sources:
        raw_url = src.get("url", "")
        if not is_domain_whitelisted(raw_url, allowed_domains):
            continue

        clean_url = normalize_url(raw_url)
        if clean_url in seen_urls or raw_url in seen_urls:
            continue

        score = src.get("score")
        if score is not None and score < min_score:
            logger.info(f"[Filter] Resultado descartado por score baixo ({score} < {min_score}): {raw_url}")
            continue

        title = src.get("title", "")
        content = src.get("content", "")

        if filter_spam:
            if is_spam_or_irrelevant(title, raw_url, content):
                continue

        # Deduplica snippets quase idênticos entre URLs diferentes (espelhos/anchors repetidos)
        snippet_shingles = get_shingles(content[:300], n=3)
        if snippet_shingles:
            is_dup_snippet = False
            for prev_sh in seen_shingles:
                if calculate_jaccard_similarity(snippet_shingles, prev_sh) >= 0.80:
                    is_dup_snippet = True
                    break
            if is_dup_snippet:
                logger.info(f"[Filter] Snippet web redundante descartado: {raw_url}")
                continue
            seen_shingles.append(snippet_shingles)

        seen_urls.add(clean_url)
        seen_urls.add(raw_url)
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
    1. Camada 1 (Quase-Idêntico / Estrutural): Shingling 3-grams + Jaccard + Contenção Léxica.
       - Mescla números de página em metadados quando chunks duplicados são consolidados.
    2. Camada 2 (Sentido Puro / Vetorial): Similaridade de Cosseno entre Embeddings na CPU.
    """
    if not documents:
        return []

    # --- Camada 1: Quase-Idêntico (Estrutural & Léxico) ---
    unique_docs: List[Document] = []
    shingles_cache: List[Set[str]] = []
    words_cache: List[Set[str]] = []
    exact_content_cache: Set[str] = set()

    for doc in documents:
        content = (doc.page_content or "").strip()
        if len(content) < 10:
            continue

        normalized_clean = " ".join(content.lower().split())
        if normalized_clean in exact_content_cache:
            # Consolida páginas no documento já aceito correspondente
            _merge_doc_pages(unique_docs, doc)
            continue

        doc_shingles = get_shingles(content, n=3)
        doc_words = tokenize_words(content)

        if not doc_words:
            continue

        is_duplicate = False
        for idx, (prev_shingles, prev_words) in enumerate(zip(shingles_cache, words_cache)):
            jaccard = calculate_jaccard_similarity(doc_shingles, prev_shingles)
            containment = calculate_containment(doc_words, prev_words)

            if jaccard >= max_jaccard or containment >= max_containment:
                logger.info(
                    f"[Deduplication - Quase Idêntico] Chunk redundante descartado (Jaccard: {jaccard:.2f}, Containment: {containment:.2f}): "
                    f"'{content[:60]}...'"
                )
                is_duplicate = True
                _merge_single_doc_pages(unique_docs[idx], doc)
                break

        if not is_duplicate:
            # Inicializa lista de páginas se houver página definida
            _init_doc_pages(doc)
            unique_docs.append(doc)
            shingles_cache.append(doc_shingles)
            words_cache.append(doc_words)
            exact_content_cache.add(normalized_clean)

    # --- Camada 2: Sentido Puro (Vetorial na CPU) ---
    active_embedding_service = embedding_service
    if active_embedding_service is None:
        try:
            from ia.embeddings.service import get_embedding_service
            active_embedding_service = get_embedding_service()
        except Exception:
            active_embedding_service = None

    if active_embedding_service is not None and len(unique_docs) > 1:
        try:
            texts = [d.page_content for d in unique_docs]
            vectors = active_embedding_service.embed_documents(texts)

            semantic_unique_docs: List[Document] = []
            accepted_vectors: List[List[float]] = []

            for doc, vec in zip(unique_docs, vectors):
                is_semantically_redundant = False
                for idx, prev_vec in enumerate(accepted_vectors):
                    cos_sim = calculate_cosine_similarity(vec, prev_vec)
                    if cos_sim >= max_semantic_similarity:
                        logger.info(
                            f"[Deduplication - Sentido Puro] Chunk redundante descartado por similaridade de cosseno ({cos_sim:.2f} >= {max_semantic_similarity}): "
                            f"'{doc.page_content[:60]}...'"
                        )
                        is_semantically_redundant = True
                        _merge_single_doc_pages(semantic_unique_docs[idx], doc)
                        break

                if not is_semantically_redundant:
                    semantic_unique_docs.append(doc)
                    accepted_vectors.append(vec)

            return semantic_unique_docs
        except Exception as exc:
            logger.warning(f"[Deduplication] Camada de sentido puro ignorada por erro: {exc}")

    return unique_docs


def _init_doc_pages(doc: Document) -> None:
    """Inicializa estrutura de páginas no metadado do documento."""
    if not hasattr(doc, "metadata") or doc.metadata is None:
        doc.metadata = {}
    page = doc.metadata.get("page")
    if page is not None and "pages" not in doc.metadata:
        doc.metadata["pages"] = [page]


def _merge_single_doc_pages(target_doc: Document, duplicate_doc: Document) -> None:
    """Mescla metadados de páginas de um chunk duplicado no chunk aceito."""
    if not hasattr(target_doc, "metadata") or target_doc.metadata is None:
        target_doc.metadata = {}
    if not hasattr(duplicate_doc, "metadata") or duplicate_doc.metadata is None:
        return

    dup_pages = set()
    if duplicate_doc.metadata.get("page") is not None:
        dup_pages.add(duplicate_doc.metadata.get("page"))
    if "pages" in duplicate_doc.metadata and isinstance(duplicate_doc.metadata["pages"], (list, set)):
        dup_pages.update(duplicate_doc.metadata["pages"])

    if dup_pages:
        existing_pages = set(target_doc.metadata.get("pages", []))
        if target_doc.metadata.get("page") is not None:
            existing_pages.add(target_doc.metadata.get("page"))
        existing_pages.update(dup_pages)
        target_doc.metadata["pages"] = sorted(list(existing_pages))


def _merge_doc_pages(unique_docs: List[Document], duplicate_doc: Document) -> None:
    """Encontra o documento correspondente e mescla as páginas."""
    dup_title = duplicate_doc.metadata.get("title", "") if duplicate_doc.metadata else ""
    dup_url = duplicate_doc.metadata.get("url", "") if duplicate_doc.metadata else ""
    for u_doc in unique_docs:
        u_title = u_doc.metadata.get("title", "") if u_doc.metadata else ""
        u_url = u_doc.metadata.get("url", "") if u_doc.metadata else ""
        if (dup_url and u_url == dup_url) or (dup_title and u_title == dup_title):
            _merge_single_doc_pages(u_doc, duplicate_doc)
            break
