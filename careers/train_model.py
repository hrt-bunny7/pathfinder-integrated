import json
import random
from pathlib import Path

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
import joblib

BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "data" / "career_profiles.json"
MODEL_FILE = BASE_DIR / "career_model.joblib"
RANDOM_SEED = 42

def load_profiles():
    with open(DATA_FILE, encoding="utf-8") as file:
        profiles = json.load(file)
    if not profiles:
        raise ValueError("The career dataset is empty.")
    return profiles

def create_training_examples(profiles):
    random.seed(RANDOM_SEED)
    texts, labels = [], []
    for profile in profiles:
        skills = profile["skills"]
        # Simulate incomplete student skill profiles from each career's skill list.
        for _ in range(60):
            count = random.randint(1, max(1, len(skills)))
            selected = random.sample(skills, count)
            # Include some noise to make the training profiles less perfect.
            if random.random() < 0.25:
                other = random.choice(profiles)
                extra = random.choice(other["skills"])
                if extra not in selected:
                    selected.append(extra)
            texts.append(" ".join(selected))
            labels.append(profile["role"])
    return texts, labels

def train_model():
    profiles = load_profiles()
    texts, labels = create_training_examples(profiles)
    model = Pipeline([
        ("vectorizer", CountVectorizer(binary=True, token_pattern=r"(?u)\b[\w.+/#-]+\b")),
        ("classifier", LogisticRegression(max_iter=2000, random_state=RANDOM_SEED))
    ])
    model.fit(texts, labels)
    joblib.dump({"model": model, "profiles": profiles}, MODEL_FILE)
    print(f"Trained model using {len(texts)} generated profiles across {len(profiles)} career roles.")
    print(f"Saved model to: {MODEL_FILE}")
    print("Note: training profiles are simulated, not real student outcome records.")
    return model

if __name__ == "__main__":
    train_model()
