#!/bin/sh

# wait for db
echo "Waiting for Postgres..."
while ! nc -z $DB_HOST $DB_PORT; do
  sleep 0.5
done
echo "Postgres up"

# run migrations & start server
python manage.py migrate --noinput
python manage.py collectstatic --noinput

# start gunicorn
gunicorn notification_service.wsgi:application --bind 0.0.0.0:8000 --workers 2
