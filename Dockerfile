FROM python:3.11-slim

WORKDIR /app

# Copier et installer les dépendances
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copier les fichiers sources
COPY . .

# Port pour le serveur web
EXPOSE 8000

# Lancer le serveur web
CMD ["python", "run_web.py"]
