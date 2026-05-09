# Complete Deployment Setup Guide

This guide walks you through deploying the BAPS Attendance app to **Render** (backend) and **Vercel** (frontend) with automated CI/CD.

---

## Step 1: Prepare GitHub Repository

Ensure your project is pushed to GitHub with this folder structure:
```
BAPS_APP/
├── attendance-system/     (Flask backend)
├── baps-frontend/         (React/Vite frontend)
├── .github/workflows/     (CI/CD pipelines)
└── DEPLOYMENT.md
```

Push all changes to the `main` branch:
```powershell
git add .
git commit -m "Add deployment configuration"
git push origin main
```

---

## Step 2: Deploy Backend to Render

### 2.1 Create Render Account
- Visit [render.com](https://render.com)
- Sign up and connect your GitHub account

### 2.2 Create Web Service
1. Dashboard → "New +" → "Web Service"
2. Select your GitHub repo
3. Choose `attendance-system` as the root directory
4. Set:
   - **Name**: `baps-api` (or preferred name)
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app --bind 0.0.0.0:$PORT`

### 2.3 Set Environment Variables
In Render dashboard, go to Service → Environment:
```
DATABASE_URL=postgresql://user:password@host:5432/dbname
FLASK_ENV=production
```

> **Note**: You need a PostgreSQL database. Use Render's free PostgreSQL or connect your own.

### 2.4 Get API Key & Service ID
- Go to **Account Settings** → **API Tokens** → Create new token → Copy it
- Go back to your service → Copy the **Service ID** from the URL

### 2.5 Add to GitHub Secrets
1. Go to GitHub repo → **Settings** → **Secrets and variables** → **Actions**
2. Add:
   - `RENDER_API_KEY`: Your Render API token
   - `RENDER_SERVICE_ID`: Your service ID

---

## Step 3: Deploy Frontend to Vercel

### 3.1 Create Vercel Account
- Visit [vercel.com](https://vercel.com)
- Sign up with GitHub

### 3.2 Import Project
1. Dashboard → "Import Project"
2. Select your GitHub repo
3. Vercel auto-detects Vite settings
4. **Root Directory**: `baps-frontend`
5. Build Command: `npm run build` (default)
6. Output: `dist` (default)

### 3.3 Set Environment Variables
In Vercel project settings → Environment Variables:
```
VITE_API_BASE=https://your-render-service.onrender.com
```
(Replace with your actual Render backend URL)

### 3.4 Get Deployment Tokens
1. Go to Vercel **Account Settings** → **Tokens** → Create token → Copy it
2. From project URL, extract **Org ID** and **Project ID**:
   - URL: `vercel.com/{org-id}/{project-id}`

### 3.5 Add to GitHub Secrets
1. GitHub repo → **Settings** → **Secrets and variables** → **Actions**
2. Add:
   - `VERCEL_TOKEN`: Your Vercel API token
   - `VERCEL_ORG_ID`: Your Vercel organization ID
   - `VERCEL_PROJECT_ID`: Your project ID

---

## Step 4: Configure Frontend to Call Backend API

Edit `baps-frontend/src/lib/api/client.ts`:
```typescript
const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:5000';

export const client = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json'
  }
});
```

Then in `baps-frontend/.env.production`:
```
VITE_API_BASE=https://your-render-service.onrender.com
```

---

## Step 5: Set Up Database

### Option A: Use Render Postgres
1. In Render dashboard, create a new PostgreSQL database
2. Copy the connection string
3. Add to backend environment: `DATABASE_URL`

### Option B: Use External Postgres
- If you have an existing PostgreSQL, use its connection string

### Initialize Database
The Flask app auto-creates tables. First deployment will initialize the schema.

---

## Step 6: Verify Deployment

### Backend Health Check
```bash
curl https://your-render-service.onrender.com/api/members
# Should return: {"status": "success", "data": [...]}
```

### Frontend URL
Visit: `https://your-vercel-project.vercel.app`

---

## Step 7: Set Up CORS

Backend (`attendance-system/app.py`) already has `CORS(app)` configured. If needed, restrict:
```python
CORS(app, origins=['https://your-vercel-project.vercel.app'])
```

---

## Automated CI/CD Workflow

Once GitHub Actions secrets are set:

1. **Push to `main` branch** → GitHub Actions triggers
2. **Backend changes** (`attendance-system/`) → Renders deploys to Render
3. **Frontend changes** (`baps-frontend/`) → Vercel deploys automatically (Vercel native integration)

Check logs:
- Render: Dashboard → Service → Logs
- Vercel: Dashboard → Project → Deployments
- GitHub Actions: Repo → Actions tab

---

## Troubleshooting

### Backend won't start
- Check logs in Render
- Ensure `DATABASE_URL` is set
- Verify `requirements.txt` includes all dependencies

### Frontend blank page
- Check browser console for API errors
- Verify `VITE_API_BASE` environment variable
- Ensure backend URL is correct

### CORS errors
- Add backend URL to Render CORS origins
- Or use permissive CORS for testing: `CORS(app)`

### Database connection fails
- Verify PostgreSQL is running and accessible
- Check connection string format
- Test locally first

---

## Quick Local Testing

### Backend
```powershell
cd attendance-system
python -m venv venv
venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py
```

### Frontend
```bash
cd baps-frontend
npm install
npm run dev
```

---

## Rollback Steps

### Render
- Dashboard → Service → Deploys → Select previous version → Redeploy

### Vercel
- Dashboard → Project → Deployments → Select previous → Promote to Production

---

## Next Steps
- Monitor logs regularly
- Set up error tracking (Sentry, etc.)
- Configure backups for PostgreSQL
- Add rate limiting if needed
- Scale services as traffic grows

Enjoy your deployed app! 🚀
