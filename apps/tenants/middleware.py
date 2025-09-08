# backend/apps/tenants/middleware.py
from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin
import logging
from django.db import connection
from apps.tenants.models import ClienteDomain

logger = logging.getLogger(__name__)

class ValidateTenantHostMiddleware(MiddlewareMixin):
    def process_request(self, request):
        print("🔗 Validating tenant host in backend/apps/tenants/middleware.py...")
        print("🏢 Tenant backend/apps/tenants/middleware.py :", getattr(request, 'tenant', None))
        print("🌐 Host backend/apps/tenants/middleware.py:", request.get_host())
        
        host = request.get_host().split(':')[0] 

        if not ClienteDomain.objects.filter(domain=host).exists():
            return JsonResponse(
                {"detail": "Domínio inválido ou não autorizado."},
                status=403
            )


class TenantRequestLoggingMiddleware(MiddlewareMixin):
    def process_request(self, request):
        tenant = connection.tenant
        auth_header = request.headers.get("Authorization", "NoAuth")
        user = getattr(request, 'user', None)

        logger.info(
            f"[TENANT: {tenant.schema_name}] "
            f"[DOMAIN: {request.get_host()}] "
            f"[AUTH HEADER: {auth_header}] "
            f"[USER: {user}] "
            f"[METHOD: {request.method}] "
            f"[PATH: {request.path}]"
        )

