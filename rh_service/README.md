# Service RH - Microservice Django REST API

Service de gestion des ressources humaines pour le système de gestion interne basé sur Django REST Framework. Ce service dépend du service d'authentification et gère les employés, contrats, congés, affectations, et demandes de paiement/achat.

## 🚀 Fonctionnalités

✅ **Gestion des Employés**
- Création, modification, suppression d'employés
- Association avec les utilisateurs du service d'authentification
- Gestion des districts et affectations géographiques
- Statistiques des employés (par département, district, statut)

✅ **Gestion des Contrats**
- Contrats CDI, CDD, stage, consultant
- Suivi des dates de début et fin
- Gestion des salaires
- Documents associés

✅ **Gestion des Congés**
- Demandes de congé (annuel, maladie, maternité, etc.)
- Workflow de validation par responsable RH
- Calcul automatique du nombre de jours
- Historique complet

✅ **Gestion des Affectations**
- Mutations, promotions, affectations temporaires
- Changement de poste et/ou de district
- Workflow de validation
- Mise à jour automatique du profil employé

✅ **Demandes de Paiement RH**
- Salaires, primes, indemnités, remboursements
- Workflow de validation
- Intégration avec le service Finance

✅ **Demandes d'Achat RH**
- Achats pour le département RH
- Validation hiérarchique
- Transmission au service Finance

✅ **Audit Complet**
- Traçabilité de toutes les actions
- Logs détaillés avec IP et User Agent
- Consultation réservée aux responsables RH

✅ **Authentification Centralisée**
- Intégration avec le service d'authentification JWT
- Permissions basées sur les rôles
- Cache des utilisateurs pour performance

## 📋 Prérequis

- Python 3.11+
- PostgreSQL 15+
- Service d'authentification opérationnel
- Docker & Docker Compose (optionnel)

## 🛠️ Installation

### Installation Locale

#### 1. Créer un environnement virtuel

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows
```

#### 2. Installer les dépendances

```bash
cd rh_service
pip install -r requirements.txt
```

#### 3. Configurer les variables d'environnement

```bash
cp .env.example .env
# Modifier .env avec vos configurations
```

**Variables importantes :**
```env
DEBUG=True
SECRET_KEY=your-secret-key
DB_NAME=rh_db
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=5432
AUTH_SERVICE_URL=http://localhost:8000
```

#### 4. Créer la base de données

```bash
# Se connecter à PostgreSQL
psql -U postgres

# Créer la base de données
CREATE DATABASE rh_db;
\q
```

#### 5. Appliquer les migrations

```bash
python manage.py migrate
```

#### 6. Créer un superutilisateur (optionnel)

```bash
python manage.py createsuperuser
```

#### 7. Lancer le serveur

```bash
python manage.py runserver 0.0.0.0:8001
```

Le service sera accessible sur **http://localhost:8001**

### Installation avec Docker

```bash
cd rh_service
cp .env.example .env
# Modifier .env si nécessaire

