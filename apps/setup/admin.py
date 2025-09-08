from django.contrib import admin
from django_tenants.utils import get_tenant_model
from django.db import connection

class AdminTenantMixin(admin.ModelAdmin):
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if hasattr(connection, 'tenant'):
            return qs.using(connection.schema_name)
        return qs

