# Service Stock - API REST

Service de gestion de stock pour le système de gestion interne.

## Fonctionnalités

### Gestion des Magasins
- CRUD des districts
- CRUD des magasins (warehouses)
- Association magasin-district

### Gestion des Articles de Stock
- CRUD des catégories de stock
- CRUD des articles de stock
- Suivi des quantités disponibles
- Gestion des seuils min/max
- Détection des articles périmés
- Alertes de réapprovisionnement (stock bas)

### Mouvements de Stock
- **Entrée de stock** : Réception de marchandises
- **Sortie de stock** : Distribution/Consommation
- **Transfert inter-magasin** : Déplacement entre magasins
- Historique complet des mouvements
- Validation par responsable de stock

### Demandes et Processus
- **Demandes de transfert** : Magasinier → Responsable Stock
- **Demandes d'achat** : Responsable Stock → Service Finance
- **Vérification de disponibilité inter-magasin**
- **Inventaires périodiques**

### Permissions et Rôles

#### Magasinier
- Voir les stocks de son magasin
- Gérer entrées/sorties de stock
- Créer demandes de réapprovisionnement
- Effectuer inventaires
- Demander ajustements de stock

#### Responsable Stock
- Toutes les permissions Magasinier
- CRUD magasins et catégories
- Vérifier disponibilité inter-magasin
- Approuver/rejeter demandes de transfert
- Créer demandes d'achat
- Consulter tous les journaux d'audit

## API Endpoints

### Districts
- `GET /api/stock/districts/` - Liste des districts
- `POST /api/stock/districts/` - Créer un district
- `GET /api/stock/districts/{id}/` - Détails d'un district
- `PUT /api/stock/districts/{id}/` - Modifier un district
- `DELETE /api/stock/districts/{id}/` - Supprimer un district

### Magasins
- `GET /api/stock/warehouses/` - Liste des magasins
- `POST /api/stock/warehouses/` - Créer un magasin (Responsable Stock)
- `GET /api/stock/warehouses/{id}/` - Détails d'un magasin
- `PUT /api/stock/warehouses/{id}/` - Modifier un magasin
- `GET /api/stock/warehouses/{id}/stock-items/` - Articles d'un magasin

### Catégories
- `GET /api/stock/categories/` - Liste des catégories
- `POST /api/stock/categories/` - Créer une catégorie

### Articles de Stock
- `GET /api/stock/items/` - Liste des articles
- `POST /api/stock/items/` - Créer un article
- `GET /api/stock/items/{id}/` - Détails d'un article
- `PUT /api/stock/items/{id}/` - Modifier un article
- `GET /api/stock/items/low-stock/` - Articles en stock bas
- `GET /api/stock/items/expired/` - Articles périmés
- `POST /api/stock/items/{id}/check-availability/` - Vérifier disponibilité inter-magasin

### Mouvements de Stock
- `GET /api/stock/movements/` - Liste des mouvements
- `POST /api/stock/movements/` - Créer un mouvement
- `GET /api/stock/movements/{id}/` - Détails d'un mouvement
- `POST /api/stock/movements/{id}/approve/` - Approuver un mouvement (Responsable)

### Demandes de Transfert
- `GET /api/stock/transfer-requests/` - Liste des demandes
- `POST /api/stock/transfer-requests/` - Créer une demande
- `GET /api/stock/transfer-requests/{id}/` - Détails d'une demande
- `POST /api/stock/transfer-requests/{id}/approve/` - Approuver (Responsable)
- `POST /api/stock/transfer-requests/{id}/reject/` - Rejeter (Responsable)

### Demandes d'Achat
- `GET /api/stock/purchase-requests/` - Liste des demandes
- `POST /api/stock/purchase-requests/` - Créer une demande
- `GET /api/stock/purchase-requests/{id}/` - Détails d'une demande
- `POST /api/stock/purchase-requests/{id}/validate/` - Valider (Responsable)

### Inventaires
- `GET /api/stock/inventory-checks/` - Liste des inventaires
- `POST /api/stock/inventory-checks/` - Créer un inventaire
- `GET /api/stock/inventory-checks/{id}/` - Détails d'un inventaire

### Audit Logs
- `GET /api/stock/audit-logs/` - Journaux d'audit (Responsable uniquement)

## Authentification

Ce service utilise JWT pour l'authentification. Le token doit être obtenu depuis le service d'authentification.

**Header requis :**
```
Authorization: Bearer <votre_token_jwt>
```

## Démarrage

### Avec Docker
```bash
docker-compose up stock_service stock_db
```

### En local
```bash
cd stock_service
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver 8002
```

## Variables d'environnement

Voir le fichier `.env` :
- `SECRET_KEY` : Clé secrète Django
- `DEBUG` : Mode debug
- `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT` : Configuration PostgreSQL
- `JWT_SIGNING_KEY` : Clé de signature JWT (doit être identique au service auth)
- `AUTH_SERVICE_URL` : URL du service d'authentification

## Documentation API

Swagger UI : http://localhost:8002/swagger/
ReDoc : http://localhost:8002/redoc/

## Flux de travail

### Processus de Réapprovisionnement

1. **Magasinier** constate un stock bas
2. **Magasinier** crée une demande de réapprovisionnement
3. **Responsable Stock** vérifie la disponibilité inter-magasin
4. Si disponible : **Responsable Stock** crée un transfert inter-magasin
5. Si indisponible : **Responsable Stock** crée une demande d'achat → Service Finance

### Processus de Transfert

1. **Magasinier** ou **Responsable** crée une demande de transfert
2. **Responsable Stock** approuve ou rejette
3. Si approuvé : mouvement de stock automatique créé
4. Stocks mis à jour dans les deux magasins

### Processus d'Achat

1. **Responsable Stock** crée une demande d'achat
2. Demande envoyée au **Service Finance**
3. **Service Finance** traite la demande
4. Notification de réception → **Magasinier** effectue l'entrée de stock
