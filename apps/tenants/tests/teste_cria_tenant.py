import uuid
import pytest
from django.db import connection
from apps.tenants.models import Cliente, ClienteDomain
from django_tenants.utils import schema_context



@pytest.mark.django_db(transaction=True)
def test_criacao_completa_de_tenant():
    schema_uuid = uuid.uuid4().hex[:8]
    schema_name = f"tenant_{schema_uuid}"
    domain_name = f"{schema_uuid}.example.com"

    # 🔹 Verifica que o schema ainda não existe
    with connection.cursor() as cursor:
        cursor.execute("SELECT schema_name FROM information_schema.schemata WHERE schema_name = %s", [schema_name])
        assert cursor.fetchone() is None, "Schema já existia antes da criação do tenant."

    # 🔹 Cria o tenant
    tenant = Cliente.objects.create(
        schema_name=schema_name,
        nome="Tenant de Teste",
        domain_url=domain_name,  # usado como default
    )
    tenant.create_schema(check_if_exists=True)

    # 🔹 Cria o domínio
    domain = ClienteDomain.objects.create(domain=domain_name, tenant=tenant, is_primary=True)

    # 🔹 Verifica que o schema foi criado
    with connection.cursor() as cursor:
        cursor.execute("SELECT schema_name FROM information_schema.schemata WHERE schema_name = %s", [schema_name])
        assert cursor.fetchone() is not None, "Schema não foi criado corretamente."

    # 🔹 Verifica que o domínio está vinculado
    assert domain.tenant == tenant
    assert domain.is_primary

    # 🔹 Verifica se consegue trocar para o schema (sem erros)
    try:
        with schema_context(schema_name):
            # Aqui poderia testar algum model específico do tenant
            pass
    except Exception as e:
        pytest.fail(f"Erro ao trocar para schema {schema_name}: {e}")

    # 🔹 Limpa (apaga tenant e schema)
    tenant.delete(force_drop=True)

    # 🔹 Verifica que schema foi removido
    with connection.cursor() as cursor:
        cursor.execute("SELECT schema_name FROM information_schema.schemata WHERE schema_name = %s", [schema_name])
        assert cursor.fetchone() is None, "Schema ainda existe após exclusão."

    # 🔹 Verifica que o domínio foi removido junto
    assert not ClienteDomain.objects.filter(domain=domain_name).exists(), "Domínio não foi excluído corretamente."
