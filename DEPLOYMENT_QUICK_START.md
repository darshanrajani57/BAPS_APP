# Quick Deployment Checklist

Use this checklist to deploy your BAPS app in ~30 minutes.

## Pre-Deployment (5 min)
- [ ] Ensure code is pushed to GitHub `main` branch
- [ ] `Procfile` exists in `attendance-system/` ✓
- [ ] `gunicorn` added to `requirements.txt` ✓
- [ ] `vercel.json` exists in `baps-frontend/` ✓
- [ ] GitHub Actions workflows in `.github/workflows/` ✓

## Backend Setup on Render (10 min)
- [ ] Create Render account (render.com)
- [ ] Create Web Service → connect GitHub repo
- [ ] Set root directory: `attendance-system`
- [ ] Add environment variable: `DATABASE_URL`
- [ ] Copy `RENDER_SERVICE_ID` from service URL
- [ ] Copy `RENDER_API_KEY` from Account Settings → API Tokens
- [ ] Add both to GitHub Secrets

## Frontend Setup on Vercel (10 min)
- [ ] Create Vercel account (vercel.com)
- [ ] Import GitHub repo → select `baps-frontend` root
- [ ] Add environment variable: `VITE_API_BASE=https://your-render-service.onrender.com`
- [ ] Copy `VERCEL_TOKEN` from Account Settings
- [ ] Copy `VERCEL_ORG_ID` and `VERCEL_PROJECT_ID` from project URL
- [ ] Add all three to GitHub Secrets

## Verify Deployment (5 min)
- [ ] Backend health: `curl https://your-render-service.onrender.com/api/members`
- [ ] Frontend loads: visit `https://your-vercel-project.vercel.app`
- [ ] Check GitHub Actions runs succeeded
- [ ] Test API calls from frontend (check browser console)

---

## GitHub Secrets to Set

1. `RENDER_API_KEY` — from Render Account Settings
2. `RENDER_SERVICE_ID` — from Render service URL
3. `VERCEL_TOKEN` — from Vercel Account Settings
4. `VERCEL_ORG_ID` — from Vercel project URL
5. `VERCEL_PROJECT_ID` — from Vercel project URL

## Important URLs

- **Render Dashboard**: https://dashboard.render.com
- **Vercel Dashboard**: https://vercel.com/dashboard
- **GitHub Secrets**: https://github.com/YOUR_ORG/YOUR_REPO/settings/secrets/actions

---

For detailed setup: see `SETUP_DEPLOYMENT.md`
