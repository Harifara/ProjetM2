# Architecture du Service Coordinateur

## Vue d'ensemble

Le service coordinateur est un microservice REST API Django qui gère la validation des demandes de décaissement dans le système de gestion interne. Il dépend du service d'authentification pour la gestion des utilisateurs et des permissions.

## Structure du projet

```
coordinateur_service/
├── coordinateur/                    # Application Django principale
│   ├── migrations/                  # Migrations de base de données
│   ├── __init__.py
│   ├── admin.py                     # Configuration admin Django
│   ├── apps.py                      # Configuration de l'application
│   ├── middleware.py                # Middlewares personnalisés
│   ├── models.py                    # Modèles de données
│   ├── permissions.py               # Permissions personnalisées
│   ├── serializers.py               # Sérialiseurs REST
│   ├── tests.py                     # Tests unitaires
│   ├── urls.py                      # Routes de l'application
│   ├── utils.py                     # Fonctions utilitaires
│   └── views.py                     # Vues/ViewSets API
├── coordinateur_service/            # Configuration du projet Django
│   ├── __init__.py
│   ├── asgi.py                      # Configuration ASGI
│   ├── settings.py                  # Configuration globale
│   ├── urls.py                      # Routes principales
│   └── wsgi.py                      # Configuration WSGI
├── .env                             # Variables d'environnement
├── .gitignore
├── Dockerfile                       # Configuration Docker
├── manage.py                        # Script de gestion Django
├── requirements.txt                 # Dépendances Python
├── start.sh                         # Script de démarrage
├── API_EXAMPLES.md                  # Exemples d'utilisation API
├── ARCHITECTURE.md                  # Ce fichier
└── README.md                        # Documentation principale
```

## Modèles de données

### DecashmentValidation
Représente une demande de validation de décaissement.

**Champs :**
- `id` : UUID unique
- `request_type` : Type de demande (purchase, payment, decashment, stock_transfer)
- `request_id` : ID de la demande originale
- `validation_status` : Statut (en_attente, validé, rejeté)
- `validated_by` : ID du coordinateur validateur
- `validation_date` : Date de validation
- `comments` : Commentaires de validation
- `amount` : Montant de la demande
- `reason` : Raison de la demande
- `requested_by` : ID du demandeur
- `department` : Département demandeur

### AuditLog
Journalise toutes les actions importantes du coordinateur.

**Champs :**
- `id` : UUID unique
- `user_id` : ID de l'utilisateur
- `action_type` : Type d'action
- `entity_type` : Type d'entité concernée
- `entity_id` : ID de l'entité
- `timestamp` : Date/heure de l'action
- `details` : Détails JSON
- `ip_address` : Adresse IP
- `user_agent` : Agent utilisateur

### OperationView
Enregistre les consultations d'opérations par le coordinateur.

**Champs :**
- `id` : UUID unique
- `viewed_by` : ID du coordinateur
- `operation_type` : Type d'opération consultée
- `operation_id` : ID de l'opération
- `viewed_at` : Date/heure de consultation

## API Endpoints

### Validations (`/api/coordinateur/validations/`)

| Méthode | Endpoint | Description | Permission |
|---------|----------|-------------|------------|
| GET | `/` | Liste des validations | Coordinateur |
| POST | `/` | Créer une validation | Coordinateur |
| GET | `/{id}/` | Détail d'une validation | Coordinateur |
| PUT | `/{id}/` | Modifier une validation | Coordinateur |
| DELETE | `/{id}/` | Supprimer une validation | Coordinateur |
| POST | `/{id}/validate/` | Valider/Rejeter | Coordinateur |
| GET | `/pending/` | Demandes en attente | Coordinateur |
| GET | `/validated/` | Demandes validées | Coordinateur |
| GET | `/rejected/` | Demandes rejetées | Coordinateur |
| GET | `/dashboard/` | Statistiques | Coordinateur |

### Opérations (`/api/coordinateur/operations/`)

