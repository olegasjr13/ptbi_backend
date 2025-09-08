from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.db import connection

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def teste_tenant_view(request):
    print("👤 User:", request.user)
    print("🪪 Auth:", request.auth)
    print("🔗 Schema:", connection.schema_name)
    print("🏢 Tenant:", getattr(request, "tenant", None))
    print("📡 Host recebido:", request.get_host())


    tenant = getattr(request, "tenant", None)
    return Response({
        "schema": connection.schema_name,
        "tenant": tenant.schema_name if tenant else None,
        "user": request.user.username if request.user else None,
        "auth": str(request.auth) if request.auth else None,
    })

