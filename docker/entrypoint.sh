#!/bin/sh
set -e  # Encerra o script caso algum comando falhe

echo "🚀 Aguardando banco de dados em $DB_HOST:$DB_PORT..."

# Aguarda até que o banco esteja acessível
while ! nc -z "$DB_HOST" "$DB_PORT"; do
  echo "⏳ Aguardando $DB_HOST:$DB_PORT..."
  sleep 1
done

echo "✅ Banco de dados disponível!"

# Define dinamicamente o módulo de settings
export DJANGO_SETTINGS_MODULE="config.settings.${DJANGO_ENV:-dev}"
echo "⚙️ Ambiente: ${DJANGO_ENV:-dev}"
echo "📂 DJANGO_SETTINGS_MODULE: $DJANGO_SETTINGS_MODULE"

# Aplica migrações em ambiente de desenvolvimento apenas
if [ "$DJANGO_ENV" = "dev" ]; then
  echo "🛠️ Ambiente de desenvolvimento detectado: aplicando migrações..."
  python manage.py makemigrations --noinput
  python manage.py migrate_schemas --shared --noinput
fi

echo "🚀 Executando comando: "
exec "$@"


