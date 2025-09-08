from django.db import models
from django.core.exceptions import ValidationError
from django_tenants.models import TenantMixin, DomainMixin
from django.utils import timezone

class Cliente(TenantMixin):
    nome = models.CharField("Nome da Empresa", max_length=100)
    criado_em = models.DateField("Data de Criação", default=timezone.now)
    atualizado_em = models.DateTimeField("Última Atualização", auto_now=True)
    is_active = models.BooleanField("Ativo", default=True)
    paid_until = models.DateField("Pago até", default="2099-12-31")
    on_trial = models.BooleanField("Em período de teste", default=False)
    domain_url = models.CharField("URL do Domínio", max_length=100, unique=True, default="placeholder.example.com")
    

    # Cria o schema automaticamente ao salvar
    auto_create_schema = True

    class Meta:
        verbose_name = "Cliente"
        verbose_name_plural = "Clientes"
        ordering = ["-criado_em"]

    def __str__(self):
        return self.nome


class ClienteDomain(DomainMixin):
    class Meta:
        verbose_name = "Domínio do Cliente"
        verbose_name_plural = "Domínios dos Clientes"
        ordering = ["-id"]

    def __str__(self):
        return self.domain

    def clean(self):
        # Impede criação de domínio duplicado
        if ClienteDomain.objects.exclude(pk=self.pk).filter(domain=self.domain).exists():
            raise ValidationError("Já existe um domínio com esse endereço.")

    def save(self, *args, **kwargs):
        self.full_clean()  # chama o clean() antes de salvar
        super().save(*args, **kwargs)
