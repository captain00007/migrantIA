from django.contrib import admin
from .models import KnowledgeDocument


@admin.register(KnowledgeDocument)
class KnowledgeDocumentAdmin(admin.ModelAdmin):
    list_display = ('title', 'pillar', 'document_type', 'source', 'updated_at')
    list_filter = ('pillar', 'document_type', 'source')
    search_fields = ('title', 'url', 'content_hash')
    readonly_fields = ('created_at', 'updated_at')
