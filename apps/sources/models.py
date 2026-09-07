from django.db import models

class PillarChoices(models.TextChoices):
    IMMIGRATION = 'IMMIGRATION', 'Imigração e Regularização'
    EDUCATION = 'EDUCATION', 'Estudo e Educação'
    NATIONALITY = 'NATIONALITY', 'Nacionalidade e Naturalização'
    COMMUNITY = 'COMMUNITY', 'Comunidades e Apoio aos Haitianos'


class WhitelistDomain(models.Model):
    """
    Domínios estritamente homologados pela governança constitucional do MigrantIA.
    Qualquer busca externa ou indexação web DEVE pertencer a um destes domínios.
    """
    domain = models.CharField(max_length=255, unique=True, db_index=True)
    organization_name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Domínio Homologado'
        verbose_name_plural = 'Domínios Homologados (Whitelist)'
        ordering = ['domain']

    def __str__(self):
        return f"{self.domain} ({self.organization_name})"


class OfficialSource(models.Model):
    """
    Fontes oficiais e páginas governamentais/ONGs cadastradas por pilar temático.
    """
    domain = models.ForeignKey(
        WhitelistDomain,
        on_delete=models.CASCADE,
        related_name='sources'
    )
    name = models.CharField(max_length=255)
    url = models.URLField(max_length=1000, unique=True)
    pillar = models.CharField(
        max_length=30,
        choices=PillarChoices.choices,
        default=PillarChoices.IMMIGRATION,
        db_index=True
    )
    authority_level = models.CharField(max_length=100, default='FEDERAL')
    description = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Fonte Oficial'
        verbose_name_plural = 'Fontes Oficiais'
        ordering = ['pillar', 'name']

    def __str__(self):
        return f"[{self.get_pillar_display()}] {self.name}"


class PartnerTypeChoices(models.TextChoices):
    LEGAL = 'LEGAL', 'Assistência Jurídica Gratuita'
    RECEPTION = 'RECEPTION', 'Acolhimento e Assistência Social'
    EDUCATIONAL = 'EDUCATIONAL', 'Cursos e Educação'
    COMMUNITY = 'COMMUNITY', 'Associação Comunitária'


class CommunityPartner(models.Model):
    """
    Diretório de organizações da sociedade civil, postos da DPU e associações de apoio aos haitianos.
    """
    name = models.CharField(max_length=255)
    partner_type = models.CharField(
        max_length=30,
        choices=PartnerTypeChoices.choices,
        default=PartnerTypeChoices.RECEPTION,
        db_index=True
    )
    city = models.CharField(max_length=100, blank=True, default='')
    state = models.CharField(max_length=10, blank=True, default='')
    address = models.CharField(max_length=255, blank=True, default='')
    phone = models.CharField(max_length=100, blank=True, default='')
    email = models.EmailField(blank=True, default='')
    website = models.URLField(blank=True, default='')
    languages_supported = models.JSONField(
        default=list,
        help_text="Lista de códigos de idiomas atendidos, ex: ['ht', 'fr', 'pt', 'en', 'es']"
    )
    services_description = models.TextField(blank=True, default='')
    is_verified = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Parceiro Comunitário / Órgão de Apoio'
        verbose_name_plural = 'Diretório de Parceiros Comunitários'
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.get_partner_type_display()}) - {self.city}/{self.state}"