| Méthode | Endpoint | Description | Permission |
|---------|----------|-------------|------------|
| GET | `/` | Liste des consultations | Coordinateur |
| POST | `/` | Enregistrer consultation | Coordinateur |
| GET | `/my-views/` | Mes consultations | Coordinateur |

### Audit (`/api/coordinateur/audit-logs/`)

| Méthode | Endpoint | Description | Permission |
|---------|----------|-------------|------------|
| GET | `/` | Journaux d'audit | Coordinateur |
| GET | `/{id}/` | Détail d'un journal | Coordinateur |

## Middlewares

### JWTAuthenticationMiddleware
- Extrait et valide le token JWT des requêtes
- Récupère les informations utilisateur du service d'authentification
- Attache l'ID et le rôle de l'utilisateur à la requête

### AuditLogMiddleware
- Journalise automatiquement les actions importantes
- Enregistre les modifications (POST, PUT, PATCH, DELETE)
- Capture l'IP et le user-agent

## Authentification et Permissions

### Authentification
- Utilise JWT (JSON Web Tokens)
- Tokens générés par le service d'authentification
- Signature partagée entre les services (`JWT_SIGNING_KEY`)

### Permissions
- `IsCoordinateur` : Restreint l'accès aux utilisateurs avec rôle "coordinateur"
- `IsAuthenticated` : Vérifie que l'utilisateur est authentifié

## Dépendances externes

### Service d'authentification
- URL : `AUTH_SERVICE_URL` (défini dans .env)
- Utilisé pour :
  - Vérifier le rôle des utilisateurs
  - Récupérer les informations utilisateur
  - Valider les tokens JWT

## Sécurité

### Bonnes pratiques implémentées
1. **Validation des tokens JWT** : Tous les endpoints nécessitent un token valide
2. **Permissions granulaires** : Seuls les coordinateurs peuvent accéder aux endpoints
3. **Audit complet** : Toutes les actions sont journalisées
4. **Validation des données** : Utilisation de sérialiseurs Django REST Framework
5. **CORS configuré** : Protection contre les requêtes cross-origin non autorisées

### Traçabilité
- Chaque validation est tracée avec l'ID du coordinateur
- Journalisation automatique via middleware
- Historique complet des consultations

## Workflow de validation

1. **Réception de la demande** : Une demande de décaissement est créée (status: en_attente)
2. **Consultation** : Le coordinateur consulte les détails de la demande
3. **Décision** :
   - **Validation** : Status devient "validé", notification au service Finance
   - **Rejet** : Status devient "rejeté", notification au service demandeur
4. **Journalisation** : L'action est enregistrée dans AuditLog

## Intégration avec d'autres services

### Service Finance
Notifie le service Finance lorsqu'une demande est validée pour procéder au paiement/achat.

### Service RH / Stock
Reçoit les demandes de décaissement de ces services et notifie en cas de rejet.

## Base de données

- **Type** : PostgreSQL 15
- **Nom** : `coordinateur_db`
- **Port** : 5435 (externe), 5432 (interne)
- **Migrations** : Gérées par Django ORM

## Déploiement

### Docker
```bash
docker-compose up -d coordinateur_db coordinateur_service
```

### Variables d'environnement requises
- `SECRET_KEY` : Clé secrète Django
- `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT` : Configuration PostgreSQL
- `JWT_SIGNING_KEY` : Clé pour la validation des tokens JWT
- `AUTH_SERVICE_URL` : URL du service d'authentification

## Tests

Exécuter les tests :
```bash
python manage.py test coordinateur
```

## Monitoring et logs

- Logs Django standard
- Journaux d'audit dans la base de données
- Endpoints de santé disponibles via `/admin/`

## Évolutions futures

1. **Notifications en temps réel** : WebSockets pour alertes instantanées
2. **Workflows complexes** : Validation en plusieurs étapes
3. **Rapports avancés** : Génération de rapports PDF
4. **Intégration mobile** : API optimisée pour applications mobiles
5. **Machine Learning** : Détection automatique des anomalies dans les demandes
