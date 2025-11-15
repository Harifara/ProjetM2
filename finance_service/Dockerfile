# ==========================
# 📦 Base Python image
# ==========================
FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Installer les dépendances système
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       libpq-dev gcc netcat-traditional \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Mettre à jour pip, setuptools et wheel
RUN pip install --upgrade pip setuptools wheel

# Copier requirements et installer les dépendances Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copier le reste du code source
COPY . .

# Rendre le script d’entrée exécutable
RUN chmod +x /app/entrypoint.sh

# Exposer le port
EXPOSE 8000

# ⚡ ENTRYPOINT pour exécuter le script de démarrage
ENTRYPOINT ["/app/entrypoint.sh"]
