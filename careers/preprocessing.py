import re

ALIASES = {
    "js": "javascript",
    "reactjs": "react",
    "react.js": "react",
    "py": "python",
    "python3": "python",
    "ml": "machine learning",
    "ai/ml": "machine learning",
    "sklearn": "scikit-learn",
    "node": "node.js",
    "powerbi": "power bi",
    "ux/ui": "ui/ux",
}

def clean_skill(value):
    value = re.sub(r"\s+", " ", str(value).strip().lower())
    return ALIASES.get(value, value)

def extract_skills(profile):
    """Accepts a list of strings, Skill objects, or a SkillProfile-style dictionary."""
    if isinstance(profile, dict):
        values = profile.get("skills", [])
    else:
        values = profile or []

    skills = []
    for item in values:
        if isinstance(item, str):
            name = item
        elif isinstance(item, dict):
            name = item.get("name", "")
        else:
            continue
        cleaned = clean_skill(name)
        if cleaned and cleaned not in skills:
            skills.append(cleaned)
    return skills
