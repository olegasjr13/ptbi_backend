from django.db import models
from apps.tenants.models import Cliente

class Empresa(models.Model):
    nome_fantasia = models.CharField(max_length=100)
    cnpj = models.CharField(max_length=18, unique=True)
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='empresas')

    def __str__(self):
        return self.nome_fantasia

