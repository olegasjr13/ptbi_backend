from rest_framework import serializers
from apps.funcionarios.models import Funcionario

class FuncionarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Funcionario
        fields = ['id', 'name', 'email', 'telefone', 'observacao', 'created_at', 'updated_at']
