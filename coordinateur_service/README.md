# Service Coordinateur - REST API

Service de validation des demandes de décaissement pour le système de gestion interne.

## Fonctionnalités

- **Validation de décaissements** : Approuver ou rejeter les demandes (achat, paiement, décaissement, transfert)
- **Consultation d'opérations** : Suivi et historique des opérations
- **Journalisation d'audit** : Traçabilité complète des actions
- **Tableau de bord** : Statistiques et métriques en temps réel

## Technologies

- Django 5.0.1
- Django REST Framework
- PostgreSQL
- JWT Authentication
- Docker

## Installation

### Avec Docker

```bash
docker-compose up -d coordinateur_db coordinateur_service
```

### Manuel

```bash
cd coordinateur_service
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver 8002
```

## Configuration

Variables d'environnement dans `.env` :

```
SECRET_KEY=votre-clé-secrète
DB_NAME=coordinateur_db
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=5432
JWT_SIGNING_KEY=votre-clé-jwt
AUTH_SERVICE_URL=http://localhost:8000/api/auth
```

## API Endpoints

### Validations

- `GET /api/coordinateur/validations/` - Liste des validations
- `POST /api/coordinateur/validations/` - Créer une validation
- `GET /api/coordinateur/validations/{id}/` - Détail d'une validation
- `POST /api/coordinateur/validations/{id}/validate/` - Valider/Rejeter
- `GET /api/coordinateur/validations/pending/` - Demandes en attente
- `GET /api/coordinateur/validations/validated/` - Demandes validées
- `GET /api/coordinateur/validations/rejected/` - Demandes rejetées
- `GET /api/coordinateur/validations/dashboard/` - Statistiques

### Opérations

- `GET /api/coordinateur/operations/` - Consultations d'opérations
- `POST /api/coordinateur/operations/` - Enregistrer une consultation
- `GET /api/coordinateur/operations/my-views/` - Mes consultations

### Audit

- `GET /api/coordinateur/audit-logs/` - Journaux d'audit

## Authentification

Le service utilise JWT pour l'authentification. Incluez le token dans l'en-tête :

```
Authorization: Bearer <votre-token>
```

Le token est obtenu via le service d'authentification.

## Permissions

Seuls les utilisateurs avec le rôle `coordinateur` peuvent accéder aux endpoints de ce service.

## Documentation API

- Swagger UI : http://localhost:8002/swagger/
- ReDoc : http://localhost:8002/redoc/
