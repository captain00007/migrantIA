import pytest
from apps.sources.models import WhitelistDomain, OfficialSource, PillarChoices
from apps.knowledge.models import KnowledgeDocument, DocumentTypeChoices

pytestmark = pytest.mark.django_db


def test_knowledge_document_creation():
    domain = WhitelistDomain.objects.create(
        domain='gov.br',
        organization_name='Governo Federal'
    )
    source = OfficialSource.objects.create(
        domain=domain,
        name='Polícia Federal',
        pillar=PillarChoices.IMMIGRATION,
        url='https://www.gov.br/pf'
    )
    doc = KnowledgeDocument.objects.create(
        title='Lei de Migração',
        source=source,
        pillar=PillarChoices.IMMIGRATION,
        document_type=DocumentTypeChoices.LAW,
        url='https://www.planalto.gov.br/lei13445',
        content_hash='abcdef123456'
    )

    assert doc.id is not None
    assert doc.title == 'Lei de Migração'
    assert doc.source == source
    assert 'Imigração' in str(doc)
