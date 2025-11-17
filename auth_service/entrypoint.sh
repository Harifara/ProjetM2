#!/bin/sh

set -e

echo "🚀 Waiting for database $DB_HOST:$DB_PORT..."
while ! nc -z $DB_HOST $DB_PORT; do
  sleep 1
done
echo "✅ Database is up!"

echo "📦 Applying database migrations..."
python manage.py migrate --noinput

echo "⚙️ Collecting static files..."
python manage.py collectstatic --noinput

echo "🚀 Starting Gunicorn server..."
exec gunicorn auth_service.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 4 \
    --timeout 120
