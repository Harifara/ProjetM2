# Service RH (Ressources Humaines)

Service Django REST Framework pour la gestion des employés et départements, protégé par Kong Gateway et utilisant JWT du service d'authentification.

## Architecture

- **Framework**: Django 4.2 + Django REST Framework
- **Base de données**: PostgreSQL
- **Authentification**: JWT via Kong Gateway
- **API Gateway**: Kong

## Fonctionnalités

### Employés
- CRUD complet des employés
- Gestion des statuts (actif, inactif, en congé, licencié)
- Recherche et filtres avancés
- Statistiques des employés
- Lien avec le service d'authentification via `user_id`

### Départements
- CRUD complet des départements
- Liste des employés par département
- Comptage automatique des employés

## Authentification JWT

Le service utilise l'authentification JWT fournie par le service Auth et validée par Kong Gateway.

### Format du token JWT

```json
{
  "iss": "auth-service",
  "sub": "user_id",
  "username": "username",
  "exp": 1234567890
}
```

### Configuration JWT

Les paramètres JWT doivent correspondre exactement entre :
- Le service Auth (`auth_service/settings.py`)
- Le service RH (`rh_service/settings.py`)
- Kong Gateway (`kong.yml`)

```python
JWT_SECRET = "my_super_secret_key_123"
JWT_ALGORITHM = "HS256"
JWT_ISSUER = "auth-service"
```

## API Endpoints

### Health Check
- `GET /api/rh/health/` - Vérification de l'état du service (public)

### Employés
- `GET /api/rh/employees/` - Liste des employés
- `POST /api/rh/employees/` - Créer un employé
- `GET /api/rh/employees/{id}/` - Détails d'un employé
- `PUT /api/rh/employees/{id}/` - Mettre à jour un employé
- `DELETE /api/rh/employees/{id}/` - Supprimer un employé
- `POST /api/rh/employees/{id}/change-status/` - Changer le statut
- `GET /api/rh/employees/by-user/{user_id}/` - Employé par user_id
- `GET /api/rh/employees/statistics/` - Statistiques

### Départements
- `GET /api/rh/departments/` - Liste des départements
- `POST /api/rh/departments/` - Créer un département
- `GET /api/rh/departments/{id}/` - Détails d'un département
- `PUT /api/rh/departments/{id}/` - Mettre à jour un département
- `DELETE /api/rh/departments/{id}/` - Supprimer un département
- `GET /api/rh/departments/{id}/employees/` - Employés du département

## Modèles de données

### Employee
- `user_id` - Lien avec le service Auth (unique)
- `first_name`, `last_name` - Nom et prénom
- `email` - Email (unique)
- `phone` - Téléphone
- `gender` - Genre (M/F/O)
- `birth_date` - Date de naissance
- `hire_date` - Date d'embauche
- `department` - Département (FK)
- `position` - Poste
- `salary` - Salaire
- `status` - Statut (active/inactive/on_leave/terminated)
- `address` - Adresse
- `emergency_contact` - Contact d'urgence
- `emergency_phone` - Téléphone d'urgence

### Department
- `name` - Nom du département (unique)
- `description` - Description

## Installation locale

```bash
cd rh_service
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver 8001
```

## Variables d'environnement

Voir `.env` pour la configuration complète.

## Sécurité

- Toutes les routes sont protégées par authentification JWT
- Validation des tokens via Kong Gateway
- CORS configuré pour autoriser uniquement les origines approuvées
