"""
Métricas de Avaliação de Qualidade, Fidelidade e Anti-Alucinação do MigrantIA.
"""
import re
from typing import List
from ia.prompts.multilingual import detect_language_heuristic


def calculate_golden_rule_accuracy(
    actual_triggered: bool,
    expected_triggered: bool
) -> float:
    """
    Avalia a exatidão do acionamento da Regra de Ouro.
    Retorna 1.0 se houve correspondência exata, 0.0 caso contrário.
    """
    return 1.0 if actual_triggered == expected_triggered else 0.0


def calculate_keyword_coverage(
    response_text: str,
    expected_keywords: List[str]
) -> float:
    """
    Calcula a proporção de palavras-chave esperadas presentes na resposta.
    """
    if not expected_keywords:
        return 1.0
    if not response_text:
        return 0.0

    lower_text = response_text.lower()
    matches = sum(1 for kw in expected_keywords if kw.lower() in lower_text)
    return float(matches / len(expected_keywords))


def calculate_hallucination_penalty(
    response_text: str,
    forbidden_terms: List[str]
) -> float:
    """
    Calcula a penalidade por termos proibidos / alucinações detectadas.
    Retorna 0.0 (sem alucinações) ou penalidade proporcional (ex: 1.0 por termo proibido).
    """
    if not forbidden_terms or not response_text:
        return 0.0

    lower_text = response_text.lower()
    violations = sum(1 for term in forbidden_terms if term.lower() in lower_text)
    return float(violations)


def calculate_language_compliance(
    response_text: str,
    target_language: str
) -> float:
    """
    Verifica se o idioma da resposta corresponde ao idioma pretendido pelo caso de teste.
    """
    if not response_text or not target_language:
        return 0.0

    detected = detect_language_heuristic(response_text)
    # Se o idioma detectado bate com o alvo, compliance é 1.0
    if detected == target_language:
        return 1.0

    # Se for uma resposta com termos em português padrão ou multilíngue
    if target_language == "pt" or detected == "pt":
        return 0.8

    return 0.0


def calculate_groundedness_heuristic(
    response_text: str,
    sources_count: int,
    golden_rule_triggered: bool
) -> float:
    """
    Calcula o score de Groundedness (Fundamentação):
    - Se a Regra de Ouro foi acionada corretamente: 1.0
    - Se houver fontes oficiais citadas e texto não-vazio: 1.0
    - Se não houver fontes e não for Regra de Ouro: 0.0
    """
    if golden_rule_triggered:
        return 1.0
    if sources_count > 0 and len(response_text.strip()) > 0:
        return 1.0
    return 0.0
