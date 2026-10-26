# Person 2 — Career Recommendation AI/ML

This folder contains only the Career Recommendation module. It does not include the skill-gap or learning-roadmap implementation, and it does not change any teammate's files.

## What it does

1. Takes a student's skills. It accepts strings such as `["Python", "SQL"]`, Skill objects such as `[{"name": "Python"}]`, or a SkillProfile-style dictionary such as `{"skills": [{"name": "Python"}]}`.
2. Normalizes common skill aliases.
3. Converts the skills into numerical binary features.
4. Trains a Logistic Regression classifier to rank career roles.
5. Combines model confidence with required-skill coverage to produce a `fit` score from 0 to 100.
6. Returns `role`, `fit`, and `reason`, which match the shape of Person 4's `Career` type.

## Files

- `career_recommendation.py` — main function and `CareerRecommender` wrapper.
- `train_model.py` — builds training examples and trains/saves the model.
- `preprocessing.py` — normalizes skills and accepts the profile input shapes.
- `evaluate.py` — sample recommendation runs.
- `data/career_profiles.json` — this module's own career/skill profiles.
- `requirements.txt` — required Python packages.

The saved model (`career_model.joblib`) is created when `train_model.py` runs. If it is missing, the recommendation function trains it automatically.

## Backend usage

```python
from career_recommendation import recommend_careers

profile = {
    "skills": [
        {"name": "Python", "level": "intermediate"},
        {"name": "SQL", "level": "beginner"},
        {"name": "Pandas"}
    ],
    "experience_years": 0,
    "education": "Undergraduate"
}

results = recommend_careers(profile, top_k=5)
print(results)
```

Example output shape:

```json
[
  {
    "role": "Data Analyst",
    "fit": 73,
    "reason": "Matched skills: sql, python. Skills to build: ..."
  }
]
```

The numerical score will depend on the trained model and input. `fit` is a ranking score, not a probability or guarantee.

## Training and deployment

For a deployment or GitHub workflow, install the dependencies and train the model:

```bash
python -m pip install -r requirements.txt
python train_model.py
```

The model can also train automatically the first time `recommend_careers()` is called if no saved model exists. A deployment should have permission to write the model file, or it should train during its build/startup step.

Run examples with:

```bash
python evaluate.py
```

## Important model limitation

The dataset has career skill profiles, not real students paired with verified career outcomes. To demonstrate actual training without inventing real-world labels, this project creates simulated incomplete skill profiles from the career profiles and trains a Logistic Regression classifier to associate those profiles with career labels. This is a trained ML prototype, but it has not been validated on real students. The `fit` score is a ranking score, not a real-world probability or measured accuracy.

## Integration boundary

This module does not integrate Person 3's roadmap code or Person 4's frontend. It only provides a Python recommendation function with a `Career`-compatible output shape (`role`, `fit`, `reason`). Teammates can call or wrap it during their own integration work.
