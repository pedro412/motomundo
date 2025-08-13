# 🔧 Creating Django Superuser on Railway

## Method 1: Railway CLI (Recommended)

1. **Install Railway CLI** (if not already installed):
   ```bash
   npm install -g @railway/cli
   ```

2. **Login and connect to your project**:
   ```bash
   railway login
   railway link
   ```

3. **Create superuser interactively**:
   ```bash
   railway run python manage.py createsuperuser
   ```

4. **Follow the prompts**:
   - Username: `admin` (or your preferred username)
   - Email: your email address
   - Password: create a strong password

## Method 2: Environment Variables + Management Command

1. **Add environment variables in Railway**:
   ```
   DJANGO_SUPERUSER_USERNAME=admin
   DJANGO_SUPERUSER_EMAIL=your-email@example.com
   DJANGO_SUPERUSER_PASSWORD=your-secure-password
   ```

2. **Create a management command** (I'll create this file):
   ```python
   # clubs/management/commands/create_superuser.py
   ```

3. **Add to Procfile release phase**:
   ```
   release: python manage.py migrate && python manage.py collectstatic --noinput && python manage.py create_superuser
   ```

## Method 3: Django Shell (Railway Console)

1. **Open Railway shell**:
   ```bash
   railway run python manage.py shell
   ```

2. **Run Python commands**:
   ```python
   from django.contrib.auth.models import User
   User.objects.create_superuser('admin', 'admin@example.com', 'your-password')
   exit()
   ```

## After Creating Superuser

Visit your admin panel:
```
https://motomundo-production.up.railway.app/admin/
```

Login with your superuser credentials to access the Django admin interface.

## Recommendation

Use **Method 1 (Railway CLI)** as it's the most straightforward and secure approach.
