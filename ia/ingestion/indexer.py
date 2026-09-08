import os
from typing import Dict, Any, List, Optional
from django.db import transaction

# Setup models
from apps.sources.models import (
    WhitelistDomain,
    OfficialSource,
    CommunityPartner,
    PillarChoices
)
from apps.knowledge.models import KnowledgeDocument, DocumentChunk
from ia.embeddings.service import get_embedding_service
from ia.ingestion.splitter import LegalDocumentSplitter, BaseDocumentSplitter
from ia.ingestion.corpus import (
    INITIAL_WHITELIST_DOMAINS,
    INITIAL_COMMUNITY_PARTNERS,
    CURATED_PILLAR_DOCUMENTS
)


class KnowledgeIndexer:
    """
    Orquestrador de indexação no PostgreSQL com pgvector para os 4 Pilares do MigrantIA.
    """
    def __init__(self, splitter: Optional[BaseDocumentSplitter] = None):
        self.embedding_service = get_embedding_service()
        self.splitter = splitter or LegalDocumentSplitter()

    def sync_whitelist_domains(self) -> Dict[str, WhitelistDomain]:
        """
        Garante que os domínios oficiais homologados estejam cadastrados no banco.
        """
        domains_map = {}
        for item in INITIAL_WHITELIST_DOMAINS:
            domain_obj, created = WhitelistDomain.objects.get_or_create(
                domain=item['domain'],
                defaults={
                    'organization_name': item['organization_name'],
                    'is_active': True
                }
            )
            domains_map[item['domain']] = domain_obj
            if created:
                print(f"[Whitelist] Domínio homologado criado: {domain_obj.domain}")
        return domains_map

    def sync_community_partners(self):
        """
        Popula o diretório de organizações de apoio comunitário e jurídico aos migrantes.
        """
        for item in INITIAL_COMMUNITY_PARTNERS:
            partner, created = CommunityPartner.objects.update_or_create(
                name=item['name'],
                defaults=item
            )
            if created:
                print(f"[Parceiro] Cadastrado: {partner.name}")

    @transaction.atomic
    def index_curated_corpus(self, domains_map: Dict[str, WhitelistDomain]) -> int:
        """
        Ingere, divide em chunks, gera embeddings e indexa no pgvector
        todos os documentos oficiais dos 4 Pilares de Conhecimento.
        """
        total_indexed_chunks = 0

        for doc_data in CURATED_PILLAR_DOCUMENTS:
            domain_str = doc_data.get('domain_str', 'gov.br')
            domain_obj = domains_map.get(domain_str) or WhitelistDomain.objects.first()

            # Cria ou obtém a Fonte Oficial
            source_obj, _ = OfficialSource.objects.get_or_create(
                url=doc_data['url'],
                defaults={
                    'domain': domain_obj,
                    'name': doc_data['title'],
                    'pillar': doc_data['pillar'],
                    'description': f"Fonte oficial do pilar {doc_data['pillar']}"
                }
            )

            # Cria ou atualiza o Documento de Conhecimento
            doc_obj, _ = KnowledgeDocument.objects.update_or_create(
                title=doc_data['title'],
                defaults={
                    'source': source_obj,
                    'pillar': doc_data['pillar'],
                    'document_type': doc_data['document_type'],
                    'url': doc_data['url']
                }
            )

            # Limpa chunks anteriores do documento para reindexação limpa
            doc_obj.chunks.all().delete()

            # Chunking do documento
            doc_meta = {
                'document_id': doc_obj.id,
                'title': doc_obj.title,
                'pillar': doc_obj.pillar,
                'url': doc_obj.url,
                'document_type': doc_obj.document_type
            }
            chunks_data = self.splitter.split_text(doc_data['content'], metadata=doc_meta)

            # Extrai os textos para gerar embeddings em lote
            texts = [c['content'] for c in chunks_data]
            embeddings = self.embedding_service.embed_documents(texts)

            # Cria os chunks com vetores no banco
            chunk_objs = []
            for c_data, emb in zip(chunks_data, embeddings):
                chunk_objs.append(
                    DocumentChunk(
                        document=doc_obj,
                        content=c_data['content'],
                        embedding=emb,
                        chunk_index=c_data['chunk_index'],
                        metadata=c_data['metadata']
                    )
                )

            DocumentChunk.objects.bulk_create(chunk_objs)
            total_indexed_chunks += len(chunk_objs)
            print(f"[Indexado] '{doc_obj.title}' -> {len(chunk_objs)} chunks no pgvector.")

        return total_indexed_chunks

    def verify_vector_search(self, sample_query: str = "Como emitir o CPF para haitianos no Brasil?"):
        """
        Executa uma consulta por similaridade de cosseno diretamente no PostgreSQL pgvector
        para verificar a precisão do índice.
        """
        from pgvector.django import CosineDistance

        print(f"\n--- [TESTE DE BUSCA VETORIAL NO PGVECTOR] ---")
        print(f"Pergunta de teste: '{sample_query}'")
        
        query_vector = self.embedding_service.embed_query(sample_query)
        
        # Consulta com operador de distância de cosseno (<=>) no pgvector
        results = (
            DocumentChunk.objects
            .annotate(distance=CosineDistance('embedding', query_vector))
            .order_by('distance')[:3]
        )

        for rank, chunk in enumerate(results, 1):
            similarity_score = 1.0 - float(chunk.distance) if chunk.distance is not None else 0.0
            print(f"\nResultado #{rank} | Similaridade: {similarity_score:.4f} | Documento: {chunk.document.title}")
            print(f"Trecho: {chunk.content[:200]}...")

        return results

    def run(self):
        """
        Execução completa da esteira de indexação.
        """
        print("=== INICIANDO INDEXAÇÃO DOS QUATRO PILARES NO PGVECTOR ===")
        domains_map = self.sync_whitelist_domains()
        self.sync_community_partners()
        total_chunks = self.index_curated_corpus(domains_map)
        print(f"\nSucesso: {total_chunks} fragmentos indexados no banco vetorial.")
        self.verify_vector_search()
        print("=== INDEXAÇÃO CONCLUÍDA COM SUCESSO! ===")
