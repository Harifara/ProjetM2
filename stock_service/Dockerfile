# ==========================
# 📦 Base Python image
# ==========================
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Prevents Python from writing pyc files to disk
ENV PYTHONDONTWRITEBYTECODE 1
# Ensures stdout/stderr are unbuffered
ENV PYTHONUNBUFFERED 1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libpq-dev gcc netcat-traditional && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy project code
COPY . .

# Entrypoint script
RUN chmod +x /app/entrypoint.sh

# Default port for Django
EXPOSE 8000

CMD ["sh", "-c", "./entrypoint.sh"]
