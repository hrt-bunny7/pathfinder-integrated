"""Glue between the teammates' modules and the website's JSON contract (docs/api-contract.md).

No web framework is imported here, so everything in this file can be unit-tested directly
(see tests/test_integration.py). main.py only exposes these functions over HTTP.

  Member 3  resume/      -> analyze_resume_bytes()   (resume file  -> SkillProfile)
  Member 2  careers/     -> recommend()              (SkillProfile -> [{role, fit, reason}])
  Member 4  skill_gap/   -> build_roadmap()          ({job, gap}   -> RoadmapPlan)

The website's own skill dictionary (frontend/lib/skills.ts, exported to canonical_skills.json)
is the single source of truth for skill names. Everything is normalised to those names.
"""
from __future__ import annotations

import io
import json
import re
import zipfile
from pathlib import Path
from typing import Any
from urllib.parse import quote
from xml.sax.saxutils import unescape

BASE_DIR = Path(__file__).resolve().parent

# --------------------------------------------------------------------------------------
# Canonical skill names (shared with the frontend)
# --------------------------------------------------------------------------------------
_canon_data = json.loads((BASE_DIR / "canonical_skills.json").read_text(encoding="utf-8"))
SKILLS: dict[str, list[str]] = _canon_data["SKILLS"]

_LOOKUP: dict[str, str] = {}
for _name, _aliases in SKILLS.items():
    _LOOKUP[_name.lower()] = _name
    for _a in _aliases:
        _LOOKUP.setdefault(_a.lower(), _name)

# Spellings produced by Member 3's resume module (or common on resumes) that the website
# dictionary does not list as aliases.
_EXTRA_ALIASES = {
    "apache spark": "Spark",
    "object-oriented programming": "OOP",
    "oops": "OOP",
    "data structures & algorithms": "Data Structures",
    "data structures and algorithms": "Data Structures",
    "algorithms": "Data Structures",
    "computer networks": "Networking",
    "google cloud": "GCP",
    "google cloud platform": "GCP",
    "vue.js": "Vue",
    "express.js": "Express",
    "natural language processing": "NLP",
    "asp.net": ".NET",
    "github": "Git",
    "postgres": "PostgreSQL",
    "scikit learn": "Scikit-learn",
}
for _k, _v in _EXTRA_ALIASES.items():
    _LOOKUP.setdefault(_k, _v)


def canonical_skill(raw: str) -> str | None:
    """'ReactJS' / 'react.js' / 'Express.Js' -> 'React' / 'React' / 'Express'. None if unknown."""
    return _LOOKUP.get(re.sub(r"\s+", " ", str(raw)).strip().lower())


# --------------------------------------------------------------------------------------
# Profile helpers (category / domains / summary)
# --------------------------------------------------------------------------------------
_CATEGORY_SETS = {
    "language": {"Python", "Java", "JavaScript", "TypeScript", "C++", "C", "C#", "Go", "Rust", "PHP",
                 "Kotlin", "Swift", "R", "HTML", "CSS", "Sass", "SQL"},
    "framework": {"React", "Next.js", "Angular", "Vue", "Node.js", "Express", "Django", "Flask", "FastAPI",
                  "Spring Boot", ".NET", "Tailwind CSS", "Bootstrap", "React Native", "Flutter",
                  "REST APIs", "GraphQL", "Microservices"},
    "database": {"MySQL", "PostgreSQL", "MongoDB", "Redis", "Firebase", "Supabase"},
    "tool": {"Git", "Docker", "Kubernetes", "Linux", "CI/CD", "Terraform"},
    "cloud": {"AWS", "Azure", "GCP"},
    "data": {"Machine Learning", "Deep Learning", "NLP", "TensorFlow", "PyTorch", "Scikit-learn", "Pandas",
             "NumPy", "Data Analysis", "Data Visualization", "Power BI", "Tableau", "Excel", "Spark",
             "Hadoop", "Statistics"},
    "concepts": {"Data Structures", "System Design", "OOP", "Testing", "Agile", "Networking", "Cybersecurity"},
    "design": {"Figma", "UI/UX"},
    "mobile": {"Android", "iOS"},
    "soft": {"Communication", "Problem Solving"},
}
_CATEGORY_OF = {skill: cat for cat, skills in _CATEGORY_SETS.items() for skill in skills}

