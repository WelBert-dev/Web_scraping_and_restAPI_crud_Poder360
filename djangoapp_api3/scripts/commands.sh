#!/bin/sh

# O shell irá encerrar a execução do script quando um comando falhar
set -e

# Fica travado aqui enquanto o postgre não iniciar
while ! nc -z $POSTGRES_HOST $POSTGRES_PORT; do
  echo "🟡 Waiting for Postgres Database Startup ($POSTGRES_HOST $POSTGRES_PORT) ..."
  sleep 2
done

echo "✅ Postgres Database Started Successfully ($POSTGRES_HOST:$POSTGRES_PORT)"

python manage.py collectstatic --dry-run --noinput
python manage.py runserver 0.0.0.0:8003
