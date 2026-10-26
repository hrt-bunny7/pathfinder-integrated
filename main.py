"""Pathfinder AI backend: one FastAPI service for the teammates' modules.

Run locally:   uvicorn main:app --reload --port 8000
Routes:        POST /resume/analyze   (Member 3)   multipart: file, user_id
               POST /careers/recommend (Member 2)  JSON: SkillProfile
               POST /roadmap/generate  (Member 4)  JSON: {job, gap}
               GET  /health

All logic lives in adapters.py. Optional protection: set BACKEND_API_KEY here and
AI_BACKEND_KEY (same value) in the frontend; the frontend then sends it as X-API-Key.
"""
import logging
import os
from contextlib import asynccontextmanager

from fastapi import Body, Depends, FastAPI, File, Form, Header, HTTPException, UploadFile

import adapters

log = logging.getLogger("pathfinder")


@asynccontextmanager
async def lifespan(_app: FastAPI):
    try:
        adapters.warmup()
        log.info("careers model ready")
    except Exception:  # the service still starts; /careers/recommend will report the error
        log.exception("careers model warm-up failed")
    yield


app = FastAPI(title="Pathfinder AI backend", lifespan=lifespan)


def require_key(x_api_key: str | None = Header(default=None)) -> None:
    expected = os.getenv("BACKEND_API_KEY")
    if expected and x_api_key != expected:
        raise HTTPException(status_code=401, detail="Invalid or missing API key")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/resume/analyze", dependencies=[Depends(require_key)])
def resume_analyze(file: UploadFile = File(...), user_id: str = Form("")):
    data = file.file.read(adapters.MAX_UPLOAD_BYTES + 1)
    try:
        return adapters.analyze_resume_bytes(file.filename or "", data, user_id)
    except adapters.ResumeError as e:
        raise HTTPException(status_code=422, detail=str(e))


@app.post("/careers/recommend", dependencies=[Depends(require_key)])
def careers_recommend(profile: dict = Body(...)):
    return adapters.recommend(profile)


@app.post("/roadmap/generate", dependencies=[Depends(require_key)])
def roadmap_generate(payload: dict = Body(...)):
    job = payload.get("job") or {}
    gap = payload.get("gap")
    if not isinstance(gap, dict):
        raise HTTPException(status_code=422, detail="'gap' is required")
    return adapters.build_roadmap(job, gap)
