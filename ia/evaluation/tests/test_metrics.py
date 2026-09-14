from ia.evaluation.metrics import (
    calculate_golden_rule_accuracy,
    calculate_keyword_coverage,
    calculate_hallucination_penalty,
    calculate_language_compliance,
    calculate_groundedness_heuristic,
)


def test_calculate_golden_rule_accuracy():
    assert calculate_golden_rule_accuracy(True, True) == 1.0
    assert calculate_golden_rule_accuracy(False, False) == 1.0
    assert calculate_golden_rule_accuracy(True, False) == 0.0
    assert calculate_golden_rule_accuracy(False, True) == 0.0


def test_calculate_keyword_coverage():
    text = "O CPF pode ser emitido na Receita Federal gratuitamente."
    keywords = ["CPF", "Receita Federal", "Passaporte"]
    # 2 de 3 palavras encontradas
    coverage = calculate_keyword_coverage(text, keywords)
    assert round(coverage, 2) == 0.67


def test_calculate_hallucination_penalty():
    clean_text = "O agendamento na Polícia Federal é online."
    forbidden = ["pague propina", "taxa de R$ 500 para agilizar"]
    assert calculate_hallucination_penalty(clean_text, forbidden) == 0.0

    hallucinated_text = "Você deve pagar taxa de R$ 500 para agilizar o visto."
    assert calculate_hallucination_penalty(hallucinated_text, forbidden) == 1.0


def test_calculate_groundedness_heuristic():
    assert calculate_groundedness_heuristic("Resposta oficial...", sources_count=2, golden_rule_triggered=False) == 1.0
    assert calculate_groundedness_heuristic("Não encontrei...", sources_count=0, golden_rule_triggered=True) == 1.0
    assert calculate_groundedness_heuristic("Texto inventado sem fontes", sources_count=0, golden_rule_triggered=False) == 0.0
