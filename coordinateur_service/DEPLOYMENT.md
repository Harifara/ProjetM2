# Guide de déploiement - Service Coordinateur

## Prérequis

- Docker et Docker Compose installés
- Ports disponibles : 8002 (API), 5435 (PostgreSQL)
- Service d'authentification démarré et accessible

## Déploiement rapide

### 1. Configuration

Créer le fichier `.env` à partir de l'exemple :

```bash
cp .env.example .env
```

Modifier les variables si nécessaire, particulièrement :
- `SECRET_KEY` : Générer une nouvelle clé secrète
- `JWT_SIGNING_KEY` : Doit être identique au service d'authentification
- `AUTH_SERVICE_URL` : URL du service d'authentification

### 2. Démarrage

Depuis le répertoire racine du projet :

```bash
# Démarrer la base de données et le service
docker-compose up -d coordinateur_db coordinateur_service

# Vérifier les logs
docker-compose logs -f coordinateur_service
```

### 3. Vérification

L'API devrait être accessible sur :
- http://localhost:8002/api/coordinateur/
- http://localhost:8002/swagger/ (documentation)
- http://localhost:8002/admin/ (interface admin)

## Commandes utiles

### Via Makefile

```bash
# Construire l'image
make build

# Démarrer les services
make up

# Voir les logs
make logs

# Accéder au shell
make shell

# Exécuter les migrations
make migrate

# Lancer les tests
make test

# Arrêter les services
make down
```

### Via Docker Compose

```bash
# Démarrer tous les services
docker-compose up -d

# Démarrer uniquement le service coordinateur
docker-compose up -d coordinateur_db coordinateur_service

# Voir les logs en temps réel
docker-compose logs -f coordinateur_service

# Redémarrer le service
docker-compose restart coordinateur_service

# Arrêter les services
docker-compose stop coordinateur_service coordinateur_db

# Supprimer les containers
docker-compose down

# Supprimer containers + volumes
docker-compose down -v
```

### Via Docker directement

```bash
# Accéder au container
docker exec -it coordinateur_service /bin/bash

# Exécuter les migrations
docker exec coordinateur_service python manage.py migrate

# Créer un superuser
docker exec -it coordinateur_service python manage.py createsuperuser

# Voir les logs
docker logs coordinateur_service

# Redémarrer le container
docker restart coordinateur_service
```

## Migrations de base de données

### Créer une migration

```bash
docker exec coordinateur_service python manage.py makemigrations
```

### Appliquer les migrations

```bash
docker exec coordinateur_service python manage.py migrate
```

### Voir l'état des migrations

```bash
docker exec coordinateur_service python manage.py showmigrations
```

### Revenir en arrière

```bash
docker exec coordinateur_service python manage.py migrate coordinateur 0001_initial
```

## Tests

### Exécuter tous les tests

```bash
docker exec coordinateur_service python manage.py test
```

### Exécuter un test spécifique

```bash
docker exec coordinateur_service python manage.py test coordinateur.tests.DecashmentValidationTests
```

### Avec couverture de code

```bash
docker exec coordinateur_service pytest --cov=coordinateur --cov-report=html
```

## Gestion de la base de données

### Accéder à PostgreSQL

```bash
docker exec -it coordinateur_db psql -U postgres -d coordinateur_db
```

### Sauvegarder la base

```bash
docker exec coordinateur_db pg_dump -U postgres coordinateur_db > backup.sql
```

### Restaurer la base

```bash
docker exec -i coordinateur_db psql -U postgres coordinateur_db < backup.sql
```

### Réinitialiser la base

```bash
# Arrêter le service
docker-compose stop coordinateur_service

# Supprimer le volume
docker volume rm project_coordinateur_postgres_data

# Redémarrer
docker-compose up -d coordinateur_db coordinateur_service
```

## Collecte des fichiers statiques

```bash
docker exec coordinateur_service python manage.py collectstatic --noinput
```

## Variables d'environnement

### Variables essentielles

