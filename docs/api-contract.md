# API contract (FastAPI service, called by the Next.js app)

Set `AI_BACKEND_URL`. All bodies are JSON unless noted. Types live in `frontend/lib/types.ts`.

## POST /resume/analyze (Member 3), multipart
Fields: `file` (PDF/DOCX, images also work), `user_id`. Unreadable files return **422** `{"detail": "message for the user"}`. Returns **SkillProfile**:
```json
{"user_id":"...","skills":[{"name":"Python","level":"intermediate","category":"language"}],
 "experience_years":2,"education":"B.Tech CSE","domains":["web"],"summary":"..."}
```
Use canonical skill names from `frontend/lib/skills.ts` (e.g. "React", not "ReactJS").

## POST /careers/recommend (Member 2)
Body: SkillProfile. Returns `[{"role":"Backend Developer","fit":74,"reason":"..."}]` (top 3).

## POST /gap/analyze (NOT USED)
The website computes the job gap itself (`frontend/lib/matching.ts`) because it reads the real job text. The backend does not implement this route. Kept here only for reference.

### (reference) shape
Body: `{"profile": SkillProfile, "job": {id,title,company,location,description,url}}`. Returns **SkillGap**:
```json
{"score":55,"matched":[{"name":"Python","weight":2}],
 "partial":[{"name":"Django","weight":1.5,"via":"Flask"}],
 "missing":[{"name":"Docker","weight":1.5}]}
```
Order `missing` by importance (highest weight first).

## POST /roadmap/generate (Member 4)
Body: `{"job": {...}, "gap": SkillGap}`. Returns **RoadmapPlan**:
```json
{"weeks":[{"week":1,"skill":"Docker","topics":["..."],"project":"...",
 "resources":[{"title":"Docker docs","url":"https://docs.docker.com"}]}]}
```
Each week's `skill` must be a name from `gap.missing` or `gap.partial`; the match % rises when that week is ticked.

## Notes
- Optional auth: if the backend has `BACKEND_API_KEY`, every request must send `X-API-Key` with that value (the frontend does this from `AI_BACKEND_KEY`).
- `GET /health` returns `{"status":"ok"}` (use it for the host's health check and to wake a sleeping free-tier server).
- Skill names are normalised to `frontend/lib/skills.ts` inside `backend/adapters.py`.
