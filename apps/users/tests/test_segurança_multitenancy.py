import pytest
from apps.tenants.models import Cliente, ClienteDomain
from apps.users.models.users_models import CustomUser
from django_tenants.utils import schema_context


@pytest.mark.django_db(transaction=True)
def test_usuario_nao_acessa_dados_de_outro_tenant():
    # Criar tenants dentro do schema PUBLIC
    with schema_context("public"):
        tenant_um = Cliente.objects.create(schema_name="tenant_um", nome="Tenant Um", paid_until="2099-12-31")
        ClienteDomain.objects.create(domain="tenantum.test.com", cliente=tenant_um, is_primary=True)

        tenant_dois = Cliente.objects.create(schema_name="tenant_dois", nome="Tenant Dois", paid_until="2099-12-31")
        ClienteDomain.objects.create(domain="tenantdois.test.com", cliente=tenant_dois, is_primary=True)

    # Criar usuários em schemas diferentes
    with schema_context("tenant_um"):
        CustomUser.objects.create_user(username="user_um", password="123", cliente=tenant_um)

    with schema_context("tenant_dois"):
        CustomUser.objects.create_user(username="user_dois", password="456", cliente=tenant_dois)

    # Validar que não há vazamento de dados
    with schema_context("tenant_um"):
        usernames = list(CustomUser.objects.values_list("username", flat=True))
        print(f"🔍 SCHEMA: tenant_um | USERS: {usernames}")
        assert "user_um" in usernames
        assert "user_dois" not in usernames

    with schema_context("tenant_dois"):
        usernames = list(CustomUser.objects.values_list("username", flat=True))
        print(f"🔍 SCHEMA: tenant_dois | USERS: {usernames}")
        assert "user_dois" in usernames
        assert "user_um" not in usernames
