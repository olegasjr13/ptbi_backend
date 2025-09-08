from django.db import models
from apps.setup.models.base_model import BaseModel

class Funcionario(BaseModel):
    name = models.CharField(max_length=250)
    email = models.EmailField(null=True, blank=True)
    telefone = models.CharField(max_length=20, null=True, blank=True)
    observacao = models.CharField(max_length=250, blank=True, null=True)

    class Meta:
        db_table = 'funcionarios'
        verbose_name = 'Funcionário'
        verbose_name_plural = 'Funcionários'

    def __str__(self):
        return self.name

