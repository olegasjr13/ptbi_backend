# apps/users/middleware.py
from django.db import connection
from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin
from django_tenants.utils import get_tenant_domain_model
import logging
logger = logging.getLogger(__name__)

class TenantAccessSecurityMiddleware(MiddlewareMixin):
    def process_request(self, request):
        print("🪪 Token recebido apps/users/middleware.py:", request.headers.get("Authorization"))
        print("🏢 Tenant atual apps/users/middleware.py:", getattr(request, 'tenant', None))

        print("🧑‍💻 Middleware request.user antes apps/users/middleware.py:", getattr(request, 'user', None))
        print("🔐 Middleware request.auth antes apps/users/middleware.py:", getattr(request, 'auth', None))

        print("🧩 [Middleware Segurança] Schema:", connection.schema_name)
        print("🧩 [Middleware Segurança] Host:", request.get_host())


        user = request.user
        tenant = getattr(request, 'tenant', None)

        # Ignorar validação para paths públicos
        PUBLIC_PATHS = [
            '/admin/', '/api/token/', '/api/login/', '/api/refresh/', '/api/logout/', '/health/'
        ]
        if any(request.path.startswith(path) for path in PUBLIC_PATHS):
            return

        if not tenant:
            logger.warning(f"Tentativa sem tenant válido: host={request.get_host()}, path={request.path}")
            return JsonResponse({'detail': 'Tenant inválido.'}, status=400)
        


        domain_model = get_tenant_domain_model()
        host = request.get_host().split(':')[0]
        domain = domain_model.objects.filter(domain=host).first()

        if not domain:
            return JsonResponse({'detail': 'Domínio não autorizado.'}, status=403)

        if not user.is_authenticated:
            return JsonResponse({'detail': 'Autenticação necessária.'}, status=401)

        # Se o usuário pertence a outro tenant
        if hasattr(user, 'empresas') and not user.empresas.filter(tenant=tenant).exists():
            logger.warning(f"Tentativa de acesso indevido: usuário {user.id} tentou acessar tenant {tenant.schema_name}")
            return JsonResponse({'detail': 'Acesso negado a este tenant.'}, status=403)
        

