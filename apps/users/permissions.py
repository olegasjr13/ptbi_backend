# apps/users/permissions.py
from rest_framework.permissions import BasePermission
from django.db import connection

class IsAuthenticatedAndInTenant(BasePermission):
    """
    Permite acesso apenas a usuários autenticados do tenant atual.
    """
    def has_permission(self, request, view):
        user = request.user
        tenant = getattr(request, 'tenant', None)

        print("🚨 Verificando acesso do usuário ao tenant:")
        print("➡️ Usuário:", user)
        print("➡️ Autenticado:", user.is_authenticated)
        print("➡️ Tenant do request:", tenant)
        print("➡️ Empresa do usuário:", getattr(user, 'empresa', None))


        if not user or not user.is_authenticated or not tenant:
            return False

        if hasattr(user, 'empresas'):
            return tenant in [e.tenant for e in user.empresas.all()]
        elif hasattr(user, 'empresa'):
            return user.empresa.tenant == tenant

        return False

