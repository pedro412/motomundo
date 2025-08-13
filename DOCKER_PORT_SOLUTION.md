# 🔧 Docker CMD and $PORT Variable Solutions

## The Root Problem

Docker's `CMD` instruction doesn't interpret shell variables like `$PORT` when using the **exec form** (array format). This causes Railway deployment failures.

## ❌ What Doesn't Work

```dockerfile
# This DOESN'T work - exec form doesn't interpret $PORT
CMD ["gunicorn", "motomundo.wsgi:application", "--bind", "0.0.0.0:$PORT"]
```

## ✅ Solution Options

### Option 1: Shell Form (Simple)
```dockerfile
# Use shell form - gets interpreted by /bin/sh
CMD gunicorn motomundo.wsgi:application --bind 0.0.0.0:$PORT --workers 3
```

### Option 2: Explicit Shell with Exec Form
```dockerfile
# Use explicit shell with exec form
CMD ["/bin/bash", "-c", "gunicorn motomundo.wsgi:application --bind 0.0.0.0:${PORT:-8000} --workers 3"]
```

### Option 3: Startup Script (Recommended) ⭐
```dockerfile
# Copy startup script and make it executable
COPY scripts/railway-start /app/scripts/railway-start
RUN chmod +x /app/scripts/railway-start

# Use the script as CMD
CMD ["/app/scripts/railway-start"]
```

## 🎯 Our Implementation

We've implemented **Option 3** (startup script) because it:
- ✅ Provides the most control and flexibility
- ✅ Includes proper error handling and logging
- ✅ Works reliably across different platforms
- ✅ Allows for complex startup logic if needed
- ✅ Is easier to debug and maintain

## Files Updated

### 1. Dockerfile
- Updated CMD to use `/app/scripts/railway-start`
- Added script copying and permission setting

### 2. scripts/railway-start
```bash
#!/bin/bash
set -e

echo "🚀 Starting MotoMundo on Railway..."
echo "🔧 PORT: ${PORT:-8000}"

exec gunicorn motomundo.wsgi:application --bind 0.0.0.0:$PORT --workers 2
```

### 3. Procfile (for Railway)
```
release: python manage.py migrate && python manage.py collectstatic --noinput
web: ./scripts/railway-start
```

## ✅ Problem Solved

The `$PORT` variable is now properly handled in both:
- **Docker containers** (via Dockerfile CMD)
- **Railway deployments** (via Procfile)

Both use the same reliable startup script approach! 🚀