_DOMAIN_SETS = {
    "web": {"React", "HTML", "CSS", "JavaScript", "TypeScript", "Next.js", "Node.js", "Angular", "Vue",
            "Express", "Django", "Flask", "FastAPI", "Tailwind CSS", "Bootstrap"},
    "data": {"Pandas", "SQL", "Data Analysis", "Data Visualization", "Power BI", "Tableau", "Excel",
             "Statistics", "NumPy", "Spark", "Hadoop"},
    "ml": {"Machine Learning", "Deep Learning", "NLP", "TensorFlow", "PyTorch", "Scikit-learn"},
    "cloud": {"AWS", "Azure", "GCP", "Docker", "Kubernetes", "Terraform", "CI/CD", "Linux"},
    "mobile": {"Android", "iOS", "React Native", "Flutter", "Kotlin", "Swift"},
}


class ResumeError(ValueError):
    """The uploaded resume could not be read (shown to the user as a message)."""


def _plural(n: int, word: str) -> str:
    return f"{n} {word}" if n == 1 else f"{n} {word}s"


def build_profile(detail: dict[str, Any], user_id: str = "") -> dict[str, Any]:
    """Member 3's detailed profile -> the website's SkillProfile."""
    names: list[str] = []
    seen: set[str] = set()
    for raw in detail.get("skills", []):
        name = canonical_skill(raw) or str(raw).strip()
        if name and name.lower() not in seen:
            seen.add(name.lower())
            names.append(name)

    skills = [{"name": n, "category": _CATEGORY_OF.get(n, "other")} for n in names]
    domains = [d for d, members in _DOMAIN_SETS.items() if len(members & set(names)) >= 2]

    years = int(detail.get("experience_years") or 0)
    projects = int(detail.get("projects_count") or 0)
    education = detail.get("education") or ""
    top = ", ".join(names[:5])
    summary = (
        f"{education or 'Candidate'} with {_plural(years, 'year')} of experience and "
        f"{_plural(projects, 'project')}."
        + (f" Key skills: {top}." if top else "")
        + (f" Main areas: {', '.join(domains)}." if domains else "")
    )
    profile: dict[str, Any] = {
        "user_id": user_id,
        "skills": skills,
        "experience_years": years,
        "education": education,
        "domains": domains,
        "summary": summary,
        # Extra fields (ignored by the current UI, kept for later use)
        "projects_count": projects,
        "certifications": detail.get("certifications", []),
        "interests": detail.get("interests", []),
    }
    return profile


# --------------------------------------------------------------------------------------
# Member 3: resume file -> SkillProfile
# --------------------------------------------------------------------------------------
_IMAGE_EXT = {".png", ".jpg", ".jpeg", ".webp", ".tiff", ".tif", ".bmp"}
MAX_UPLOAD_BYTES = 10 * 1024 * 1024


def extract_text_from_docx(data: bytes) -> str:
    """Plain-text extraction for .docx using only the standard library."""
    try:
        with zipfile.ZipFile(io.BytesIO(data)) as z:
            xml = z.read("word/document.xml").decode("utf-8", errors="ignore")
    except (zipfile.BadZipFile, KeyError) as e:
        raise ResumeError("This DOCX file looks damaged. Try saving it again or upload a PDF.") from e
    xml = re.sub(r"</w:p>", "\n", xml)
    xml = re.sub(r"<w:tab/>", " ", xml)
    xml = re.sub(r"<w:br[^>]*/>", "\n", xml)
    xml = re.sub(r"<[^>]+>", "", xml)
    return unescape(xml)


