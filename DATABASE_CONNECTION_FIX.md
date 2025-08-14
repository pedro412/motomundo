# 🔧 Database Connection Troubleshooting

## The Problem

You're getting database connection errors because the default `settings.py` expects individual database variables (`DJANGO_DB_HOST`, `DJANGO_DB_USER`, etc.), but Railway provides a single `DATABASE_URL`.

## ✅ Solution: Use settings_railway.py

### Step 1: Verify Your Railway Environment Variables

In your Railway **web service** variables, you should have:

```bash
# CRITICAL: This tells Django to use the Railway settings
DJANGO_SETTINGS_MODULE=motomundo.settings_railway

# Database connection (Railway provides this automatically)
DATABASE_URL=${{ Postgres.DATABASE_URL }}

# Required Django settings
DJANGO_SECRET_KEY=your-super-long-secret-key-here
DEBUG=False

# Optional: Superuser creation
DJANGO_SUPERUSER_USERNAME=admin
DJANGO_SUPERUSER_EMAIL=admin@motomundo.com
DJANGO_SUPERUSER_PASSWORD=MotomundoAdmin2025!
```

### Step 2: Check Current Variables

Go to Railway → Your Project → **Web Service** → **Variables** and verify:

1. ✅ `DJANGO_SETTINGS_MODULE=motomundo.settings_railway`
2. ✅ `DATABASE_URL=${{ Postgres.DATABASE_URL }}`
3. ✅ `DJANGO_SECRET_KEY` is set
4. ✅ `DEBUG=False`

### Step 3: How settings_railway.py Works

Your `settings_railway.py` file:
- ✅ Uses `dj_database_url.parse()` to handle `DATABASE_URL`
- ✅ Automatically configures PostgreSQL connection
- ✅ Includes WhiteNoise for static files
- ✅ Has proper production security settings

### Step 4: Common Issues & Fixes

**Issue 1: Wrong Settings Module**
- ❌ `DJANGO_SETTINGS_MODULE=motomundo.settings` (uses individual DB vars)
- ✅ `DJANGO_SETTINGS_MODULE=motomundo.settings_railway` (uses DATABASE_URL)

**Issue 2: Missing DATABASE_URL**
- Ensure PostgreSQL service is added to your Railway project
- Verify `DATABASE_URL=${{ Postgres.DATABASE_URL }}` variable exists

**Issue 3: Case Sensitivity**
- Variable names are case-sensitive
- Use exact case: `DATABASE_URL` not `database_url`

### Step 5: Redeploy After Changes

After setting correct environment variables:
1. Railway will automatically redeploy
2. Check deployment logs for database connection success
3. Look for migration output

### Step 6: Check Deployment Logs

Your logs should show:
```bash
🗄️ Database URL detected: postgresql://user:pass@host:port/db
Running migrations...
Operations to perform:
  Apply all migrations: admin, auth, contenttypes, sessions, clubs
Running migrations:
  Applying contenttypes.0001_initial... OK
  Applying auth.0001_initial... OK
  ...
✅ Superuser admin created successfully!
```

## Quick Fix Checklist

1. ✅ PostgreSQL service added to Railway project
2. ✅ `DJANGO_SETTINGS_MODULE=motomundo.settings_railway`
3. ✅ `DATABASE_URL=${{ Postgres.DATABASE_URL }}`
4. ✅ `DJANGO_SECRET_KEY` set to a long random string
5. ✅ `DEBUG=False`
6. ✅ Redeploy triggered

## Test After Fix

Visit: `https://motomundo-production.up.railway.app/admin/`

You should see the Django admin login page (not an error page)! 🚀
