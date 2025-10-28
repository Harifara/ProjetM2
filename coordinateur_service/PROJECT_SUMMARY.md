# Service Coordinateur - Résumé du Projet

## 🎯 Objectif

Service REST API microservice pour la gestion et validation des demandes de décaissement dans un système de gestion interne d'entreprise.

## 📋 Fonctionnalités principales

### 1. Validation de décaissements
- Réception des demandes de décaissement (achats, paiements, transferts)
- Validation ou rejet des demandes avec commentaires
- Suivi du statut (en attente, validé, rejeté)
- Gestion des montants et justifications

### 2. Consultation d'opérations
- Enregistrement des consultations effectuées
- Historique des opérations consultées par chaque coordinateur
- Traçabilité complète des accès

### 3. Tableau de bord et statistiques
- Vue d'ensemble des demandes par statut
- Totaux par type de demande
- Montants en attente, validés et rejetés
- Statistiques agrégées

### 4. Journal d'audit
- Enregistrement automatique de toutes les actions
- Capture de l'IP et du user-agent
- Historique complet et non modifiable
- Filtrage et recherche avancés

## 🏗️ Architecture technique

### Stack technologique
- **Framework** : Django 5.0.1
- **API** : Django REST Framework 3.14.0
- **Base de données** : PostgreSQL 15
- **Authentification** : JWT (Simple JWT)
- **Documentation** : drf-yasg (Swagger/OpenAPI)
- **Containerisation** : Docker

### Dépendances
- Service d'authentification (auth_service) pour la gestion des utilisateurs
- Communication inter-services via JWT partagé
- Base de données PostgreSQL dédiée

## 📊 Modèles de données

### DecashmentValidation
Demandes de validation avec statut, montant, raison et traçabilité complète.

### AuditLog
Journal d'audit immutable de toutes les actions du coordinateur.

### OperationView
Enregistrement des consultations d'opérations.

## 🔐 Sécurité

- ✅ Authentification JWT obligatoire
- ✅ Permissions basées sur les rôles (coordinateur uniquement)
- ✅ Audit complet de toutes les actions
- ✅ Validation des données entrantes
- ✅ CORS configuré
- ✅ Protection CSRF

## 🚀 Déploiement

### Docker Compose
```bash
docker-compose up -d coordinateur_db coordinateur_service
```

### Ports
- **Service** : 8002
- **Base de données** : 5435 (externe), 5432 (interne)

### URLs
- API : http://localhost:8002/api/coordinateur/
- Admin : http://localhost:8002/admin/
- Swagger : http://localhost:8002/swagger/
- ReDoc : http://localhost:8002/redoc/

## 📡 Endpoints principaux

| Endpoint | Méthode | Description |
|----------|---------|-------------|
| `/validations/` | GET, POST | Gestion des validations |
| `/validations/{id}/validate/` | POST | Valider/Rejeter |
| `/validations/pending/` | GET | Demandes en attente |
| `/validations/validated/` | GET | Demandes validées |
| `/validations/rejected/` | GET | Demandes rejetées |
| `/validations/dashboard/` | GET | Statistiques |
| `/operations/` | GET, POST | Consultations |
| `/audit-logs/` | GET | Journaux d'audit |

## 🔄 Workflow

1. **Réception** : Une demande arrive d'un autre service (RH, Stock, Finance)
2. **Consultation** : Le coordinateur examine les détails
3. **Décision** : Validation ou rejet avec commentaires
4. **Notification** : Le service d'origine est notifié
5. **Audit** : L'action est journalisée automatiquement

## 📦 Structure des fichiers

```
coordinateur_service/
├── coordinateur/              # Application principale
│   ├── migrations/
│   ├── admin.py
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   ├── urls.py
│   ├── permissions.py
│   ├── middleware.py
│   ├── utils.py
│   └── tests.py
├── coordinateur_service/      # Configuration Django
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── .env                       # Variables d'environnement
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── manage.py
└── Documentation/
    ├── README.md
    ├── ARCHITECTURE.md
    ├── API_EXAMPLES.md
    └── PROJECT_SUMMARY.md
```

## 🧪 Tests

### Exécuter les tests
```bash
python manage.py test coordinateur
```

### Tests inclus
- Tests de création de validation
- Tests de validation/rejet
- Tests de permissions
- Tests d'audit logging

### Script de test API
```bash
python test_api.py
```

## 📝 Documentation

- **README.md** : Guide d'installation et utilisation
- **ARCHITECTURE.md** : Documentation technique détaillée
- **API_EXAMPLES.md** : Exemples de requêtes cURL
- **PROJECT_SUMMARY.md** : Ce fichier

## 🔧 Configuration

### Variables d'environnement essentielles

```env
SECRET_KEY=              # Clé secrète Django
DB_NAME=coordinateur_db  # Nom de la base
DB_HOST=coordinateur_db  # Hôte PostgreSQL
JWT_SIGNING_KEY=         # Clé JWT partagée
AUTH_SERVICE_URL=        # URL du service auth
```

## 🎨 Conventions de code

- PEP 8 pour Python
- Commentaires en français
- Noms de variables explicites
- Documentation des fonctions complexes

## 📈 Métriques de qualité

- ✅ Couverture de tests : Base établie
- ✅ Documentation complète
- ✅ Code modulaire et maintenable
- ✅ Séparation des responsabilités
- ✅ Gestion des erreurs

## 🔮 Évolutions possibles

1. **Notifications temps réel** : WebSockets pour alertes instantanées
2. **Workflows avancés** : Validation multi-niveaux
3. **Rapports** : Génération de rapports PDF/Excel
4. **Analytics** : Tableaux de bord avancés
5. **Mobile** : API optimisée pour applications mobiles
6. **ML** : Détection d'anomalies automatique

## 👥 Rôles et permissions

### Coordinateur (seul rôle autorisé)
- Consulter toutes les demandes
- Valider les demandes
- Rejeter les demandes
- Voir les statistiques
- Consulter les journaux d'audit
- Enregistrer des consultations

## 🔗 Intégrations

### Service d'authentification
- Validation JWT
- Récupération des rôles utilisateurs
- Vérification des permissions

### Service Finance
- Réception des notifications de validation
- Déclenchement des paiements/achats

### Service RH / Stock
- Envoi des demandes de décaissement
- Réception des notifications de rejet

## 📞 Support

Pour toute question ou problème :
1. Consulter la documentation (README.md, ARCHITECTURE.md)
2. Vérifier les exemples d'API (API_EXAMPLES.md)
3. Exécuter le script de test (test_api.py)
4. Consulter les logs Docker

## ✅ Checklist de démarrage

- [ ] Cloner le repository
- [ ] Configurer le fichier .env
- [ ] Lancer Docker Compose
- [ ] Vérifier les migrations
- [ ] Créer un utilisateur coordinateur (via service auth)
- [ ] Tester l'API avec test_api.py
- [ ] Consulter la documentation Swagger
- [ ] Vérifier les logs d'audit

## 🎉 Conclusion

Le service coordinateur est un microservice robuste et sécurisé qui centralise la validation des décaissements. Il s'intègre parfaitement dans l'architecture microservices du système de gestion interne et offre une traçabilité complète de toutes les opérations.
