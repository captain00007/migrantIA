from django.db import models
from apps.sources.models import OfficialSource, PillarChoices


class DocumentTypeChoices(models.TextChoices):
    LAW = 'LAW', 'Lei Federal'
    DECREE = 'DECREE', 'Decreto Presidencial'
    PORTARIA = 'PORTARIA', 'Portaria Ministerial / Interministerial'
    GUIDE = 'GUIDE', 'Guia / Manual Oficial'
    CARTILHA = 'CARTILHA', 'Cartilha de Orientação'
    FAQ = 'FAQ', 'Perguntas Frequentes Homologadas'


class KnowledgeDocument(models.Model):
    """
    Catálogo e metadados de documentos oficiais indexados no MigrantIA.
    Os fragmentos textuais (chunks) e vetores de embeddings sÃo gerenciados
    diretamente pelo PGVector no PostgreSQL (vectorstore).
    """
    title = models.CharField(max_length=500)
    source = models.ForeignKey(
        OfficialSource,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='documents'
    )
    pillar = models.CharField(
        max_length=30,
        choices=PillarChoices.choices,
        db_index=True
    )
    document_type = models.CharField(
        max_length=30,
        choices=DocumentTypeChoices.choices,
        default=DocumentTypeChoices.GUIDE
    )
    url = models.URLField(max_length=1000, blank=True, default='')
    content_hash = models.CharField(max_length=64, blank=True, default='', db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Documento de Conhecimento'
        verbose_name_plural = 'Documentos de Conhecimento'
        ordering = ['pillar', 'title']

    def __str__(self):
        return f"[{self.get_pillar_display()}] {self.title}"
