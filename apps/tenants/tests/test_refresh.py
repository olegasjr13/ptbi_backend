import pytest
from django.urls import reverse
from apps.empresa.models.empresa_models import Empresa
from rest_framework_simplejwt.tokens import RefreshToken
from django_tenants.test.cases import TenantTestCase
from django_tenants.test.client import TenantClient
from apps.tenants.models import Cliente
from django_tenants.utils import schema_context
from uuid import uuid4


class TestRefreshTokenPorTenant(TenantTestCase):

    @classmethod
    def setup_tenant(cls, tenant):
        """
        Criação do tenant principal (tenant de teste gerenciado pelo TenantTestCase)
        """
        tenant.nome = "Tenant A"
        tenant.domain_url = "tenant-a.testserver"
        tenant.paid_until = "2099-12-31"
        tenant.on_trial = False
        tenant.is_active = True
        tenant.save()

    @pytest.fixture(autouse=True)
    def setup(self, django_user_model):
        """
        Fixture que roda automaticamente antes de cada teste
        """
        # Identificadores únicos para evitar conflitos de chave
        unique_id = uuid4().hex[:8]

        self.schema_name_b = f"tenant_b_{unique_id}"
        self.domain_b = f"tenant-b-{unique_id}.testserver"
        self.email = f"usera_{unique_id}@example.com"
        self.username = f"usera_{unique_id}"
        self.cnpj = f"{unique_id[:8]:0<14}"

        # Criação do segundo tenant (Tenant B)
        with schema_context("public"):
            self.tenant_b = Cliente.objects.create(
                schema_name=self.schema_name_b,
                nome="Tenant B",
                domain_url=self.domain_b,
                paid_until="2099-12-31",
                on_trial=False,
                is_active=True,
            )

        # Criação da empresa e usuário no Tenant A
        with schema_context(self.tenant.schema_name):
            empresa_a = Empresa.objects.create(
                nome_fantasia="Empresa A1",
                cnpj=self.cnpj,
                cliente=self.tenant,
            )

            self.user_a = django_user_model.objects.create_user(
                username=self.username,
                password="senha123",
                email=self.email,
                cliente=self.tenant,
            )
            self.user_a.save(skip_clean=True)
            self.user_a.empresas.set([empresa_a])

        # Criação dos clients
        self.client_a = TenantClient(self.tenant)
        self.client_b = TenantClient(self.tenant_b)

    def login(self, client):
        url = reverse("token_obtain_pair")
        if not url.endswith("/"):
            url += "/"

        print("LOGIN URL:", url)

        response = client.post(
            url,
            {"username": self.username, "password": "senha123"},
            follow=False
        )

        print("LOGIN STATUS CODE:", response.status_code)
        print("LOGIN CONTENT:", response.content)

        assert response.status_code == 200, f"Erro ao logar: status {response.status_code}, content: {response.content}"
        return response.data

    def test_refresh_token_em_outro_tenant(self):
        """
        Tenta usar um refresh token válido do Tenant A no Tenant B (deve falhar)
        """
        tokens = self.login(self.client_a)
        refresh_token = tokens["refresh"]

        response = self.client_b.post(reverse("token_refresh"), {
            "refresh": refresh_token
        })

        assert response.status_code == 401
        assert "não pertence a este domínio" in response.data["detail"]

    def test_refresh_token_valido_mesmo_tenant(self):
        """
        Usa refresh token dentro do tenant correto (deve funcionar)
        """
        tokens = self.login(self.client_a)
        response = self.client_a.post(reverse("token_refresh"), {
            "refresh": tokens["refresh"]
        })

        assert response.status_code == 200
        assert "access" in response.data

    def test_refresh_token_sem_schema(self):
        """
        Testa token inválido (sem schema_name no payload)
        """
        token = RefreshToken.for_user(self.user_a)
        token.payload.pop("schema_name", None)

        response = self.client_a.post(reverse("token_refresh"), {
            "refresh": str(token)
        })

        assert response.status_code == 401
        assert "Token inválido ou corrompido" in response.data["detail"]