| Variable | Description | Valeur par défaut |
|----------|-------------|-------------------|
| `SECRET_KEY` | Clé secrète Django | À changer en production |
| `DEBUG` | Mode debug | `True` |
| `ALLOWED_HOSTS` | Hôtes autorisés | `*` |
| `DB_NAME` | Nom de la base | `coordinateur_db` |
| `DB_USER` | Utilisateur PostgreSQL | `postgres` |
| `DB_PASSWORD` | Mot de passe PostgreSQL | `postgres` |
| `DB_HOST` | Hôte PostgreSQL | `coordinateur_db` |
| `DB_PORT` | Port PostgreSQL | `5432` |
| `JWT_SIGNING_KEY` | Clé JWT partagée | À synchroniser avec auth |
| `AUTH_SERVICE_URL` | URL service auth | `http://auth_service:8000/api/auth` |

## Monitoring et logs

### Voir les logs en direct

```bash
docker-compose logs -f coordinateur_service
```

### Voir les logs de la base de données

```bash
docker-compose logs -f coordinateur_db
```

### Voir les dernières 100 lignes

```bash
docker-compose logs --tail=100 coordinateur_service
```

## Dépannage

### Le service ne démarre pas

1. Vérifier les logs :
```bash
docker-compose logs coordinateur_service
```

2. Vérifier que la base est prête :
```bash
docker-compose ps coordinateur_db
```

3. Vérifier les variables d'environnement :
```bash
docker-compose exec coordinateur_service env | grep DB_
```

### Erreur de connexion à la base

1. Vérifier que le service database est en cours :
```bash
docker-compose ps coordinateur_db
```

2. Tester la connexion manuellement :
```bash
docker exec coordinateur_db pg_isready -U postgres
```

3. Vérifier les credentials dans `.env`

### Erreur JWT

1. Vérifier que `JWT_SIGNING_KEY` est identique dans tous les services
2. Vérifier que le service d'authentification est accessible :
```bash
curl http://localhost:8000/api/auth/
```

### Port déjà utilisé

Modifier le port dans `docker-compose.yml` :
```yaml
ports:
  - "8003:8000"  # Au lieu de 8002:8000
```

## Sécurité en production

### Checklist

- [ ] Changer `SECRET_KEY`
- [ ] Mettre `DEBUG=False`
- [ ] Définir `ALLOWED_HOSTS` correctement
- [ ] Utiliser des mots de passe forts pour PostgreSQL
- [ ] Configurer HTTPS
- [ ] Activer les backups automatiques
- [ ] Configurer les logs centralisés
- [ ] Limiter les permissions PostgreSQL
- [ ] Mettre à jour régulièrement les dépendances

### Configuration HTTPS

Utiliser un reverse proxy (Nginx, Traefik) avec Let's Encrypt.

### Backups automatiques

Créer un cron job :
```bash
0 2 * * * docker exec coordinateur_db pg_dump -U postgres coordinateur_db > /backups/coordinateur_$(date +\%Y\%m\%d).sql
```

## Mise à jour

### Mettre à jour le service

```bash
# Pull les dernières modifications
git pull

# Reconstruire l'image
docker-compose build coordinateur_service

# Redémarrer
docker-compose up -d coordinateur_service

# Appliquer les migrations
docker exec coordinateur_service python manage.py migrate
```

## Performance

### Optimisation PostgreSQL

Dans `docker-compose.yml`, ajouter :
```yaml
coordinateur_db:
  environment:
    POSTGRES_INITDB_ARGS: "-E UTF8 --locale=fr_FR.UTF-8"
  command:
    - "postgres"
    - "-c"
    - "shared_buffers=256MB"
    - "-c"
    - "max_connections=200"
```

### Cache Redis (optionnel)

Ajouter Redis pour améliorer les performances :
```yaml
coordinateur_redis:
  image: redis:7-alpine
  ports:
    - "6379:6379"
```

## Support

En cas de problème :
1. Consulter les logs
2. Vérifier la documentation
3. Tester avec `test_api.py`
4. Vérifier les issues GitHub
