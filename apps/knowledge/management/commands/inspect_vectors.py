from django.core.management.base import BaseCommand
from django.db import connection
import json


class Command(BaseCommand):
    help = "Inspeciona e lista os vetores e fragmentos armazenados no PGVector (PostgreSQL)"

    def add_arguments(self, parser):
        parser.add_argument(
            '--pillar',
            type=str,
            help='Filtrar por pilar (IMMIGRATION, EDUCATION, NATIONALITY, COMMUNITY)',
            default=None,
        )
        parser.add_argument(
            '--limit',
            type=int,
            help='Limite de fragmentos para exibir',
            default=20,
        )

    def handle(self, *args, **options):
        pillar_filter = options.get('pillar')
        limit = options.get('limit')

        with connection.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM langchain_pg_embedding;")
            total_count = cursor.fetchone()[0]

            self.stdout.write(self.style.SUCCESS(f"\n========================================================"))
            self.stdout.write(self.style.SUCCESS(f" 🧠 BANCO VETORIAL PGVECTOR (Total de fragmentos: {total_count})"))
            self.stdout.write(self.style.SUCCESS(f"========================================================\n"))

            if total_count == 0:
                self.stdout.write(self.style.WARNING("Nenhum vetor encontrado. Execute o povoamento da base."))
                return

            query = """
                SELECT 
                    uuid,
                    cmetadata,
                    document,
                    vector_dims(embedding) as dims
                FROM langchain_pg_embedding
            """
            params = []
            if pillar_filter:
                query += " WHERE cmetadata->>'pillar' = %s"
                params.append(pillar_filter.upper())

            query += f" LIMIT {limit};"
            cursor.execute(query, params)
            rows = cursor.fetchall()

            for i, (uid, meta, doc, dims) in enumerate(rows, 1):
                if isinstance(meta, str):
                    meta = json.loads(meta)
                pilar = meta.get('pillar', 'N/A')
                title = meta.get('title', 'Sem título')
                url = meta.get('url', '')
                doc_type = meta.get('document_type', 'N/A')

                self.stdout.write(self.style.HTTP_INFO(f"[{i}] Pilar: {pilar} | Tipo: {doc_type} | Dims: {dims}"))
                self.stdout.write(self.style.SQL_KEYWORD(f"    Título: {title}"))
                if url:
                    self.stdout.write(f"    Fonte Oficial: {url}")
                self.stdout.write(f"    UUID: {uid}")
                self.stdout.write("    Trecho:")
                # Exibir as primeiras 3 linhas do chunk
                sample = "\n".join(["      " + line for line in doc.strip().splitlines()[:4]])
                self.stdout.write(f"{sample}\n")