docker-compose up -d
```

Le service sera accessible sur **http://localhost:8001**

## 📚 API Endpoints

### Districts

| Méthode | Endpoint | Description | Permission |
|---------|----------|-------------|------------|
| GET | `/api/rh/districts/` | Liste des districts | Authentifié |
| POST | `/api/rh/districts/` | Créer un district | Responsable RH |
| GET | `/api/rh/districts/{id}/` | Détails d'un district | Authentifié |
| PUT | `/api/rh/districts/{id}/` | Modifier un district | Responsable RH |
| DELETE | `/api/rh/districts/{id}/` | Supprimer un district | Responsable RH |

### Employés

| Méthode | Endpoint | Description | Permission |
|---------|----------|-------------|------------|
| GET | `/api/rh/employees/` | Liste des employés | Responsable RH |
| POST | `/api/rh/employees/` | Créer un employé | Responsable RH |
| GET | `/api/rh/employees/{id}/` | Détails d'un employé | Responsable RH |
| PUT | `/api/rh/employees/{id}/` | Modifier un employé | Responsable RH |
| DELETE | `/api/rh/employees/{id}/` | Supprimer un employé | Responsable RH |
| GET | `/api/rh/employees/stats/` | Statistiques employés | Responsable RH |
| GET | `/api/rh/employees/{id}/contracts/` | Contrats d'un employé | Responsable RH |
| GET | `/api/rh/employees/{id}/leave-requests/` | Congés d'un employé | Responsable RH |

### Contrats

| Méthode | Endpoint | Description | Permission |
|---------|----------|-------------|------------|
| GET | `/api/rh/contracts/` | Liste des contrats | Responsable RH |
| POST | `/api/rh/contracts/` | Créer un contrat | Responsable RH |
| GET | `/api/rh/contracts/{id}/` | Détails d'un contrat | Responsable RH |
| PUT | `/api/rh/contracts/{id}/` | Modifier un contrat | Responsable RH |
| DELETE | `/api/rh/contracts/{id}/` | Supprimer un contrat | Responsable RH |

### Demandes de Congé

| Méthode | Endpoint | Description | Permission |
|---------|----------|-------------|------------|
| GET | `/api/rh/leave-requests/` | Liste des demandes | Authentifié* |
| POST | `/api/rh/leave-requests/` | Créer une demande | Authentifié |
| GET | `/api/rh/leave-requests/{id}/` | Détails d'une demande | Authentifié* |
| PUT | `/api/rh/leave-requests/{id}/` | Modifier une demande | Authentifié* |
| DELETE | `/api/rh/leave-requests/{id}/` | Supprimer une demande | Authentifié* |
| POST | `/api/rh/leave-requests/{id}/validate/` | Valider une demande | Responsable RH |

*Les employés ne voient que leurs propres demandes. Les responsables RH voient tout.

### Affectations

| Méthode | Endpoint | Description | Permission |
|---------|----------|-------------|------------|
| GET | `/api/rh/assignments/` | Liste des affectations | Responsable RH |
| POST | `/api/rh/assignments/` | Créer une affectation | Responsable RH |
| GET | `/api/rh/assignments/{id}/` | Détails d'une affectation | Responsable RH |
| PUT | `/api/rh/assignments/{id}/` | Modifier une affectation | Responsable RH |
| DELETE | `/api/rh/assignments/{id}/` | Supprimer une affectation | Responsable RH |
| POST | `/api/rh/assignments/{id}/validate/` | Valider une affectation | Responsable RH |

### Demandes de Paiement

| Méthode | Endpoint | Description | Permission |
|---------|----------|-------------|------------|
| GET | `/api/rh/payment-requests/` | Liste des demandes | Responsable RH |
| POST | `/api/rh/payment-requests/` | Créer une demande | Responsable RH |
| GET | `/api/rh/payment-requests/{id}/` | Détails d'une demande | Responsable RH |
| PUT | `/api/rh/payment-requests/{id}/` | Modifier une demande | Responsable RH |
| DELETE | `/api/rh/payment-requests/{id}/` | Supprimer une demande | Responsable RH |
| POST | `/api/rh/payment-requests/{id}/validate/` | Valider une demande | Responsable RH |

### Demandes d'Achat

| Méthode | Endpoint | Description | Permission |
|---------|----------|-------------|------------|
| GET | `/api/rh/purchase-requests/` | Liste des demandes | Responsable RH |
| POST | `/api/rh/purchase-requests/` | Créer une demande | Responsable RH |
| GET | `/api/rh/purchase-requests/{id}/` | Détails d'une demande | Responsable RH |
| PUT | `/api/rh/purchase-requests/{id}/` | Modifier une demande | Responsable RH |
| DELETE | `/api/rh/purchase-requests/{id}/` | Supprimer une demande | Responsable RH |
| POST | `/api/rh/purchase-requests/{id}/validate/` | Valider une demande | Responsable RH |

### Logs d'Audit

| Méthode | Endpoint | Description | Permission |
|---------|----------|-------------|------------|
| GET | `/api/rh/audit-logs/` | Liste des logs | Responsable RH |
| GET | `/api/rh/audit-logs/{id}/` | Détails d'un log | Responsable RH |

## 🔐 Authentification

Ce service utilise l'authentification JWT fournie par le service d'authentification.

### Obtenir un token

```bash
# Se connecter au service d'authentification
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "responsable_rh",
    "password": "password123"
  }'
```

### Utiliser le token

```bash
curl -X GET http://localhost:8001/api/rh/employees/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## 📖 Exemples d'Utilisation

### 1. Créer un District

```bash
curl -X POST http://localhost:8001/api/rh/districts/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Antananarivo"
  }'
```

### 2. Créer un Employé

```bash
curl -X POST http://localhost:8001/api/rh/employees/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user-uuid-from-auth-service",
    "employee_number": "EMP001",
    "position": "Développeur Senior",
    "department": "IT",
    "hire_date": "2024-01-15",
    "status": "active",
    "district": "district-uuid"
  }'
```

### 3. Créer un Contrat

```bash
curl -X POST http://localhost:8001/api/rh/contracts/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "employee": "employee-uuid",
    "contract_type": "CDI",
    "start_date": "2024-01-15",
    "status": "active",
    "salary": "2500000.00"
  }'
```

### 4. Demande de Congé

```bash
curl -X POST http://localhost:8001/api/rh/leave-requests/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "employee": "employee-uuid",
    "leave_type": "annual",
    "start_date": "2024-03-01",
    "end_date": "2024-03-10",
    "reason": "Vacances familiales"
  }'
```

### 5. Valider une Demande de Congé

```bash
curl -X POST http://localhost:8001/api/rh/leave-requests/{id}/validate/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "approved"
  }'
```

### 6. Créer une Affectation (Mutation)

