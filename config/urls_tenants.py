# config/urls_tenants.py

from django.urls import path, include
from apps.users.serializers.token import MyTokenObtainPairView, MyTokenRefreshView
from apps.users.views.testes_views import teste_tenant_view

urlpatterns = [
    path("api/token/", MyTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", MyTokenRefreshView.as_view(), name="token_refresh"),
    path("teste-tenant/", teste_tenant_view, name="teste-tenant"),
    path("api/funcionarios/", include("apps.funcionarios.urls")),
]
