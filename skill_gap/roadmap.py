"""Compatibility entry point for generating a personalized learning roadmap.

The skill-gap logic lives in skill_gap.py so the project has one source of truth.
"""
try:
    from .skill_gap import generate_roadmap as _generate_roadmap
except ImportError:  # supports running this file directly from the project folder
    from skill_gap import generate_roadmap as _generate_roadmap


def generate_roadmap(career, user_skills=None, display=True):
    """Generate a roadmap for `career`; user_skills may be a list or a level dict.

    For dictionaries, any non-empty level other than 'none' or '0' counts as a
    known skill. An empty value, 'none', or '0' means the skill is not known.
    """
    if isinstance(user_skills, dict):
        known = [
            skill for skill, level in user_skills.items()
            if level is not None and str(level).strip().casefold() not in ("", "0", "none", "not known")
        ]
    else:
        known = user_skills or []
    result = _generate_roadmap(known, career, display=display)
    if result is None:
        print(f"Career '{career}' was not found in the career dataset.")
    return result


if __name__ == "__main__":
    generate_roadmap("Data Scientist", ["Python", "SQL", "Pandas"])
