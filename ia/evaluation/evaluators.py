"""
Orquestrador de Avaliação e Homologação RAG do MigrantIA.
"""
import time
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

from ia.evaluation.datasets.benchmark import BenchmarkCase, get_benchmark_dataset
from ia.evaluation.metrics import (
    calculate_golden_rule_accuracy,
    calculate_keyword_coverage,
    calculate_hallucination_penalty,
    calculate_language_compliance,
    calculate_groundedness_heuristic,
)
from ia.rag.pipeline import RAGPipeline, get_rag_pipeline


@dataclass
class CaseEvaluationResult:
    case: BenchmarkCase
    latency_seconds: float
    response_content: str
    golden_rule_triggered: bool
    sources_count: int
    golden_rule_score: float
    keyword_score: float
    hallucination_penalty: float
    language_score: float
    groundedness_score: float
    passed: bool
    details: str = ""


@dataclass
class BenchmarkSummary:
    total_cases: int
    passed_cases: int
    failed_cases: int
    golden_rule_accuracy: float
    average_keyword_coverage: float
    average_language_compliance: float
    average_groundedness: float
    total_hallucinations_detected: int
    average_latency_seconds: float
    is_homologated: bool
    results: List[CaseEvaluationResult] = field(default_factory=list)


class RAGEvaluator:
    """
    Avaliador do motor RAG contra o dataset de homologação constitucional.
    """

    def __init__(self, pipeline: Optional[RAGPipeline] = None):
        self.pipeline = pipeline or get_rag_pipeline()

    def evaluate_case(self, case: BenchmarkCase) -> CaseEvaluationResult:
        """Executa um caso de teste individual e calcula as métricas."""
        start_time = time.perf_counter()
        
        rag_response = self.pipeline.query(
            question=case.question,
            ui_language=case.language,
            pillar_filter=case.pillar
        )
        
        latency = time.perf_counter() - start_time

        # Cálculos de Métricas
        gr_score = calculate_golden_rule_accuracy(
            actual_triggered=rag_response.golden_rule_triggered,
            expected_triggered=case.should_trigger_golden_rule
        )
        kw_score = calculate_keyword_coverage(
            response_text=rag_response.content,
            expected_keywords=case.expected_keywords
        )
        hal_penalty = calculate_hallucination_penalty(
            response_text=rag_response.content,
            forbidden_terms=case.forbidden_terms
        )
        lang_score = calculate_language_compliance(
            response_text=rag_response.content,
            target_language=case.language
        )
        groundedness = calculate_groundedness_heuristic(
            response_text=rag_response.content,
            sources_count=len(rag_response.sources),
            golden_rule_triggered=rag_response.golden_rule_triggered
        )

        # Critério de Aprovação do Caso
        passed = (
            gr_score == 1.0
            and hal_penalty == 0.0
            and (kw_score >= 0.3 or case.should_trigger_golden_rule)
        )

        return CaseEvaluationResult(
            case=case,
            latency_seconds=round(latency, 3),
            response_content=rag_response.content,
            golden_rule_triggered=rag_response.golden_rule_triggered,
            sources_count=len(rag_response.sources),
            golden_rule_score=gr_score,
            keyword_score=round(kw_score, 2),
            hallucination_penalty=hal_penalty,
            language_score=round(lang_score, 2),
            groundedness_score=round(groundedness, 2),
            passed=passed,
        )

    def run_benchmark(
        self,
        dataset: Optional[List[BenchmarkCase]] = None,
    ) -> BenchmarkSummary:
        """Executa a bateria completa de testes de benchmark e sumariza as métricas."""
        cases = dataset or get_benchmark_dataset()
        results: List[CaseEvaluationResult] = []

        for case in cases:
            res = self.evaluate_case(case)
            results.append(res)

        total = len(results)
        passed_count = sum(1 for r in results if r.passed)
        failed_count = total - passed_count

        avg_gr = sum(r.golden_rule_score for r in results) / total if total else 0.0
        avg_kw = sum(r.keyword_score for r in results) / total if total else 0.0
        avg_lang = sum(r.language_score for r in results) / total if total else 0.0
        avg_groundedness = sum(r.groundedness_score for r in results) / total if total else 0.0
        total_hallucinations = int(sum(r.hallucination_penalty for r in results))
        avg_latency = sum(r.latency_seconds for r in results) / total if total else 0.0

        # Critérios Constitucionais de Homologação
        is_homologated = (
            avg_gr >= 0.90
            and total_hallucinations == 0
            and avg_groundedness >= 0.85
        )

        return BenchmarkSummary(
            total_cases=total,
            passed_cases=passed_count,
            failed_cases=failed_count,
            golden_rule_accuracy=round(avg_gr, 2),
            average_keyword_coverage=round(avg_kw, 2),
            average_language_compliance=round(avg_lang, 2),
            average_groundedness=round(avg_groundedness, 2),
            total_hallucinations_detected=total_hallucinations,
            average_latency_seconds=round(avg_latency, 3),
            is_homologated=is_homologated,
            results=results,
        )
