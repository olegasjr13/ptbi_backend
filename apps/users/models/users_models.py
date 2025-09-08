from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models
from django.db import connection

from apps.empresa.models import Empresa
from apps.tenants.models import Cliente


class CustomUser(AbstractUser):
    cliente = models.ForeignKey(Cliente, on_delete=models.PROTECT)
    empresas = models.ManyToManyField(Empresa, through='UsuarioEmpresa')

    def __str__(self):
        return self.username

    @property
    def tenant(self):
        return self.cliente

    def save(self, *args, **kwargs):
        """
        Salva o usuário com validação opcional.

        - Por padrão, executa `full_clean()` para garantir integridade.
        - Use `skip_clean=True` nos kwargs para pular validações (ex: durante testes ou pre-save incompleto).
        """
        skip_clean = kwargs.pop("skip_clean", False)

        if not self.cliente:
            raise ValidationError(_("Campo 'cliente' é obrigatório."))

        # Só realiza validação se o objeto já tiver um ID (evita problemas com M2M) e não for ignorada explicitamente
        if not skip_clean and self.pk:
            self.full_clean()

        super().save(*args, **kwargs)


    def clean(self):
        """
        Valida que o usuário está sendo salvo dentro do tenant correto.
        """
        from django.db import connection
        print("DEBUG clean(): schema atual:", connection.schema_name)
        print("DEBUG clean(): cliente.schema_name:", self.cliente.schema_name if self.cliente else None)

        tenant = getattr(connection, "tenant", None)
        if tenant is None:
            raise ValidationError(_("Não foi possível identificar o tenant atual."))

        if self.empresas and getattr(self.empresas, "cliente", None) != tenant:
            raise ValidationError("Usuário não pode ser criado fora do seu tenant atual.")


class UsuarioEmpresa(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE)

    class Meta:
        unique_together = ("user", "empresa")
