from ia.evaluation.datasets.benchmark import (
    BENCHMARK_DATASET,
    get_benchmark_dataset,
    BenchmarkCase,
)
from apps.sources.models import PillarChoices


def test_benchmark_dataset_integrity():
    assert len(BENCHMARK_DATASET) >= 10
    
    # Valida presença dos 5 idiomas
    languages = {case.language for case in BENCHMARK_DATASET}
    assert {"ht", "fr", "es", "en", "pt"}.issubset(languages)

    # Valida presença dos 4 pilares
    pillars = {case.pillar for case in BENCHMARK_DATASET}
    assert {
        PillarChoices.IMMIGRATION,
        PillarChoices.EDUCATION,
        PillarChoices.NATIONALITY,
        PillarChoices.COMMUNITY,
    }.issubset(pillars)

    # Valida presença de casos da Regra de Ouro (perguntas armadilha)
    golden_cases = [c for c in BENCHMARK_DATASET if c.should_trigger_golden_rule]
    assert len(golden_cases) >= 2


def test_get_benchmark_dataset_filters():
    ht_cases = get_benchmark_dataset(language="ht")
    assert all(c.language == "ht" for c in ht_cases)

    imm_cases = get_benchmark_dataset(pillar=PillarChoices.IMMIGRATION)
    assert all(c.pillar == PillarChoices.IMMIGRATION for c in imm_cases)
