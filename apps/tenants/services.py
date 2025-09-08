# apps/tenants/services.py

from django_tenants.utils import schema_context
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from apps.tenants.models import Cliente, ClienteDomain


def criar_cliente(nome: str, dominio: str) -> Cliente:
    """
    Cria um novo tenant (Cliente) com domínio associado, validando conflitos e garantindo atomicidade.

    Args:
        nome (str): Nome do cliente.
        dominio (str): Nome do subdomínio, sem ".meudominio.com.br".

    Returns:
        Cliente: Instância do tenant criado.

    Raises:
        ValidationError: Se já existir um cliente ou domínio com o mesmo schema.
        IntegrityError: Se houver erro de banco de dados ao criar cliente ou domínio.
    """
    schema_name = dominio.lower()
    full_domain = f"{schema_name}.meudominio.com.br"

    # Verifica duplicidade de schema ou domínio
    if Cliente.objects.filter(schema_name=schema_name).exists():
        raise ValidationError(f"Já existe um cliente com o schema '{schema_name}'")

    if ClienteDomain.objects.filter(domain=full_domain).exists():
        raise ValidationError(f"O domínio '{full_domain}' já está em uso.")

    try:
        with transaction.atomic():
            cliente = Cliente.objects.create(
                nome=nome,
                dominio=dominio,
                schema_name=schema_name,
            )

            ClienteDomain.objects.create(
                domain=full_domain,
                tenant=cliente,
                is_primary=True,
            )
    except IntegrityError as e:
        raise IntegrityError(f"Erro ao criar cliente ou domínio: {e}")

    return cliente
