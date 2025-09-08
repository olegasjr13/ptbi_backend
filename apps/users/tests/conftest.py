# apps/users/tests/conftest.py

import pytest
from apps.tenants.models import Cliente, ClienteDomain
from django_tenants.utils import schema_context



@pytest.fixture
def tenant_um(db):
    with schema_context("public"):
        cliente = Cliente.objects.create(
            nome="Tenant UM",
            schema_name="tenant_um",
            domain_url="tenantum.localhost"
        )
        ClienteDomain.objects.create(
            tenant=cliente,
            domain="tenantum.localhost"
        )

    yield cliente  # podemos usar `cliente` como referência no teste


@pytest.fixture
def tenant_dois(db):
    with schema_context("public"):
        cliente = Cliente.objects.create(
            nome="Tenant DOIS",
            schema_name="tenant_dois",
            domain_url="tenantdois.localhost"
        )
        ClienteDomain.objects.create(
            tenant=cliente,
            domain="tenantdois.localhost"
        )

    yield cliente
