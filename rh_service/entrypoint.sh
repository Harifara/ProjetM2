#!/bin/sh
set -e

echo "🚀 Waiting for database $DB_HOST:$DB_PORT..."
while ! nc -z $DB_HOST $DB_PORT; do
  sleep 1
done
echo "✅ Database is up!"

echo "📦 Making migrations..."
python manage.py makemigrations  --noinput  # <-- supprime le nom 'authentication'

echo "📦 Applying all migrations..."
python manage.py migrate --noinput

echo "⚙️ Collecting static files..."
python manage.py collectstatic --noinput

echo "🚀 Starting Django server..."
exec python manage.py runserver 0.0.0.0:8000
