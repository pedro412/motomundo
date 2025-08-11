# Motomundo

Django project with PostgreSQL and Redis using Docker.

## Quick Start

1. Build and start the services:
   ```sh
   docker-compose up --build
   ```
2. Run migrations and create a superuser:
   ```sh
   docker-compose exec web python manage.py migrate
   docker-compose exec web python manage.py createsuperuser
   ```
3. Access the app at http://localhost:8000
