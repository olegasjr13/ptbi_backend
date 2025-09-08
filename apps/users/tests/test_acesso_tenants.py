import uuid
import pytest
from apps.empresa.models.empresa_models import Empresa
from apps.tenants.models import Cliente, ClienteDomain
from apps.users.models.users_models import CustomUser
from apps.setup.utils.gerar_cnpj_valido import gerar_cnpj_valido
from rest_framework.test import APIClient
from django_tenants.utils import schema_context
from django.db import connection


@pytest.mark.django_db(transaction=True)
def test_usuario_so_acessa_seu_tenant():
    client = APIClient()

    def criar_tenant_e_usuario(schema_suffix: str, criar_user=False):
        schema_uuid = uuid.uuid4().hex[:8]
        schema_name = f"tenant_{schema_suffix}_{schema_uuid}"
        domain = f"{schema_suffix}-{schema_uuid}.test.com"

        tenant = Cliente.objects.create(
            schema_name=schema_name,
            nome=f"Tenant {schema_suffix}",
            domain_url=domain
        )
        tenant.create_schema(check_if_exists=True)
        ClienteDomain.objects.create(domain=domain, tenant=tenant, is_primary=True)

        if criar_user:
            with schema_context(schema_name):
                empresa = Empresa.objects.create(
                    nome_fantasia=f"Empresa {schema_suffix}",
                    cliente=tenant,
                    cnpj=gerar_cnpj_valido(),
                )
                user = CustomUser.objects.create_user(
                    username="usuario_teste",
                    email="teste@exemplo.com",
                    password="senha123",
                    cliente=tenant,
                )
                user.empresas.add(empresa)
                print(f"✅ Usuário criado no schema: {schema_name}")
                return tenant, domain, user

        return tenant, domain, None

    # 🔹 Cria tenant_1 com usuário
    tenant1, domain1, user1 = criar_tenant_e_usuario("um", criar_user=True)

    # 🔹 Cria tenant_2 sem usuário
    tenant2, domain2, _ = criar_tenant_e_usuario("dois", criar_user=False)

    # 🔹 Login no tenant correto (tenant_1)
    client.credentials(HTTP_HOST=domain1)
    print(f"\n🌐 Tentando login no domínio CORRETO: {domain1}")
    response_ok = client.post("/api/token/", {
        "username": "usuario_teste",
        "password": "senha123"
    }, format="json")

    print("🔎 URL usada na requisição: /api/token/")
    print("🔎 Schema ativo:", connection.schema_name)
    print("🔎 Headers:", {"HTTP_HOST": domain1})
    print("📥 Status code esperado 200 → Recebido:", response_ok.status_code)
    print("📥 Response:", response_ok.json() if response_ok.status_code == 200 else response_ok.content)

    assert response_ok.status_code == 200
    assert "access" in response_ok.data
    assert "refresh" in response_ok.data

    # 🔹 Login no tenant ERRADO (tenant_2)
    client.credentials(HTTP_HOST=domain2)
    print(f"\n🌐 Tentando login no domínio ERRADO: {domain2}")
    response_erro = client.post("/api/token/", {
        "username": "usuario_teste",
        "password": "senha123"
    }, format="json")

    print("🔎 Schema ativo:", connection.schema_name)
    print("📥 Status code esperado diferente de 200 → Recebido:", response_erro.status_code)
    print("📥 Response:", response_erro.content)

    assert response_erro.status_code != 200
