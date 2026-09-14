"""
Comando Django para execução da Auditoria e Homologação Anti-Alucinação do MigrantIA.
Uso: python manage.py evaluate_rag [--language pt|ht|fr|es|en] [--pillar IMMIGRATION|...] [--output relatorio.json]
"""
import json
from django.core.management.base import BaseCommand
from ia.evaluation.datasets.benchmark import get_benchmark_dataset
from ia.evaluation.evaluators import RAGEvaluator


class Command(BaseCommand):
    help = "Executa a bateria de testes de homologação anti-alucinação e fidelidade do RAG."

    def add_arguments(self, parser):
        parser.add_argument(
            "--language",
            type=str,
            help="Filtra benchmark por código de idioma (ex: ht, fr, pt, es, en)",
        )
        parser.add_argument(
            "--pillar",
            type=str,
            help="Filtra benchmark por pilar (ex: IMMIGRATION, EDUCATION, NATIONALITY, COMMUNITY)",
        )
        parser.add_argument(
            "--output",
            type=str,
            help="Caminho do arquivo JSON para salvar o relatório de homologação",
        )

    def handle(self, *args, **options):
        lang = options.get("language")
        pillar = options.get("pillar")
        output_file = options.get("output")

        self.stdout.write(self.style.NOTICE("🔍 Iniciando Bateria de Homologação Constitucional do MigrantIA...\n"))

        dataset = get_benchmark_dataset(language=lang, pillar=pillar)
        self.stdout.write(f"📋 Total de Casos Selecionados: {len(dataset)}\n")

        evaluator = RAGEvaluator()
        summary = evaluator.run_benchmark(dataset=dataset)

        self.stdout.write("=" * 80)
        self.stdout.write(f"{'ID':<12} | {'Idioma':<6} | {'Regra Ouro':<10} | {'Palavras':<8} | {'Alucinação':<10} | {'Status'}")
        self.stdout.write("-" * 80)

        for res in summary.results:
            status_str = self.style.SUCCESS("APROVADO") if res.passed else self.style.ERROR("REPROVADO")
            gr_str = "SIM" if res.golden_rule_triggered else "NÃO"
            self.stdout.write(
                f"{res.case.case_id:<12} | {res.case.language:<6} | {gr_str:<10} | "
                f"{res.keyword_score:<8.2f} | {res.hallucination_penalty:<10.0f} | {status_str}"
            )

        self.stdout.write("=" * 80)
        self.stdout.write(f"\n📊 RESUMO DA AUDITORIA:")
        self.stdout.write(f"• Casos Aprovados: {summary.passed_cases}/{summary.total_cases}")
        self.stdout.write(f"• Acurácia da Regra de Ouro: {summary.golden_rule_accuracy * 100:.1f}%")
        self.stdout.write(f"• Cobertura Média de Palavras-Chave: {summary.average_keyword_coverage * 100:.1f}%")
        self.stdout.write(f"• Score Médio de Groundedness: {summary.average_groundedness * 100:.1f}%")
        self.stdout.write(f"• Total de Alucinações Detectadas: {summary.total_hallucinations_detected}")
        self.stdout.write(f"• Latência Média por Consulta: {summary.average_latency_seconds:.3f}s\n")

        if summary.is_homologated:
            self.stdout.write(self.style.SUCCESS("🎉 PARECER FINAL: MOTOR DE IA HOMOLOGADO COM SUCESSO! ✅"))
        else:
            self.stdout.write(self.style.ERROR("❌ PARECER FINAL: MOTOR REPROVADO NA AUDITORIA CONSTITUCIONAL!"))

        if output_file:
            payload = {
                "total_cases": summary.total_cases,
                "passed_cases": summary.passed_cases,
                "golden_rule_accuracy": summary.golden_rule_accuracy,
                "average_groundedness": summary.average_groundedness,
                "total_hallucinations": summary.total_hallucinations_detected,
                "is_homologated": summary.is_homologated,
            }
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(payload, f, indent=2)
            self.stdout.write(f"💾 Relatório exportado para: {output_file}")
