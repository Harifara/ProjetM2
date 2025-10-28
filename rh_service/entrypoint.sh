#!/bin/sh

# Arrête le script si une commande échoue
set -e

echo "🚀 Waiting for database $DB_HOST:5432..."

# Attente que la base PostgreSQL soit prête
until nc -z "$DB_HOST" 5432; do
  echo "❌ Database not ready, retrying in 2 seconds..."
  sleep 2
done

echo "✅ Database is up!"

echo "📦 Running makemigrations..."
python manage.py makemigrations --noinput || echo "⚠️ Makemigrations failed or no changes."

echo "📦 Applying migrations..."
python manage.py migrate --noinput

# Collecte des fichiers statiques (utile si Django admin ou fichiers statiques)
echo "⚙️ Collecting static files..."
python manage.py collectstatic --noinput || echo "⚠️ No static files to collect."

echo "🚀 Starting Django development server..."
exec python manage.py runserver 0.0.0.0:8000
