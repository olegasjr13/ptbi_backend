# tests/test_tenant_middleware.py
import pytest
from django.contrib.auth import get_user_model
from apps.tenants.models import Cliente, ClienteDomain
from apps.empresa.models.empresa_models import Empresa
from apps.setup.utils.gerar_cnpj_valido import gerar_cnpj_valido
from django_tenants.utils import schema_context
from rest_framework.test import APIClient

import uuid


@pytest.mark.django_db(transaction=True)
def test_middleware_define_request_tenant():
    client = APIClient()
    User = get_user_model()

    schema_uuid = uuid.uuid4().hex[:8]
    schema_name = f"tenant_test_{schema_uuid}"
    domain = f"{schema_uuid}.example.com"

    # Criação do tenant
    tenant = Cliente.objects.create(
        schema_name=schema_name,
        nome="Tenant Teste",
        domain_url=domain
    )
    tenant.create_schema(check_if_exists=True)

    ClienteDomain.objects.create(
        domain=domain,
        tenant=tenant,
        is_primary=True
    )

    # Criação de usuário e empresa dentro do tenant
    with schema_context(schema_name):
        empresa = Empresa.objects.create(
            nome_fantasia="Empresa do Tenant",
            cnpj="12345678000100",
            cliente=tenant
        )

        user = User.objects.create_user(
            username="usuario_teste",
            email="teste@exemplo.com",
            password="senha123",
            cliente=tenant
        )
        user.empresas.add(empresa)

    # Realiza login e obtém token JWT
    client.credentials(HTTP_HOST=domain)
    login_response = client.post("/api/token/", {
        "username": "usuario_teste",
        "password": "senha123"
    }, format="json")

    print("🔑 Login response status:", login_response.status_code)
    print("🔑 Login response data:", login_response.json())

    if login_response.status_code != 200:
        pytest.fail(f"❌ Falha no login: {login_response.status_code} - {login_response.content}")

    access_token = login_response.data.get("access")
    assert access_token, "❌ Token de acesso não retornado."

    # Define o token no header
    client.credentials(
        HTTP_AUTHORIZATION=f"Bearer {access_token}",
        HTTP_HOST=domain
    )

    print("🪪 Token enviado:", access_token)
    print("🧪 Header enviado:", client._credentials)

    # Faz a requisição autenticada
    response = client.get("/api/teste-tenant/")
    print("📥 Protected endpoint response:", response.status_code, response.json())

    assert response.status_code == 200
    assert response.json()["schema"] == schema_name
    assert response.json()["tenant"] == schema_name

