#!/bin/bash

if [ -z "$PORT" ]; then
  echo "ERROR: Port not specified."
  exit 1
fi

while ! ncat -z $POSTGRES_HOST $POSTGRES_PORT; do
  echo "🟡 Waiting for Postgres Database Startup ($POSTGRES_HOST $POSTGRES_PORT) ..."
  sleep 2
done

echo "✅ Postgres Database Started Successfully ($POSTGRES_HOST:$POSTGRES_PORT)"

python3 manage.py collectstatic --dry-run --noinput
python3 manage.py runserver 0.0.0.0:$PORT