def _read_resume_text(filename: str, data: bytes) -> str:
    from resume.document_extractor import (  # Member 3
        clean_extracted_text, extract_text_from_image, extract_text_from_pdf,
    )

    ext = Path(filename or "").suffix.lower()
    try:
        if ext == ".pdf":
            return extract_text_from_pdf(data)
        if ext == ".docx":
            return clean_extracted_text(extract_text_from_docx(data))
        if ext in _IMAGE_EXT:
            return extract_text_from_image(data)
    except ResumeError:
        raise
    except ImportError as e:
        raise ResumeError(f"The server is missing a reader for this file type ({e}).") from e
    except Exception as e:  # damaged / encrypted files
        raise ResumeError(f"We could not read this file ({type(e).__name__}). Try a different PDF or DOCX.") from e
    raise ResumeError("Unsupported file type. Upload a PDF or DOCX.")


def analyze_resume_bytes(filename: str, data: bytes, user_id: str = "") -> dict[str, Any]:
    if not data:
        raise ResumeError("The file is empty.")
    if len(data) > MAX_UPLOAD_BYTES:
        raise ResumeError("The file is too large.")

    text = _read_resume_text(filename, data)
    if len(text.strip()) < 30:
        raise ResumeError(
            "No readable text found. If this is a scanned PDF, upload a text-based PDF or a DOCX instead."
        )

    from resume.profile_analyzer import ResumeProfileAnalyzer  # Member 3

    detail = ResumeProfileAnalyzer(text).get_detailed_profile()
    if not detail.get("skills"):
        raise ResumeError(
            "We could not find any known skills in this resume. Add a 'Skills' section and try again."
        )
    return build_profile(detail, user_id)


# --------------------------------------------------------------------------------------
# Member 2: SkillProfile -> careers
# --------------------------------------------------------------------------------------
# Member 2's model uses its own lowercase vocabulary. Translate the website names into it.
_TO_CAREER_VOCAB = {
    "REST APIs": "rest api",
    "NLP": "natural language processing",
    "OOP": "object-oriented programming",
    "UI/UX": "ui design",
}


def _pretty(name: str) -> str:
    name = name.strip()
    return canonical_skill(name) or (name[:1].upper() + name[1:])


def _pretty_reason(reason: str) -> str:
    """Member 2 writes lowercase skill names and a note about ignored skills. Tidy it for the UI."""
    reason = re.sub(r"\s*Unrecognized skills ignored for matching:[^.]*\.", "", reason)

    def fix(m: re.Match) -> str:
        items = [_pretty(x) for x in m.group(2).split(",") if x.strip()]
        return f"{m.group(1)}: {', '.join(items)}."

    return re.sub(r"(Matched skills|Skills to build): ([^.]*)\.", fix, reason).strip()


def recommend(profile: dict[str, Any], top_k: int = 3, min_fit: int = 25) -> list[dict[str, Any]]:
    """Top careers as [{role, fit, reason}]. Empty list if the skills match nothing in the model."""
    from careers.career_recommendation import recommend_careers  # Member 2

    names = []
    for s in (profile or {}).get("skills", []):
        raw = s.get("name") if isinstance(s, dict) else str(s)
        if not raw:
            continue
        canon = canonical_skill(raw) or str(raw)
        names.append(_TO_CAREER_VOCAB.get(canon, canon.lower()))
    if not names:
        return []
    try:
        ranked = recommend_careers({"skills": [{"name": n} for n in names]}, top_k=max(top_k, 5))
    except ValueError:  # none of the skills are in the model's vocabulary
        return []

    cleaned = [{"role": str(r["role"]), "fit": int(r["fit"]), "reason": _pretty_reason(str(r["reason"]))} for r in ranked]
    good = [c for c in cleaned if c["fit"] >= min_fit][:top_k]
    return good or cleaned[:1]  # always show at least the best match


