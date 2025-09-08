#!/bin/sh

set -e  # Interrompe em qualquer erro

echo "🟡 Aplicando migrações..."
python manage.py makemigrations --noinput

# Aplica migrações para todos os schemas (multi-tenant)
python manage.py migrate_schemas --shared --noinput

echo "🟢 Coletando arquivos estáticos..."
python manage.py collectstatic --noinput

echo "🚀 Iniciando servidor Gunicorn..."
exec gunicorn config.wsgi:application   --bind 0.0.0.0:8000   --workers 3   --log-level info   --access-logfile -   --error-logfile -
