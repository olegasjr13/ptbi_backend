from rest_framework.permissions import BasePermission

class TenantAccessPermission(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        tenant = getattr(request, 'tenant', None)

        print("🔐 User:", user)
        print("✅ Authenticated:", user.is_authenticated if user else None)
        print("🏢 Tenant:", tenant)

        if not user or not user.is_authenticated or not tenant:
            print("❌ Acesso negado: falta de autenticação ou tenant")
            return False

        if hasattr(user, 'empresas'):
            permitido = tenant in [e.tenant for e in user.empresas.all()]
            print("📦 Empresas:", [e.tenant for e in user.empresas.all()])
            return permitido

        elif hasattr(user, 'empresa'):
            print("🏭 Empresa:", user.empresa.tenant if user.empresa else None)
            return user.empresa and user.empresa.tenant == tenant

        print("❌ Acesso negado: usuário sem vínculo de empresa")
        return False

