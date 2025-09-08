# config/urls_public.py

from django.contrib import admin
from django.urls import path
from apps.users.serializers.token import MyTokenObtainPairView, MyTokenRefreshView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/token/", MyTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", MyTokenRefreshView.as_view(), name="token_refresh"),
]