```bash
curl -X POST http://localhost:8001/api/rh/assignments/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "employee": "employee-uuid",
    "assignment_type": "transfer",
    "new_position": "Chef de Service IT",
    "new_district": "new-district-uuid",
    "start_date": "2024-04-01",
    "reason": "Promotion et transfert"
  }'
```

### 7. Demande de Paiement

```bash
curl -X POST http://localhost:8001/api/rh/payment-requests/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "employee": "employee-uuid",
    "request_type": "bonus",
    "amount": "500000.00",
    "reason": "Prime de performance Q1 2024"
  }'
```

### 8. Statistiques des Employés

```bash
curl -X GET http://localhost:8001/api/rh/employees/stats/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## 📊 Documentation API

Documentation interactive disponible :

- **Swagger UI** : http://localhost:8001/swagger/
- **ReDoc** : http://localhost:8001/redoc/

## 🏗️ Architecture

```
rh_service/
├── rh_service/              # Configuration Django
│   ├── settings.py         # Configuration principale
│   ├── urls.py             # URLs principales
│   ├── wsgi.py
│   └── asgi.py
├── rh/                      # Application RH
│   ├── models.py           # Modèles (Employee, Contract, etc.)
│   ├── serializers.py      # Serializers DRF
│   ├── views.py            # ViewSets
│   ├── permissions.py      # Permissions personnalisées
│   ├── authentication.py   # Auth avec service externe
│   ├── middleware.py       # Middleware d'audit
│   ├── utils.py            # Fonctions utilitaires
│   ├── urls.py             # URLs de l'app
│   └── admin.py            # Configuration admin
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── .env.example
```

## 🔒 Sécurité

- ✅ Authentification JWT centralisée
- ✅ Permissions basées sur les rôles (RBAC)
- ✅ Validation des données avec DRF
- ✅ Audit complet de toutes les actions
- ✅ Protection CORS configurable
- ✅ Séparation des préoccupations (microservices)

## 🎭 Rôles et Permissions

| Rôle | Permissions |
|------|-------------|
| **admin** | Accès complet à toutes les fonctionnalités |
| **responsable_rh** | Gestion complète des employés, contrats, congés, affectations |
| **employé** | Consultation de son profil et création de demandes de congé |

## 🔗 Intégration avec le Service d'Authentification

Le service RH communique avec le service d'authentification pour :

1. **Validation des tokens JWT** : Chaque requête est authentifiée via le service d'auth
2. **Récupération des informations utilisateur** : Profil, rôle, permissions
3. **Cache des utilisateurs** : Performance optimisée avec mise en cache (5 min)

**Configuration** :
```env
AUTH_SERVICE_URL=http://localhost:8000
AUTH_SERVICE_TIMEOUT=5
```

## 🚦 Workflow BPMN Implémenté

### Processus RH Principal

1. **Création/Modification Employé** → Responsable RH
2. **Gestion Contrats** → Responsable RH
3. **Gestion Congés** → Employé (demande) → Responsable RH (validation)
4. **Gestion Affectations** → Responsable RH (création) → Responsable RH (validation)
5. **Demande Paiement RH** → Responsable RH → Service Finance
6. **Demande Achat RH** → Responsable RH → Service Finance
7. **Audit** → Logs automatiques de toutes les actions

## 🧪 Tests

```bash
python manage.py test rh
```

## 📦 Production

### Checklist de Déploiement

- [ ] Désactiver le mode debug : `DEBUG=False`
- [ ] Changer la `SECRET_KEY`
- [ ] Configurer `ALLOWED_HOSTS`
- [ ] Utiliser une base de données sécurisée
- [ ] Configurer CORS correctement
- [ ] Utiliser Gunicorn ou uWSGI
- [ ] Mettre en place HTTPS
- [ ] Configurer les backups de base de données
- [ ] Monitorer les logs et performances
- [ ] Vérifier la connexion au service d'authentification

### Exemple de déploiement avec Gunicorn

```bash
gunicorn --bind 0.0.0.0:8001 --workers 3 rh_service.wsgi:application
```

## 🐛 Dépannage

### Erreur de connexion au service d'authentification

```bash
# Vérifier que le service d'auth est démarré
curl http://localhost:8000/api/auth/me/

# Vérifier la variable AUTH_SERVICE_URL dans .env
```

### Erreur de base de données

```bash
# Vérifier que PostgreSQL est démarré
psql -U postgres -c "SELECT version();"

# Re-créer la base de données si nécessaire
python manage.py migrate --run-syncdb
```

### Token expiré

Les tokens JWT expirent après 1 heure. Utilisez le refresh token pour obtenir un nouveau token d'accès.

## 📞 Support

Pour toute question ou problème, veuillez créer une issue dans le repository.

## 📄 Licence

Ce projet fait partie du système de gestion interne.

---

**Version** : 1.0.0
**Django** : 5.0.1
**Django REST Framework** : 3.14.0
**PostgreSQL** : 15+
