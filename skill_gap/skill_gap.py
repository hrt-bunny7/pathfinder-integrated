"""Skill-gap analysis and personalized learning roadmap generation.

This module uses the project's JSON files as its source of truth. Career `skills`
are treated as required skills; `skill_types` is used for roadmap categorization.
"""

import json
import re
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"


def load_json(filename):
    path = DATA_DIR / filename
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


career_skills = load_json("career_skills.json")
prerequisites = load_json("prerequisites.json")
foundational_skills = load_json("foundational_skills.json")
learning_resources = load_json("learning_resources.json")


def _key(value):
    """Normalize a skill/career name for reliable case/spacing comparisons."""
    return re.sub(r"\s+", " ", str(value)).strip().casefold()


def normalize_skills(skills):
    """Return normalized skill names; accepts lists, sets, or dicts of skills."""
    if skills is None:
        return set()
    if isinstance(skills, dict):
        skills = skills.keys()
    if isinstance(skills, str):
        skills = [skills]
    return {_key(skill) for skill in skills if _key(skill)}


def _find_name(name, mapping):
    """Find the original key in a mapping, ignoring case and extra whitespace."""
    target = _key(name)
    for original in mapping:
        if _key(original) == target:
            return original
    return None


def _prerequisite_list(skill):
    actual = _find_name(skill, prerequisites)
    if actual is None:
        return []
    value = prerequisites[actual]
    if isinstance(value, dict):
        value = value.get("prerequisites", [])
    return value if isinstance(value, list) else []


def get_required_skills(career):
    """Return a career's required skills, or None when the career is unknown."""
    actual_career = _find_name(career, career_skills)
    if actual_career is None:
        return None
    skills = career_skills[actual_career].get("skills", {})
    if isinstance(skills, dict):
        return list(skills.keys())
    if isinstance(skills, list):
        return list(skills)
    return []


def get_similar_careers(new_career):
    """Return dataset roles sharing meaningful words with an unknown role name."""
    ignored = {"engineer", "developer", "analyst", "specialist", "scientist",
               "architect", "and", "of", "the", "for", "in", "with"}

    def words(value):
        return {word for word in re.findall(r"[a-z0-9+#.]+", _key(value))
                if word not in ignored}

    target = words(new_career)
    if not target:
        return []
    matches = []
    for career in career_skills:
        if target.intersection(words(career)):
            matches.append(career)
    return matches


def estimate_skills_for_new_career(new_career):
    """Estimate likely skills from similar roles; this is only a rough estimate."""
    similar = get_similar_careers(new_career)
    if not similar:
        return None

    estimated = {}
    for career in similar:
        data = career_skills[career]
        skills = data.get("skills", {})
        if isinstance(skills, dict):
            for skill, score in skills.items():
                try:
                    score = float(score)
                except (TypeError, ValueError):
                    continue
                estimated[skill] = max(estimated.get(skill, score), score)
        elif isinstance(skills, list):
            for skill in skills:
                estimated.setdefault(skill, 1)
    return estimated or None


def find_skill_gaps(student_skills, career):
    """Return required career skills the student does not already know."""
    required = get_required_skills(career)
    if required is None:
        return None
    known = normalize_skills(student_skills)
    return [skill for skill in required if _key(skill) not in known]


def find_prerequisites(skill, student_skills):
    """Return all unknown prerequisites of a skill, in prerequisite-first order."""
    known = normalize_skills(student_skills)
    missing = []
    visited = set()
    active = set()

    def visit(current):
        actual = _find_name(current, prerequisites) or str(current).strip()
        key = _key(actual)
        if key in known or key in visited:
            return
        if key in active:
            raise ValueError(f"Circular prerequisite detected involving: {actual}")
        active.add(key)
        for prereq in _prerequisite_list(actual):
            visit(prereq)
        active.remove(key)
        visited.add(key)
        missing.append(actual)

    visit(skill)
    return missing


def get_complete_skill_gap(student_skills, career):
    """Return required skill gaps plus all missing prerequisites, without duplicates."""
    missing = find_skill_gaps(student_skills, career)
    if missing is None:
        return None
    known = normalize_skills(student_skills)
    complete = []
    included = set()
    for skill in missing:
        for item in find_prerequisites(skill, student_skills):
            key = _key(item)
            if key not in known and key not in included:
                complete.append(item)
                included.add(key)
    return complete


