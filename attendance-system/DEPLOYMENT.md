Render + Vercel deployment guide

Overview
- Frontend: deploy `baps-frontend` to Vercel (Vite app).
- Backend: deploy `attendance-system` (Flask) to Render as a Web Service (Gunicorn).

Backend (Render)
1. Ensure `requirements.txt` contains `gunicorn` (done).
2. `Procfile` present with: `web: gunicorn app:app --bind 0.0.0.0:$PORT` (done).
3. Recommended Render service settings:
   - Runtime: Python 3.x
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn app:app --bind 0.0.0.0:$PORT`
4. Environment variables (set in Render dashboard):
   - `DATABASE_URL` — your Postgres URL (e.g. `postgresql://user:pass@host:5432/dbname`).
   - Any other secrets (e.g., `FLASK_ENV`, `SENTRY_DSN`).
5. Database: use Render Postgres or external Postgres and set `DATABASE_URL`.
6. Logs & health: Render shows service logs; enable health checks if desired.

Frontend (Vercel)
1. Vercel auto-detects Vite. Connect the GitHub repo and select `baps-frontend` root.
2. Build Command: `npm run build` (default). Output directory: `dist` (Vite default).
3. Environment variables: if the frontend calls backend APIs, set `VITE_API_BASE` or configure `src/lib/api/client.ts` accordingly.

Local testing commands
- Backend (local sqlite/postgres):
```powershell
# from attendance-system
python -m venv venv
venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py
```
- Frontend (local):
```bash
# from baps-frontend
npm install
npm run dev
```

Notes & next steps
- CI/CD: you can add GitHub Actions to run tests and push to Render/Vercel on merges.
- If you prefer a single host, Render supports both frontend and backend.
- I can now: create a `vercel.json` file, add a Render `render.yaml`, or scaffold GitHub Actions for automated deploys — which would you like next?
