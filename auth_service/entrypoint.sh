#!/bin/sh

set -e

echo "🚀 Waiting for database $DB_HOST:$DB_PORT..."
while ! nc -z $DB_HOST $DB_PORT; do
  sleep 1
done
echo "✅ Database is up!"

echo "📦 Making migrations for authentication..."
python manage.py makemigrations authentication --noinput

echo "📦 Applying all migrations..."
python manage.py migrate --noinput

echo "⚙️ Collecting static files..."
python manage.py collectstatic --noinput

echo "🚀 Starting Django server..."
python manage.py runserver 0.0.0.0:8000
