import uuid
import pytest
from django.db import connection
from apps.users.models.users_models import CustomUser, UsuarioEmpresa
from apps.empresa.models.empresa_models import Empresa
from apps.tenants.models import Cliente, ClienteDomain
from apps.setup.utils.gerar_cnpj_valido import gerar_cnpj_valido
from django_tenants.utils import schema_context


@pytest.mark.django_db(transaction=True)
def test_criacao_usuario_com_empresa_em_tenant():
    # 🔹 Gera schema único
    schema_uuid = uuid.uuid4().hex[:8]
    schema_name = f"tenant_{schema_uuid}"
    domain_name = f"{schema_uuid}.test.com"

    # 🔹 Cria o tenant e o domínio
    tenant = Cliente.objects.create(
        schema_name=schema_name,
        nome="Tenant de Teste2",
        domain_url=domain_name,
    )
    tenant.create_schema(check_if_exists=True)
    ClienteDomain.objects.create(domain=domain_name, tenant=tenant, is_primary=True)
    print(f"✅ Tenant criado: {tenant.schema_name} | domínio: {domain_name}")

    # 🔹 Dentro do schema do tenant:
    with schema_context(schema_name):
        # 1. Cria uma empresa
        empresa = Empresa.objects.create(
            nome_fantasia="Empresa Exemplo",
            cliente=tenant,
            cnpj=gerar_cnpj_valido(),
        )
        print(f"✅ Empresa criada: {empresa.nome_fantasia} | CNPJ: {empresa.cnpj}")

        # 2. Cria um usuário vinculado ao tenant e à empresa
        user = CustomUser(
            username="usuario_teste",
            email="teste@exemplo.com",
            cliente=tenant,
        )
        user.set_password("teste123")
        user.save(skip_clean=True)
        UsuarioEmpresa.objects.create(user=user, empresa=empresa)
        print(f"✅ Usuário criado: {user.username} | Tenant: {user.cliente.schema_name}")

        # 3. Verifica existência e vínculos
        assert CustomUser.objects.count() == 1
        assert user.cliente == tenant
        assert user.empresas.count() == 1
        assert user.empresas.first() == empresa
        assert user.check_password("teste123")
        print("✅ Usuário vinculado à empresa corretamente.")
        # 🔹 Limpa o usuário antes de sair do schema
        user.delete()
        print(f"✅ Usuário {user.username} removido do schema {schema_name}")

    # 🔹 No schema public: usuário ainda estará listado (se não foi excluído no public)
    with schema_context("public"):
        assert CustomUser.objects.filter(username="usuario_teste").count() == 0
        print("✅ Usuário não está no schema public (como esperado).")
        
    # 🔹 Limpa tenant
    tenant.delete(force_drop=True)
    print(f"✅ Tenant {tenant.schema_name} removido com sucesso.")

    # 🔹 Confirma que o schema foi removido do banco
    with connection.cursor() as cursor:
        cursor.execute("SELECT schema_name FROM information_schema.schemata WHERE schema_name = %s", [schema_name])
        assert cursor.fetchone() is None, "Schema ainda existe após exclusão"
        print(f"✅ Schema {schema_name} removido do banco de dados.")