# --------------------------------------------------------------------------------------
# Member 4: {job, gap} -> learning roadmap
# --------------------------------------------------------------------------------------
# Website skill name -> the name used in Member 4's dataset (when they differ)
_TO_GAP_VOCAB = {
    "REST APIs": "REST API",
    "Android": "Android Development",
    "iOS": "iOS Development",
    "UI/UX": "UX Design",
    "Cybersecurity": "Cybersecurity Fundamentals",
    "NLP": "Natural Language Processing",
}
_EXTRA_RESOURCES = {
    k: v for k, v in json.loads((BASE_DIR / "data" / "extra_resources.json").read_text(encoding="utf-8")).items()
    if not k.startswith("_")
}


def _generic_resources(skill: str) -> dict[str, Any]:
    q = quote(skill)
    return {
        "level": "Beginner",
        "resources": [
            {"name": f"{skill} tutorials on YouTube", "type": "Search", "url": f"https://www.youtube.com/results?search_query={q}+full+course"},
            {"name": f"freeCodeCamp: {skill}", "type": "Search", "url": f"https://www.freecodecamp.org/news/search?query={q}"},
            {"name": "roadmap.sh guides", "type": "Guide", "url": "https://roadmap.sh"},
        ],
        "practice": "",
        "project": f"Build a small project that uses {skill} and push it to GitHub.",
    }


def _resources_for(skill: str) -> dict[str, Any]:
    from skill_gap.skill_gap import get_learning_resources  # Member 4

    info = get_learning_resources(_TO_GAP_VOCAB.get(skill, skill))
    if info and info.get("resources"):
        return info
    if skill in _EXTRA_RESOURCES:
        return _EXTRA_RESOURCES[skill]
    return _generic_resources(skill)


def build_roadmap(job: dict[str, Any], gap: dict[str, Any], limit: int = 6) -> dict[str, Any]:
    """One week per skill the user still has to learn. Every week's `skill` comes from the gap,
    so ticking a week raises the match % on the website."""
    from skill_gap.skill_gap import find_prerequisites, order_skills  # Member 4

    targets = sorted(
        list(gap.get("missing", [])) + list(gap.get("partial", [])),
        key=lambda s: -float(s.get("weight", 0)),
    )[:limit]
    names = [t["name"] for t in targets]
    if not names:
        return {"weeks": []}

    to_gap = {n: _TO_GAP_VOCAB.get(n, n) for n in names}
    from_gap = {v.casefold(): k for k, v in to_gap.items()}
    try:  # prerequisites first, otherwise keep the importance order
        ordered = [from_gap.get(g.casefold(), g) for g in order_skills(list(to_gap.values()))]
    except ValueError:
        ordered = names

    known = [_TO_GAP_VOCAB.get(m["name"], m["name"]) for m in gap.get("matched", [])]
    target_keys = {g.casefold() for g in to_gap.values()}

    weeks = []
    for i, skill in enumerate(ordered, start=1):
        info = _resources_for(skill)
        try:
            prereqs = [
                p for p in find_prerequisites(to_gap.get(skill, skill), known)
                if p.casefold() != to_gap.get(skill, skill).casefold() and p.casefold() not in target_keys
            ]
        except ValueError:
            prereqs = []

        res = [r for r in info.get("resources", []) if r.get("url")][:4]
        topics = []
        if prereqs:
            topics.append("Review these prerequisites first: " + ", ".join(prereqs[:4]))
        topics.append(f"Learn the core ideas of {skill}" + (f" ({info['level']} level)" if info.get("level") else ""))
        if info.get("practice"):
            topics.append(info["practice"])
        if res:
            topics.append("Study: " + "; ".join(r.get("name", "Resource") for r in res[:2]))

        weeks.append({
            "week": i,
            "skill": skill,
            "topics": topics,
            "project": info.get("project") or f"Build a small project that uses {skill}.",
            "resources": [{"title": r.get("name", "Learning resource"), "url": r["url"]} for r in res],
        })
    return {"weeks": weeks}


def warmup() -> None:
    """Train/load the careers model once at startup so the first request is fast."""
    from careers.career_recommendation import _load_model  # Member 2

    _load_model()
