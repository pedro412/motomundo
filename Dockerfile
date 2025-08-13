FROM python:3.11-slim AS base
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
RUN apt-get update && apt-get install -y build-essential libpq-dev && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

COPY . .

ARG DJANGO_SETTINGS_MODULE=motomundo.settings
ENV DJANGO_SETTINGS_MODULE=${DJANGO_SETTINGS_MODULE}

# Copy and make startup script executable
COPY scripts/railway-start /app/scripts/railway-start
RUN chmod +x /app/scripts/railway-start

# Ensure entrypoint script executable
RUN chmod +x /app/entrypoint.sh || true

RUN python manage.py collectstatic --noinput || true

EXPOSE 8000
# Use the startup script that properly handles $PORT
CMD ["/app/scripts/railway-start"]
