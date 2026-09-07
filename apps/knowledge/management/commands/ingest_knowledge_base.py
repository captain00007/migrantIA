from django.core.management.base import BaseCommand
from ia.ingestion.indexer import KnowledgeIndexer


class Command(BaseCommand):
    help = "Ingere e indexa a base de conhecimento oficial dos Quatro Pilares no PostgreSQL pgvector"

    def handle(self, *args, **options):
        indexer = KnowledgeIndexer()
        indexer.run()
        self.stdout.write(self.style.SUCCESS("Indexação no pgvector concluída com sucesso!"))
