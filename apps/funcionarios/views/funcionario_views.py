from apps.funcionarios.models.funcionario_models import Funcionario
from apps.funcionarios.serializers.funcionario_serializers import FuncionarioSerializer
from rest_framework import viewsets
from apps.users.permissions import IsAuthenticatedAndInTenant
from rest_framework.permissions import IsAuthenticated

class FuncionarioViewSet(viewsets.ModelViewSet):
    queryset = Funcionario.objects.all()
    serializer_class = FuncionarioSerializer
    permission_classes = [IsAuthenticated, IsAuthenticatedAndInTenant]

