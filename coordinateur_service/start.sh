#!/bin/bash

echo "🔄 Waiting for database..."
while ! pg_isready -h coordinateur_db -p 5432 -U postgres > /dev/null 2>&1; do
  sleep 1
done

echo "✅ Database is ready"

echo "🔄 Running migrations..."
python manage.py migrate --noinput

echo "🔄 Collecting static files..."
python manage.py collectstatic --noinput

echo "🚀 Starting server..."
python manage.py runserver 0.0.0.0:8000
