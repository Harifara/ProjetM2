# Finance Service - Microservice REST API

Service de gestion financière pour le système de gestion interne.

## Fonctionnalités

### Gestion des Demandes de Décaissement
- Réception des demandes de décaissement des services RH et Stock
- Validation des demandes par le coordinateur
- Notification aux services d'origine

### Gestion des Dépenses
- Création et suivi des dépenses
- Approbation et exécution des paiements
- Liaison avec les demandes de décaissement

### Gestion des Paiements
- Création des paiements
- Support de multiples méthodes de paiement
- Suivi du statut des paiements

### Gestion des Budgets
- Définition des budgets par département et catégorie
- Suivi des dépenses vs budget alloué
- Alertes en cas de dépassement

### Génération de Documents
- Factures
- Bulletins de paie
- Reçus de paiement
- Ordres de virement

### Notifications
- Notifications temps réel aux utilisateurs
- Notifications inter-services

### Audit et Traçabilité
- Journalisation de toutes les actions
- Historique complet des opérations

## API Endpoints

### Demandes de Décaissement
- `GET /api/finance/decashment-requests/` - Liste des demandes
- `POST /api/finance/decashment-requests/` - Créer une demande
- `GET /api/finance/decashment-requests/{id}/` - Détails d'une demande
- `POST /api/finance/decashment-requests/{id}/validate/` - Valider (coordinateur)
- `POST /api/finance/decashment-requests/{id}/reject/` - Rejeter (coordinateur)

### Dépenses
- `GET /api/finance/expenses/` - Liste des dépenses
- `POST /api/finance/expenses/` - Créer une dépense
- `POST /api/finance/expenses/{id}/approve/` - Approuver
- `POST /api/finance/expenses/{id}/execute/` - Exécuter

### Paiements
- `GET /api/finance/payments/` - Liste des paiements
- `POST /api/finance/payments/` - Créer un paiement
- `POST /api/finance/payments/{id}/complete/` - Compléter

### Budgets
- `GET /api/finance/budgets/` - Liste des budgets
- `POST /api/finance/budgets/` - Créer un budget
- `GET /api/finance/budgets/summary/` - Résumé budgétaire

### Documents
- `GET /api/finance/documents/` - Liste des documents
- `POST /api/finance/documents/` - Uploader un document

## Dépendances avec les autres services

### Auth Service
- Authentification JWT
- Validation des utilisateurs

### RH Service
- Réception des demandes de paiement RH
- Notification de validation/rejet

### Stock Service
- Réception des demandes d'achat
- Notification de validation/rejet

### Coordinateur Service
- Validation des demandes de décaissement

## Installation

1. Installer les dépendances:
```bash
pip install -r requirements.txt
```

2. Configurer les variables d'environnement (.env)

3. Migrations:
```bash
python manage.py makemigrations
python manage.py migrate
```

4. Créer un superutilisateur:
```bash
python manage.py createsuperuser
```

5. Lancer le serveur:
```bash
python manage.py runserver 0.0.0.0:8000
```

## Docker

Construction:
```bash
docker build -t finance_service .
```

Exécution:
```bash
docker run -p 8004:8000 finance_service
```

## Tâches Celery

- `check_pending_decashment_requests` - Vérifie les demandes en attente
- `update_budget_alerts` - Alertes budgétaires
- `generate_monthly_report` - Rapport mensuel
- `cleanup_old_notifications` - Nettoyage des notifications
- `sync_payment_status` - Synchronisation des paiements

Lancer Celery:
```bash
celery -A finance_service worker --loglevel=info
celery -A finance_service beat --loglevel=info
```

## Tests

```bash
python manage.py test
```

## Documentation API

Swagger UI: http://localhost:8004/swagger/
ReDoc: http://localhost:8004/redoc/
