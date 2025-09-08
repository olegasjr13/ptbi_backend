import pytest
from django_tenants.test.cases import TenantTestCase
from django.contrib.auth import get_user_model

User = get_user_model()

@pytest.mark.django_db
class TestTokenTenantAuth(TenantTestCase):
    def setUp(self):
        super().setUp()
        self.user = User.objects.create_user(username="tenantuser", password="test123")

    def test_user_creation(self):
        assert User.objects.count() == 1
        assert self.user.username == "tenantuser"
