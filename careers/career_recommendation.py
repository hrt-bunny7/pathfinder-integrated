from pathlib import Path
import joblib

try:  # works both as a package (backend) and when run from its own folder
    from .preprocessing import extract_skills, clean_skill
    from .train_model import MODEL_FILE, train_model, load_profiles
except ImportError:
    from preprocessing import extract_skills, clean_skill
    from train_model import MODEL_FILE, train_model, load_profiles

def _load_model():
    if not Path(MODEL_FILE).exists():
        train_model()
    saved = joblib.load(MODEL_FILE)
    return saved["model"], saved["profiles"]

def recommend_careers(profile, top_k=5):
    """
    Input: a list of skill names, Skill objects, or a SkillProfile-style dict.
    Output: list of {role, fit, reason}, compatible with Person 4's Career shape.
    `fit` is a ranking score, not a probability.
    """
    if not isinstance(top_k, int) or isinstance(top_k, bool) or top_k < 1:
        raise ValueError("top_k must be a positive integer.")

    skills = extract_skills(profile)
    if not skills:
        raise ValueError("Provide at least one skill.")

    model, profiles = _load_model()
    profile_by_role = {item["role"]: item for item in profiles}
    known_skills = {clean_skill(skill) for item in profiles for skill in item["skills"]}
    known = [skill for skill in skills if skill in known_skills]
    unknown = [skill for skill in skills if skill not in known_skills]
    if not known:
        raise ValueError(
            "None of the supplied skills match the dataset vocabulary. "
            "Try skills such as Python, SQL, React, Linux, or Machine Learning."
        )

    probabilities = model.predict_proba([" ".join(skills)])[0]
    classes = model.named_steps["classifier"].classes_
    ranked = sorted(zip(classes, probabilities), key=lambda pair: pair[1], reverse=True)

    results = []
    for role, probability in ranked[:min(top_k, len(ranked))]:
        career = profile_by_role[role]
        required = [clean_skill(skill) for skill in career["skills"]]
        matched = [skill for skill in required if skill in known]
        missing = [skill for skill in required if skill not in known]
        coverage = len(matched) / len(required) if required else 0
        # Combine classifier confidence with transparent required-skill coverage.
        score = round(100 * (0.65 * float(probability) + 0.35 * coverage))
        if matched:
            reason = "Matched skills: " + ", ".join(matched[:5]) + "."
        else:
            reason = "The trained model ranked this career highly based on the supplied profile."
        if missing:
            reason += " Skills to build: " + ", ".join(missing[:4]) + "."
        if unknown:
            reason += " Unrecognized skills ignored for matching: " + ", ".join(unknown[:3]) + "."
        results.append({"role": role, "fit": score, "reason": reason})
    return results

class CareerRecommender:
    """Small wrapper for backend integration."""
    def recommend(self, profile, top_k=5):
        return recommend_careers(profile, top_k)
