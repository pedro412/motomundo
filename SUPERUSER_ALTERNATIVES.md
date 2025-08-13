# 🔧 Manual Superuser Creation Methods

## The Railway CLI Issue

The `railway run` command is having issues. Here are alternative methods:

## ✅ Method 1: Environment Variables (Automated)

1. **Add these variables in Railway dashboard**:
   ```
   DJANGO_SUPERUSER_USERNAME=admin
   DJANGO_SUPERUSER_EMAIL=admin@motomundo.com
   DJANGO_SUPERUSER_PASSWORD=MotomundoAdmin2025!
   ```

2. **Commit and push the updated Procfile**:
   ```bash
   git add .
   git commit -m "Add superuser creation to release process"
   git push origin main
   ```

3. **Redeploy in Railway** - the superuser will be created automatically.

## ✅ Method 2: Railway Web Console

1. Go to your Railway project dashboard
2. Click on your service
3. Go to the "Console" tab
4. Run:
   ```python
   python manage.py shell
   ```
5. In the shell, run:
   ```python
   from django.contrib.auth.models import User
   User.objects.create_superuser('admin', 'admin@motomundo.com', 'MotomundoAdmin2025!')
   exit()
   ```

## ✅ Method 3: Direct Database Access

If Railway provides database access:
1. Connect to your PostgreSQL database
2. Insert the superuser record directly

## 🎯 Recommended: Use Method 1

I've updated your Procfile to automatically create the superuser on deployment. Just:

1. Set the environment variables in Railway
2. Push your code changes
3. The superuser will be created on next deployment

**Login Details:**
- Username: `admin`
- Email: `admin@motomundo.com`  
- Password: `MotomundoAdmin2025!`
- URL: `https://motomundo-production.up.railway.app/admin/`
