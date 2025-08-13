# 🚂 Railway Deployment Guide for MotoMundo

## 🚀 Quick Deploy to Railway

### Prerequisites
- [Railway Account](https://railway.app)
- GitHub repo with MotoMundo code
- Railway CLI (optional but recommended)

### Step 1: Prepare Your GitHub Repository

1. **Push your code to GitHub:**
```bash
git add .
git commit -m "Prepare MotoMundo for Railway deployment"
git push origin main
```

### Step 2: Deploy to Railway

#### Option A: Web Dashboard (Easiest)

1. **Go to [Railway.app](https://railway.app) and login**
2. **Click "New Project"**
3. **Select "Deploy from GitHub repo"**
4. **Choose your `motomundo` repository**
5. **Railway will auto-detect it's a Django app**

#### Option B: Railway CLI

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login to Railway
railway login

# In your project directory
railway link
railway up
```

### Step 3: Add PostgreSQL Database

1. **In Railway Dashboard → Add Service → Database → PostgreSQL**
2. **Railway will automatically set `DATABASE_URL` environment variable**

### Step 4: Configure Environment Variables

In Railway Dashboard → Your Project → Variables, add:

#### Required Variables:
```bash
DJANGO_SECRET_KEY=your-super-secret-key-here
DEBUG=false
FRONTEND_URL=https://your-app-name.up.railway.app
```

#### Optional Email Variables (for SendGrid):
```bash
SENDGRID_API_KEY=your-sendgrid-api-key
FROM_EMAIL=noreply@yourdomain.com
```

#### Optional Redis Variables (if using Redis):
```bash
# Railway will auto-set REDIS_URL if you add Redis service
```

### Step 5: Deploy Settings

Railway will automatically:
- Detect `requirements.txt` and install dependencies
- Run migrations via `railway-entrypoint.sh`
- Serve static files with WhiteNoise
- Create admin user (admin/admin123)

### Step 6: Access Your App

1. **Railway will provide a URL like:** `https://motomundo-production.up.railway.app`
2. **Admin panel:** `https://your-url.up.railway.app/admin/`
3. **API docs:** `https://your-url.up.railway.app/api/`

## 🔧 Environment Variables Reference

### Core Django Settings
| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DJANGO_SECRET_KEY` | ✅ | - | Django secret key |
| `DEBUG` | ❌ | false | Debug mode |
| `FRONTEND_URL` | ❌ | Railway URL | Frontend URL for links |

### Database (Auto-configured by Railway)
| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DATABASE_URL` | ✅ | Auto-set | PostgreSQL connection string |

### Email (Optional - for SendGrid)
| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `SENDGRID_API_KEY` | ❌ | - | SendGrid API key |
| `FROM_EMAIL` | ❌ | noreply@motomundo.com | From email address |

### Redis (Optional)
| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `REDIS_URL` | ❌ | Auto-set | Redis connection string |

## 🏍️ Post-Deployment Checklist

### ✅ Basic Functionality
- [ ] App loads at Railway URL
- [ ] Admin panel accessible at `/admin/`
- [ ] Health check works at `/health/`
- [ ] API endpoints respond at `/api/`

### ✅ Test Core Features
- [ ] Login to admin panel (admin/admin123)
- [ ] Create a test club and chapter
- [ ] Test invitation link creation
- [ ] Verify database is persisting data

### ✅ Optional Features
- [ ] Test email invitations (if SendGrid configured)
- [ ] Upload club logo (test media files)
- [ ] Test achievement system

## 🔧 Troubleshooting

### Common Issues:

**1. Build Failures:**
- Check `requirements.txt` has all dependencies
- Verify Python version compatibility
- Check Railway build logs

**2. Database Connection:**
- Ensure PostgreSQL service is added
- Check `DATABASE_URL` is set automatically
- Verify migrations ran successfully

**3. Static Files:**
- WhiteNoise should handle static files automatically
- Check `STATIC_ROOT` and `STATIC_URL` settings
- Run `python manage.py collectstatic` locally to test

**4. Environment Variables:**
- Double-check all required variables are set
- Ensure no typos in variable names
- Check Railway Variables tab

### Useful Commands:

```bash
# View Railway logs
railway logs

# Run database migrations manually
railway run python manage.py migrate

# Create superuser manually
railway run python manage.py createsuperuser

# Access Django shell
railway run python manage.py shell
```

## 🚀 Production Optimizations

### Performance:
- Railway automatically handles scaling
- PostgreSQL included with good performance
- WhiteNoise serves static files efficiently

### Security:
- HTTPS enabled by default
- Environment variables secure
- Django security settings enabled in production

### Monitoring:
- Railway provides built-in metrics
- Health check endpoint at `/health/`
- Django admin for data management

## 💰 Cost Estimates

**Railway Starter (Recommended for MCs):**
- **$5/month** - Web service + PostgreSQL
- **Includes:** 512MB RAM, 1GB storage, custom domain
- **Perfect for:** Small to medium MC clubs

**Add-ons:**
- **Redis:** +$1/month (for caching)
- **SendGrid:** $0-15/month (for emails)

**Total typical cost:** $5-20/month depending on features

## 🎉 Your MotoMundo is Ready!

Once deployed, your motorcycle club management system will be live with:

- ✅ **Club & Member Management**
- ✅ **Achievement System** 
- ✅ **Invitation System** (Email + Links)
- ✅ **Mobile-Responsive Admin**
- ✅ **WhatsApp Integration Ready**
- ✅ **Spanish Language Support**

**Perfect for real motorcycle clubs! 🏍️**
