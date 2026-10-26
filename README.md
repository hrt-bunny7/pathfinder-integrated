# Pathfinder: AI Career Assistant (integrated)

```
career-assistant/
├── frontend/   Next.js 14 website (auth, jobs, matching, dashboard)  -> deploy on Vercel
├── backend/    FastAPI service joining the teammates' modules         -> deploy on Render/Railway (Docker)
│   ├── main.py        3 routes + /health
│   ├── adapters.py    converts each module's output to the website's JSON
│   ├── resume/        Member 3: resume reading + skill extraction
│   ├── careers/       Member 2: career recommendation model
│   ├── skill_gap/     Member 4: prerequisites + learning resources (+ data/)
│   └── tests/         integration tests
└── docs/api-contract.md
```

## How the pieces fit
| Step on the website | Who does it |
|---|---|
| Upload resume -> skills | Member 3 (`/resume/analyze`) |
| Career suggestions on the dashboard | Member 2 (`/careers/recommend`) |
| Job list, match %, skill gap | Web app (`frontend/lib/matching.ts`) |
| Learning roadmap | Member 4 (`/roadmap/generate`) |

No `AI_BACKEND_URL` set = demo mode (mock profile and careers, local roadmap). With it set, the site uses the real backend, and an unreadable resume shows an error instead of fake data.

## 1. Supabase (once)
1. Create a project at supabase.com. 2. SQL Editor -> run `frontend/supabase/schema.sql`.
3. Authentication -> Providers: enable Email (and Google if wanted). For quick testing turn "Confirm email" off.
4. Copy the Project URL and the anon key (Settings -> API).

## 2. Run everything on your computer
**Backend** (Python 3.10+):
```bash
cd backend
python -m venv .venv && source .venv/bin/activate     # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
python -m unittest discover -s tests -v               # should say OK
uvicorn main:app --reload --port 8000
```
Open http://localhost:8000/health -> `{"status":"ok"}`.

**Frontend** (Node 18+):
```bash
cd frontend
cp .env.example .env.local        # fill in the Supabase URL + anon key, and:
# AI_BACKEND_URL=http://localhost:8000
npm install
npm run dev                       # http://localhost:3000
```
Test: sign up -> upload a PDF/DOCX resume -> dashboard shows your skills and careers -> Jobs -> open a job -> build roadmap.
If something looks like mock data, read the **terminal running `npm run dev`** for `[backend]` lines.

## 3. Deploy
**Backend on Render** (or Railway):
1. Push this repo to GitHub.
2. Render -> New -> Web Service -> pick the repo -> Root Directory `backend`, Runtime **Docker**.
3. Optional env var `BACKEND_API_KEY` = a long random string.
4. After deploy, open `https://YOUR-SERVICE.onrender.com/health`.
   Free instances sleep when idle: open /health before a demo to wake it (about 30-60 s).

**Frontend on Vercel:**
1. New Project -> same repo -> **Root Directory `frontend`**.
2. Environment variables: `NEXT_PUBLIC_SUPABASE_URL`, `NEXT_PUBLIC_SUPABASE_ANON_KEY`, `AI_BACKEND_URL` (the Render URL, no trailing slash), `AI_BACKEND_KEY` (same as `BACKEND_API_KEY`, if you set one), and optionally `ADZUNA_APP_ID`, `ADZUNA_APP_KEY`.
3. Deploy. Env var changes only apply after a redeploy.
4. Supabase -> Authentication -> URL Configuration: add `https://YOUR-APP.vercel.app/auth/callback` to Redirect URLs (and set the Site URL).

## Known limits
- Resume reading is rule-based (keyword dictionary). It finds skills it knows; unusual layouts can be missed.
- Scanned/image resumes need Tesseract (included in the Docker image) and may be less accurate.
- Career model (Member 2) is trained on simulated profiles, so treat `fit` as a ranking, not a prediction.
- Some roadmap links for skills outside Member 4's dataset (`backend/data/extra_resources.json`) were written without internet access. Open them once before presenting.
- Files are limited to 4 MB (Vercel's request limit is about 4.5 MB).
