import uuid
import pytest
import jwt
from django.conf import settings
from rest_framework.test import APIClient
from django_tenants.utils import schema_context
from apps.tenants.models import Cliente, ClienteDomain
from apps.empresa.models.empresa_models import Empresa
from apps.users.models.users_models import CustomUser
from apps.setup.utils.gerar_cnpj_valido import gerar_cnpj_valido


@pytest.mark.django_db(transaction=True)
def test_refresh_token_contem_schema_name():
    client = APIClient()

    # 🔹 Criação do tenant e usuário
    schema_uuid = uuid.uuid4().hex[:8]
    schema_name = f"tenant_um_{schema_uuid}"
    domain = f"um-{schema_uuid}.test.com"

    tenant = Cliente.objects.create(
        schema_name=schema_name,
        nome="Tenant Um",
        domain_url=domain
    )
    tenant.create_schema(check_if_exists=True)
    ClienteDomain.objects.create(domain=domain, tenant=tenant, is_primary=True)

    with schema_context(schema_name):
        empresa = Empresa.objects.create(
            nome_fantasia="Empresa Um",
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

    # 🔹 Login para obter o refresh token
    client.credentials(HTTP_HOST=domain)
    response = client.post("/api/token/", {
        "username": "usuario_teste",
        "password": "senha123"
    }, format="json")

    assert response.status_code == 200
    refresh_token = response.data["refresh"]
    assert refresh_token is not None

    # 🔹 Decodifica o token
    decoded_payload = jwt.decode(
        refresh_token,
        settings.SECRET_KEY,
        algorithms=["HS256"]
    )

    print("🧾 Payload do Refresh Token:", decoded_payload)

    # 🔹 Valida presença do schema_name
    assert "schema_name" in decoded_payload
    assert decoded_payload["schema_name"] == schema_name
