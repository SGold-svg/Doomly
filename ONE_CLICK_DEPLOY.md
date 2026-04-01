# One-Click Deploy Instructions

## Option 1: Deploy Backend to Railway (Easiest - 2 minutes)

1. Go to **https://railway.app**
2. Sign up with GitHub
3. Click **New Project** → **Deploy from GitHub repo**
4. Select your `doomly` repo
5. Railway will auto-detect it's a Python/Flask app
6. Go to **Settings** → **Variables**
7. Add: `DATABASE_URL = sqlite:///doomly.db` (Railway provides PostgreSQL - use that URL instead)
8. Go to **Settings** → **Start Command**
9. Set: `cd backend && gunicorn app:app --bind 0.0.0.0:$PORT`
10. Wait for deployment... Your backend URL will be like: `https://doomly.railway.app`

---

## Option 2: Deploy Frontend to Vercel (Easiest - 1 minute)

1. Go to **https://vercel.com**
2. Sign up with GitHub
3. Click **Add New** → **Project**
4. Import your `doomly` repo
5. Framework: **Vite**
6. Root Directory: `./frontend`
7. Click **Deploy**
8. You'll get: `https://doomly.vercel.app`

---

## After Both Deployments:

1. Edit `frontend/vercel.json` and update the API URL:
```json
{
  "rewrites": [
    { "source": "/api/(.*)", "destination": "https://YOUR-RAILWAY-URL.railway.app/api/$1" }
  ]
}
```

2. Push changes to GitHub
3. Vercel will auto-redeploy with new API URL

---

## Alternative: Use Render (also free)

**Backend:** https://render.com → New → Web Service → Connect GitHub
**Database:** Render → New → PostgreSQL

**Frontend:** https://vercel.com → New Project → Import doomly repo

---

## GitHub Repo Ready ✓

Your code is committed and ready. Just push to GitHub:
```bash
cd doomly
git remote add origin https://github.com/YOUR_USERNAME/doomly.git
git push -u origin main
```
