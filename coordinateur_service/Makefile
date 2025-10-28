.PHONY: help build up down restart logs shell migrate test clean

help:
	@echo "Commandes disponibles:"
	@echo "  make build     - Construire l'image Docker"
	@echo "  make up        - Démarrer les services"
	@echo "  make down      - Arrêter les services"
	@echo "  make restart   - Redémarrer les services"
	@echo "  make logs      - Voir les logs"
	@echo "  make shell     - Ouvrir un shell dans le container"
	@echo "  make migrate   - Exécuter les migrations"
	@echo "  make test      - Exécuter les tests"
	@echo "  make clean     - Nettoyer les fichiers temporaires"

build:
	docker-compose build coordinateur_service

up:
	docker-compose up -d coordinateur_db coordinateur_service

down:
	docker-compose down

restart:
	docker-compose restart coordinateur_service

logs:
	docker-compose logs -f coordinateur_service

shell:
	docker-compose exec coordinateur_service /bin/bash

migrate:
	docker-compose exec coordinateur_service python manage.py migrate

makemigrations:
	docker-compose exec coordinateur_service python manage.py makemigrations

test:
	docker-compose exec coordinateur_service python manage.py test

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true

superuser:
	docker-compose exec coordinateur_service python manage.py createsuperuser

collectstatic:
	docker-compose exec coordinateur_service python manage.py collectstatic --noinput

dbshell:
	docker-compose exec coordinateur_db psql -U postgres -d coordinateur_db