def order_skills(skills):
    """Topologically order a list of skills so prerequisites appear first."""
    canonical = {}
    for skill in skills:
        canonical.setdefault(_key(skill), skill)
    ordered, visited, active = [], set(), set()

    def visit(skill):
        key = _key(skill)
        if key in visited:
            return
        if key in active:
            raise ValueError(f"Circular prerequisite detected involving: {skill}")
        active.add(key)
        for prereq in _prerequisite_list(skill):
            matching = canonical.get(_key(prereq))
            if matching is not None:
                visit(matching)
        active.remove(key)
        visited.add(key)
        ordered.append(skill)

    for skill in skills:
        visit(skill)
    return ordered


def get_skill_depth(skill, visited=None):
    """Return prerequisite depth (zero for a skill with no prerequisites)."""
    visited = set() if visited is None else set(visited)
    key = _key(skill)
    if key in visited:
        return 0
    visited.add(key)
    required = _prerequisite_list(skill)
    if not required:
        return 0
    return 1 + max((get_skill_depth(item, visited) for item in required), default=0)


def categorize_skills(ordered_skills, career=None):
    """Group roadmap skills into Foundation, Core, Advanced, and Optional."""
    categories = {"Foundation": [], "Core": [], "Advanced": [], "Optional": []}
    actual_career = _find_name(career, career_skills) if career else None
    career_data = career_skills.get(actual_career, {}) if actual_career else {}
    types = career_data.get("skill_types", {})
    essential = normalize_skills(types.get("essential", []))
    specialization = normalize_skills(types.get("specialization", []))
    optional = normalize_skills(types.get("optional", []))
    implicit = normalize_skills(types.get("implicit", []))
    foundational = normalize_skills(
        foundational_skills.keys() if isinstance(foundational_skills, dict)
        else foundational_skills
    )

    for skill in ordered_skills:
        key = _key(skill)
        if key in foundational:
            category = "Foundation"
        elif key in essential or key in implicit:
            category = "Core"
        elif key in specialization:
            category = "Advanced"
        elif key in optional:
            category = "Optional"
        else:
            depth = get_skill_depth(skill)
            category = "Foundation" if depth <= 1 else "Core" if depth <= 2 else "Advanced"
        categories[category].append(skill)
    return categories


def get_learning_resources(skill):
    """Get resources for a skill, allowing case-insensitive skill names."""
    actual = _find_name(skill, learning_resources)
    return learning_resources.get(actual, {}) if actual else {}


def build_roadmap(categories):
    """Build structured roadmap data suitable for a UI/API as well as printing."""
    return {
        category: [
            {"skill": skill, "resources": get_learning_resources(skill)}
            for skill in skills
        ]
        for category, skills in categories.items()
    }


def display_roadmap(roadmap, career):
    """Print a readable version of a structured roadmap."""
    print("\n" + "=" * 55)
    print("PERSONALIZED CAREER ROADMAP")
    print(f"Career: {career}")
    print("=" * 55)
    for category, entries in roadmap.items():
        print(f"\n{category.upper()}\n" + "-" * 55)
        if not entries:
            print("No skills in this category.")
            continue
        for index, entry in enumerate(entries, start=1):
            skill, info = entry["skill"], entry["resources"]
            print(f"\n{index}. {skill}")
            print("   Level:", info.get("level", "Not specified"))
            for resource in info.get("resources", []):
                print("   -", resource.get("name", "Learning resource"))
                if resource.get("url"):
                    print("     ", resource["url"])
            if info.get("practice"):
                print("   Practice:", info["practice"])
            if info.get("project"):
                print("   Project:", info["project"])
    print("\n" + "=" * 55 + "\nEND OF ROADMAP\n" + "=" * 55)


def generate_roadmap(student_skills, career, display=True):
    """Return a personalized roadmap; optionally print it. Unknown roles return None."""
    missing = get_complete_skill_gap(student_skills, career)
    if missing is None:
        return None
    ordered = order_skills(missing)
    categories = categorize_skills(ordered, career)
    roadmap = build_roadmap(categories)
    if display:
        display_roadmap(roadmap, career)
    return roadmap


if __name__ == "__main__":
    demo_known_skills = ["Python", "SQL", "Pandas"]
    generate_roadmap(demo_known_skills, "Data Scientist")
