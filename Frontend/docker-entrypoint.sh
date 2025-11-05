#!/bin/sh

# Remplacer les variables d'environnement dans le fichier de configuration
# Cela permet de configurer l'URL de l'API au runtime plutôt qu'au build time

if [ -z "$VITE_API_URL" ]; then
    export VITE_API_URL="http://localhost:8000"
fi

# Créer un fichier de configuration JavaScript qui sera chargé par l'app
cat <<EOF > /usr/share/nginx/html/config.js
window.ENV = {
    VITE_API_URL: '${VITE_API_URL}'
};
EOF

echo "Configuration runtime injectée:"
echo "VITE_API_URL=${VITE_API_URL}"

# Démarrer nginx
exec "$@"
