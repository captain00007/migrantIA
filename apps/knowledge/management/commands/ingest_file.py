import os
from pathlib import Path
from django.core.management.base import BaseCommand, CommandError
from apps.sources.models import PillarChoices, OfficialSource, WhitelistDomain
from apps.knowledge.models import DocumentTypeChoices, KnowledgeDocument
from ia.ingestion.loaders.document import DocumentLoader
from ia.ingestion.indexer import KnowledgeIndexer


class Command(BaseCommand):
    help = "Faz o upload/ingestão e vetorização de um arquivo (PDF, DOCX, TXT, MD) no PGVector e salva na pasta do hash"

    def add_arguments(self, parser):
        parser.add_argument("file_path", type=str, help="Caminho do arquivo a ser ingerido")
        parser.add_argument(
            "--pillar",
            type=str,
            required=True,
            choices=[c[0] for c in PillarChoices.choices],
            help="Pilar de conhecimento (IMMIGRATION, EDUCATION, NATIONALITY, COMMUNITY)",
        )
        parser.add_argument(
            "--title",
            type=str,
            default=None,
            help="Título do documento (opcional, padrão: nome do arquivo)",
        )
        parser.add_argument(
            "--url",
            type=str,
            default="",
            help="URL oficial de referência do documento (opcional)",
        )
        parser.add_argument(
            "--type",
            type=str,
            default=DocumentTypeChoices.GUIDE,
            choices=[c[0] for c in DocumentTypeChoices.choices],
            help="Tipo de documento (LAW, DECREE, PORTARIA, GUIDE, CARTILHA, FAQ)",
        )

    def handle(self, *args, **options):
        file_path_str = options["file_path"]
        file_path = Path(file_path_str)

        if not file_path.exists():
            raise CommandError(f"Arquivo não encontrado: {file_path_str}")

        pillar = options["pillar"]
        title = options.get("title") or file_path.stem.replace("_", " ").replace("-", " ").title()
        url = options.get("url") or ""
        doc_type = options.get("type") or DocumentTypeChoices.GUIDE

        self.stdout.write(self.style.NOTICE(f"📂 Carregando arquivo: {file_path.name}..."))

        loader = DocumentLoader()
        try:
            # Carregar documentos usando o DocumentLoader
            result = loader.load(source=str(file_path), custom_title=title, url=url)
            raw_docs = result.get("documents", [])
            if not raw_docs:
                from langchain_core.documents import Document
                content = result.get("content", "")
                if content:
                    raw_docs = [Document(page_content=content, metadata={"title": title, "url": url})]
            self.stdout.write(self.style.NOTICE(f"Documentos raw loader: {len(raw_docs)} página(s)/documento(s) extraído(s)"))
        except Exception as e:
            raise CommandError(f"Erro ao processar arquivo com DocumentLoader: {e}")

        if not raw_docs:
            raise CommandError("Nenhum conteúdo pôde ser extraído do arquivo.")

        self.stdout.write(self.style.NOTICE(f"⚙️ Processando e indexando no PostgreSQL/PGVector..."))

        indexer = KnowledgeIndexer()
        chunks_count = indexer.index_documents(
            documents=raw_docs,
            pillar=pillar,
            title=title,
            url=url,
            document_type=doc_type,
            source_file=file_path,
            original_filename=file_path.name,
        )

        doc_record = KnowledgeDocument.objects.filter(title=title, pillar=pillar).first()
        storage_info = f"   - Pasta dos arquivos: {doc_record.storage_dir}\n" if doc_record and doc_record.storage_dir else ""

        if chunks_count == 0:
            self.stdout.write(
                self.style.WARNING(
                    f"\n⚡ Documento '{title}' no pilar [{pillar}] já estava atualizado (hash de conteúdo inalterado).\n"
                    f"{storage_info}"
                    f"   - Metadados verificados/atualizados.\n"
                    f"   - Vetorização ignorada (0 custo de embeddings / 0 duplicatas)."
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f"\n🎉 Sucesso! Documento '{title}' indexado no pilar [{pillar}].\n"
                    f"{storage_info}"
                    f"   - Total de fragmentos vetorizados: {chunks_count}\n"
                    f"   - Banco vetorial (pgvector): Atualizado com sucesso!"
                )
            )
