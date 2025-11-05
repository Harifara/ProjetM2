# ==========================
# 📦 Base Python image
# ==========================
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Prevent Python from writing pyc files
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system dependencies (lightweight)
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       libpq-dev gcc netcat-traditional \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip, setuptools, wheel
RUN pip install --upgrade pip setuptools wheel

# Copy only requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy project code
COPY . .

# Entrypoint script
RUN chmod +x /app/entrypoint.sh

# Default port for Django
EXPOSE 8000

# Entrypoint
CMD ["sh", "-c", "./entrypoint.sh"]
