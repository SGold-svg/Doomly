# Doomly Deployment Guide

A comprehensive guide to deploying Doomly Event Management Platform.

---

## 🚀 Quick Start (Development)

```bash
# 1. Clone and enter directory
cd doomly

# 2. Start with Docker (recommended)
docker-compose up

# Backend: http://localhost:5000
# Frontend: http://localhost:3000
# API: http://localhost:5000/api
# Mail UI: http://localhost:8025
# Database: localhost:5432
```

---

## ☁️ Cloud Deployments

### Option 1: Railway (Recommended - Free Tier Available)

**1. Create Railway Account:**
- Go to [railway.app](https://railway.app)
- Sign up with GitHub

**2. Deploy Backend:**
```bash
# Push to GitHub
git init
git add .
git commit -m "Initial Doomly setup"
git remote add origin https://github.com/YOUR_USERNAME/doomly.git
git push -u origin main

# In Railway dashboard:
# 1. New Project → Deploy from GitHub repo
# 2. Select doomly/backend
# 3. Add Environment Variables:
#    - DATABASE_URL (Railway will provision PostgreSQL)
#    - SECRET_KEY (generate a secure key)
#    - JWT_SECRET_KEY (generate a secure key)
# 4. Deploy!
```

**3. Deploy Frontend (Vercel/Netlify):**
```bash
cd frontend
npm run build
# Deploy dist folder to Vercel/Netlify
```

---

### Option 2: Render (Free Tier Available)

**1. Create Render Account:**
- Go to [render.com](https://render.com)
- Connect your GitHub repo

**2. Deploy:**
```bash
# Push to GitHub first
git push

# In Render dashboard:
# 1. New → Blueprint
# 2. Upload render.yaml
# 3. Connect PostgreSQL (auto-provisioned)
# 4. Deploy!
```

---

### Option 3: Heroku

```bash
# Install Heroku CLI
heroku login

# Create Heroku app
heroku create doomly-api --buildpack heroku/python

# Add PostgreSQL
heroku addons:create heroku-postgresql:hobby-dev

# Set environment variables
heroku config:set SECRET_KEY=your-secret-key
heroku config:set JWT_SECRET_KEY=your-jwt-secret
heroku config:set FLASK_ENV=production

# Deploy
git push heroku main
```

---

### Option 4: VPS (DigitalOcean, Vultr, etc.)

**1. Server Setup:**
```bash
# SSH into your server
ssh root@your-server-ip

# Install Docker
curl -fsSL https://get.docker.com | sh

# Install Docker Compose
apt install docker-compose
```

**2. Clone and Configure:**
```bash
git clone https://github.com/YOUR_USERNAME/doomly.git
cd doomly

# Copy and edit environment
cp backend/.env.example backend/.env
nano backend/.env  # Add your values
```

**3. Deploy with Docker:**
```bash
docker-compose -f docker-compose.prod.yml up -d
```

**4. Setup Nginx + SSL (Let's Encrypt):**
```bash
# Install Nginx
apt install nginx

# Copy Nginx config
cp deployment/nginx.conf /etc/nginx/sites-available/doomly

# Enable site
ln -s /etc/nginx/sites-available/doomly /etc/nginx/sites-enabled/

# Install SSL
apt install certbot python3-certbot-nginx
certbot --nginx -d your-domain.com
```

---

## 📱 Static Hosting (Frontend Only)

### Vercel (Recommended)
```bash
cd frontend
npm i -g vercel
vercel
# Follow prompts, set build command: npm run build
# Set output directory: dist
```

### Netlify
```bash
cd frontend
npm run build
# Drag and drop the 'dist' folder to Netlify
# Or connect via GitHub integration
```

---

## 🔧 Configuration

### Environment Variables

**Backend (.env):**
```env
FLASK_ENV=production
SECRET_KEY=generate-a-64-char-random-string
JWT_SECRET_KEY=generate-another-64-char-random-string
DATABASE_URL=postgresql://user:pass@host:5432/doomly
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
```

### Getting SMTP Working

**Option 1: Gmail (Development)**
1. Enable 2FA on Google account
2. Create App Password: https://myaccount.google.com/apppasswords
3. Use the 16-character app password

**Option 2: Mailgun (Production)**
1. Sign up at mailgun.org
2. Add domain or use sandbox
3. Use SMTP credentials from dashboard

**Option 3: SendGrid**
1. Sign up at sendgrid.com
2. Create API key
3. Use SMTP relay

---

## 🗄️ Database

### PostgreSQL Commands
```bash
# Connect to database
psql $DATABASE_URL

# Run migrations
flask db upgrade

# Create migrations
flask db migrate -m "Your migration message"

# Rollback
flask db downgrade
```

---

## 🔒 Security Checklist

Before going live:

- [ ] Change all default passwords
- [ ] Use strong SECRET_KEY and JWT_SECRET_KEY
- [ ] Enable HTTPS/SSL
- [ ] Set up rate limiting
- [ ] Configure CORS for your domain
- [ ] Enable database SSL connections
- [ ] Set up proper email authentication
- [ ] Review user permissions
- [ ] Enable logging/monitoring
- [ ] Set up backups

---

## 📊 Monitoring

### Health Check Endpoint
```
GET /api/health
```

Returns:
```json
{
  "status": "healthy",
  "app": "Doomly Event Management"
}
```

### Logs
```bash
# Docker
docker-compose logs -f

# Gunicorn (direct)
tail -f /var/log/doomly/error.log
```

---

## 🔄 Updates & Maintenance

```bash
# Pull latest changes
git pull origin main

# Rebuild containers
docker-compose build
docker-compose up -d

# Or for production
docker-compose -f docker-compose.prod.yml up -d
```

---

## 🆘 Troubleshooting

### Database Connection Issues
```bash
# Check DATABASE_URL format
postgresql://user:password@host:5432/database
```

### Email Not Sending
```bash
# Test SMTP
telnet smtp.gmail.com 587
```

### CORS Errors
- Check ALLOWED_ORIGINS includes your frontend URL
- Include trailing slash: `https://example.com/`

---

## 📞 Support

For issues or questions, create an issue on GitHub.

---

**Good luck with your deployment! 🚀**
