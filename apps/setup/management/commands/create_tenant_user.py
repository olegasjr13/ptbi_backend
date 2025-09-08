from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django_tenants.utils import schema_context

User = get_user_model()

class Command(BaseCommand):
    help = 'Cria um usuário dentro de um tenant específico'

    def add_arguments(self, parser):
        parser.add_argument('schema', type=str, help='Nome do schema do tenant')
        parser.add_argument('username', type=str)
        parser.add_argument('password', type=str)

    def handle(self, *args, **options):
        schema = options['schema']
        with schema_context(schema):
            if not User.objects.filter(username=options['username']).exists():
                User.objects.create_user(
                    username=options['username'],
                    password=options['password']
                )
                self.stdout.write(self.style.SUCCESS(f"Usuário criado com sucesso em {schema}"))
            else:
                self.stdout.write(self.style.WARNING(f"Usuário já existe em {schema}"))

