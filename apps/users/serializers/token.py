# apps/users/serializers/token.py
import logging
from django.contrib.auth import authenticate
from django.db import connection
from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.serializers import (
    TokenObtainPairSerializer,
    TokenRefreshSerializer,
)
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from rest_framework_simplejwt.tokens import RefreshToken

logger = logging.getLogger(__name__)

def get_current_schema_name():
    return getattr(connection.tenant, 'schema_name', None)

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        request = self.context.get("request")
        if request is None:
            raise AuthenticationFailed("Request ausente no contexto")

        current_tenant = connection.tenant
        username = attrs.get("username")
        password = attrs.get("password")

        if username is None or password is None:
            raise AuthenticationFailed("Usuário ou senha não fornecidos")

        user = authenticate(request=request, username=username, password=password)

        if not user or not user.is_active:
            logger.warning(f"Tentativa de login inválido para usuário '{username}'")
            raise AuthenticationFailed("Credenciais inválidas ou usuário inativo")

        if not user.empresas.filter(cliente__schema_name=current_tenant.schema_name).exists():
            logger.warning(f"Usuário '{username}' tentou acessar tenant inválido '{current_tenant.schema_name}'")
            raise AuthenticationFailed("Usuário não pertence a este domínio")

        refresh = self.get_token(user)
        refresh["schema_name"] = current_tenant.schema_name

        data = {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "user": {
                "id": user.id,
                "nome": user.get_full_name(),
                "email": user.email,
            }
        }
        data["schema_name"] = connection.schema_name
        return data


class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer


class MyTokenRefreshSerializer(TokenRefreshSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)

        refresh = RefreshToken(attrs["refresh"])
        user_id = refresh.payload.get("user_id")
        token_schema = refresh.payload.get("schema_name")
        current_schema = get_current_schema_name()

        if not user_id:
            raise AuthenticationFailed("Token inválido")

        if not isinstance(token_schema, str):
            raise AuthenticationFailed("schema_name inválido no token")

        if token_schema != current_schema:
            logger.warning(f"Token de schema '{token_schema}' usado em tenant '{current_schema}'")
            raise AuthenticationFailed("Este token não pertence a este domínio")

        return data


class MyTokenRefreshView(TokenRefreshView):
    serializer_class = MyTokenRefreshSerializer
