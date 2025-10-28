# Service d'Authentification - Microservice Django REST API

Service d'authentification pour le système de gestion interne basé sur Django REST Framework avec JWT.

## Fonctionnalités

- ✅ Authentification JWT (JSON Web Tokens)
- ✅ Gestion des utilisateurs avec rôles
- ✅ Système d'audit complet
- ✅ Permissions basées sur les rôles
- ✅ API REST complète
- ✅ Documentation Swagger/ReDoc intégrée
- ✅ Support Docker

## Rôles Disponibles

- `admin` - Administrateur système
- `responsable_rh` - Responsable Ressources Humaines
- `responsable_stock` - Responsable Stock
- `responsable_finance` - Responsable Finance
- `magasinier` - Magasinier
- `coordinateur` - Coordinateur

## Installation

### Prérequis

- Python 3.11+
- PostgreSQL 15+
- Docker & Docker Compose (optionnel)

### Installation locale

1. Créer un environnement virtuel :
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows
```

2. Installer les dépendances :
```bash
pip install -r requirements.txt
```

3. Configurer les variables d'environnement :
```bash
cp .env.example .env
# Modifier .env avec vos configurations
```

4. Appliquer les migrations :
```bash
python manage.py migrate
```

5. Créer un superutilisateur :
```bash
python manage.py createsuperuser
```

6. Lancer le serveur :
```bash
python manage.py runserver
```

### Installation avec Docker

```bash
docker-compose up -d
```

Le service sera accessible sur `http://localhost:8000`

## Endpoints API

### Authentification

- `POST /api/auth/login/` - Connexion
- `POST /api/auth/logout/` - Déconnexion
- `GET /api/auth/me/` - Profil utilisateur
- `POST /api/auth/token/refresh/` - Rafraîchir le token

### Utilisateurs (Admin uniquement)

- `GET /api/auth/users/` - Liste des utilisateurs
- `POST /api/auth/users/` - Créer un utilisateur
- `GET /api/auth/users/{id}/` - Détails d'un utilisateur
- `PUT /api/auth/users/{id}/` - Modifier un utilisateur
- `DELETE /api/auth/users/{id}/` - Supprimer un utilisateur
- `POST /api/auth/users/{id}/change-password/` - Changer le mot de passe
- `POST /api/auth/users/{id}/toggle-active/` - Activer/Désactiver un utilisateur

### Audit Logs (Admin uniquement)

- `GET /api/auth/audit-logs/` - Liste des logs d'audit
- `GET /api/auth/audit-logs/{id}/` - Détails d'un log

## Documentation API

- Swagger UI : `http://localhost:8000/swagger/`
- ReDoc : `http://localhost:8000/redoc/`

## Exemples d'utilisation

### 1. Connexion

```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "password123"
  }'
```

Réponse :
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": "uuid",
    "username": "admin",
    "email": "admin@example.com",
    "full_name": "Administrateur",
    "role": "admin",
    "is_active": true
  }
}
```

### 2. Créer un utilisateur

```bash
curl -X POST http://localhost:8000/api/auth/users/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "username": "responsable_rh",
    "email": "rh@example.com",
    "full_name": "Responsable RH",
    "role": "responsable_rh",
    "password": "securepassword",
    "password_confirm": "securepassword",
    "is_active": true
  }'
```

### 3. Obtenir le profil

```bash
curl -X GET http://localhost:8000/api/auth/me/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### 4. Rafraîchir le token

```bash
curl -X POST http://localhost:8000/api/auth/token/refresh/ \
  -H "Content-Type: application/json" \
  -d '{
    "refresh": "YOUR_REFRESH_TOKEN"
  }'
```

## Structure du Projet

```
auth_service/
├── auth_service/           # Configuration Django
│   ├── __init__.py
│   ├── settings.py        # Configuration principale
│   ├── urls.py            # URLs principales
│   ├── wsgi.py
│   └── asgi.py
├── authentication/         # Application d'authentification
│   ├── models.py          # Modèles User et AuditLog
│   ├── serializers.py     # Serializers DRF
│   ├── views.py           # ViewSets et vues
│   ├── permissions.py     # Permissions personnalisées
│   ├── middleware.py      # Middleware d'audit
│   ├── utils.py           # Fonctions utilitaires
│   ├── urls.py            # URLs de l'app
│   └── admin.py           # Configuration admin
├── manage.py
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── .env.example
```

## Sécurité

- Les mots de passe sont hashés avec PBKDF2
- Authentification JWT avec refresh tokens
- Tokens expirés après 1 heure (access) et 7 jours (refresh)
- Audit complet de toutes les actions
- Permissions basées sur les rôles
- CORS configurable

## Système d'Audit

Toutes les actions sont automatiquement enregistrées dans la table `audit_logs` :
- Connexions/Déconnexions
- Création/Modification/Suppression d'utilisateurs
- Changements de mots de passe
- Toutes les requêtes API modifiant des données

Chaque log contient :
- Utilisateur
- Type d'action
- Type et ID de l'entité
- Détails de l'action
- Timestamp
- Adresse IP
- User Agent

## Variables d'environnement

```env
DEBUG=True
SECRET_KEY=your-secret-key
ALLOWED_HOSTS=localhost,127.0.0.1

DB_NAME=auth_db
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=5432

CORS_ALLOW_ALL_ORIGINS=True
```

## Tests

```bash
python manage.py test authentication
```

## Production

1. Désactiver le mode debug : `DEBUG=False`
2. Changer la `SECRET_KEY`
3. Configurer `ALLOWED_HOSTS`
4. Utiliser une base de données sécurisée
5. Configurer CORS correctement
6. Utiliser un serveur WSGI (Gunicorn, uWSGI)
7. Mettre en place HTTPS

## Support

Pour toute question ou problème, veuillez créer une issue dans le repository.
