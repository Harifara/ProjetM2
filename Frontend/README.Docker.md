# 🐳 Guide de Déploiement Docker - E.C.A.R.T Frontend

## 📋 Prérequis

- Docker >= 20.10
- Docker Compose >= 2.0
- Node.js 20+ (pour le développement local)

## 🚀 Déploiement

### Option 1: Build et Run Production

```bash
# Build de l'image
docker build -t ecart-frontend:latest .

# Run le container
docker run -d \
  -p 3000:3000 \
  -e VITE_API_URL=http://kong:8000 \
  --name ecart_frontend \
  ecart-frontend:latest
```

### Option 2: Docker Compose (Production)

```bash
# Démarrer le frontend seul
docker-compose -f docker-compose.frontend.yml up -d frontend

# Vérifier les logs
docker-compose -f docker-compose.frontend.yml logs -f frontend
```

### Option 3: Docker Compose (Développement avec Hot-Reload)

```bash
# Démarrer en mode développement
docker-compose -f docker-compose.frontend.yml up -d frontend_dev

# Vérifier les logs
docker-compose -f docker-compose.frontend.yml logs -f frontend_dev
```

## 🔧 Configuration

### Variables d'Environnement

| Variable | Description | Défaut | Exemple |
|----------|-------------|--------|---------|
| `VITE_API_URL` | URL de l'API Gateway Kong | `http://localhost:8000` | `http://kong:8000` |

### Configuration Runtime vs Build-time

L'application supporte deux modes de configuration:

1. **Build-time** (fichier `.env`)
   - Utilisé pendant `npm run build`
   - Intégré dans le bundle JavaScript

2. **Runtime** (script Docker)
   - Injecté via `/config.js` au démarrage du container
   - Permet de changer la config sans rebuild
   - **Recommandé pour production**

## 🏗️ Architecture Multi-Stage

Le `Dockerfile` utilise une build multi-stage:

```
Stage 1 (builder): Node.js 20 Alpine
  └─> npm install & build
  
Stage 2 (production): Nginx Alpine
  └─> Copy build artifacts
  └─> Nginx server optimisé
```

### Avantages:
- ✅ Image finale légère (~25MB)
- ✅ Sécurité accrue (pas de dépendances de build)
- ✅ Performance optimale avec Nginx

## 📦 Intégration avec le Stack Complet

Pour intégrer avec votre `docker-compose.yml` principal:

```yaml
services:
  frontend:
    build:
      context: ./Frontend
      dockerfile: Dockerfile
    container_name: ecart_frontend
    ports:
      - "3000:3000"
    environment:
      - VITE_API_URL=http://kong:8000
    depends_on:
      - kong
    restart: unless-stopped
    networks:
      - project_network

networks:
  project_network:
    driver: bridge
```

## 🔍 Vérification

### Health Check

```bash
# Vérifier que le container est en bonne santé
curl http://localhost:3000/health

# Devrait retourner: "healthy"
```

### Logs

```bash
# Voir les logs en temps réel
docker logs -f ecart_frontend

# Voir les 100 dernières lignes
docker logs --tail 100 ecart_frontend
```

## 🛠️ Développement Local

### Sans Docker

```bash
# Installer les dépendances
npm install

# Démarrer le serveur de dev
npm run dev

# Build pour production
npm run build

# Preview du build de production
npm run preview
```

### Avec Docker (Hot-Reload)

```bash
# Utiliser le Dockerfile.dev
docker-compose -f docker-compose.frontend.yml up frontend_dev
```

## 📊 Optimisations Nginx

Le fichier `nginx.conf` inclut:

- ✅ Compression Gzip
- ✅ Cache des assets statiques (1 an)
- ✅ Headers de sécurité (XSS, Frame Options, etc.)
- ✅ Routing SPA (redirections vers index.html)
- ✅ Endpoint /health pour monitoring

## 🐛 Dépannage

### Le container ne démarre pas

```bash
# Vérifier les logs
docker logs ecart_frontend

# Vérifier la configuration
docker exec ecart_frontend cat /etc/nginx/conf.d/default.conf
```

### L'API n'est pas accessible

```bash
# Vérifier la config injectée
docker exec ecart_frontend cat /usr/share/nginx/html/config.js

# Tester la connectivité réseau
docker exec ecart_frontend wget -O- http://kong:8000/api/auth/
```

### Rebuild complet

```bash
# Supprimer l'image et rebuild
docker-compose -f docker-compose.frontend.yml down
docker rmi ecart-frontend:latest
docker-compose -f docker-compose.frontend.yml up --build -d
```

## 📝 Notes de Production

1. **Sécurité**: Assurez-vous de configurer HTTPS en production
2. **Monitoring**: Utilisez le endpoint `/health` pour le monitoring
3. **Logs**: Configurez un système de centralisation des logs (ELK, Loki, etc.)
4. **Resources**: Limitez les resources CPU/Memory du container en production

```yaml
# Exemple de limites de ressources
services:
  frontend:
    deploy:
      resources:
        limits:
          cpus: '0.5'
          memory: 512M
        reservations:
          cpus: '0.25'
          memory: 256M
```
