"""
Unit & Integration Tests for Person 1 (Resume & Profile Analysis)
Validates:
1. Resume text parsing & information extraction
2. Canonical skill standardization & deduplication
3. Output schema matching exact specification:
   {
       "education": "B.Tech CSE",
       "skills": ["Python", "SQL", "Pandas", "Machine Learning"],
       "experience": 1,
       "projects": 2
   }
4. Manual skills and interests merging
"""

import json
import os
import sys

# Ensure package modules can be imported
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from profile_analyzer import ResumeProfileAnalyzer
from skill_dictionary import clean_and_standardize_skills, standardize_skill_name


SAMPLE_RESUME_TEXT = """
ALEX MERCER
Email: alex.mercer@example.com | Phone: +1 234 567 890 | GitHub: github.com/alexm

EDUCATION
National Institute of Technology
Bachelor of Technology in Computer Science and Engineering (B.Tech CSE)
CGPA: 8.9 / 10 | 2020 - 2024

TECHNICAL SKILLS
- Programming Languages: Python, SQL, C++, Java
- Libraries & Tools: Pandas, NumPy, Scikit-Learn, TensorFlow
- Concepts: Machine Learning, Data Structures, Algorithms

WORK EXPERIENCE
Data Science Intern | Apex Analytics
June 2023 - June 2024 (1 year of experience)
- Built predictive customer churn pipelines using Python, SQL, and Pandas.
- Implemented Machine Learning models reaching 92% classification accuracy.

PROJECTS
1. AI Resume & Profile Analyzer
   - Developed an automated NLP-based resume parsing tool using Python and PyMuPDF.
   - Extracted and normalized candidate skills, education history, and experience.

2. Smart E-Commerce Product Recommendation Engine
   - Designed collaborative filtering models in Python with Pandas and Scikit-Learn.
   - Deployed recommendation APIs serving 10,000+ monthly active users.

CERTIFICATIONS
- DeepLearning.AI Machine Learning Specialization
- AWS Certified Cloud Practitioner
"""


def test_standardization():
    print("[TEST] Testing Skill Standardization...")
    raw_skills = ["py", "pandas ", "MACHINE LEARNING", "sql", "k8s", "c++", "ReactJS", "py"]
    standardized = clean_and_standardize_skills(raw_skills)
    
    expected = ["Python", "Pandas", "Machine Learning", "SQL", "Kubernetes", "C++", "React"]
    print(f"  Input:  {raw_skills}")
    print(f"  Output: {standardized}")
    assert standardized == expected, f"Expected {expected}, got {standardized}"
    print("  [OK] Standardization PASSED!\n")


def test_profile_extraction():
    print("[TEST] Testing Profile Analysis on Sample Resume...")
    analyzer = ResumeProfileAnalyzer(SAMPLE_RESUME_TEXT)
    summary = analyzer.get_summary()

    print("  Extracted Summary:")
    print(json.dumps(summary, indent=4))

    # Assertions
    assert "B.Tech CSE" in summary["education"], f"Unexpected education: {summary['education']}"
    assert "Python" in summary["skills"], "Python missing from skills"
    assert "SQL" in summary["skills"], "SQL missing from skills"
    assert "Pandas" in summary["skills"], "Pandas missing from skills"
    assert "Machine Learning" in summary["skills"], "Machine Learning missing from skills"
    assert summary["experience"] == 1, f"Expected experience 1, got {summary['experience']}"
    assert summary["projects"] == 2, f"Expected projects 2, got {summary['projects']}"
    print("  [OK] Profile extraction matches required specification!\n")


def test_manual_entry():
    print("[TEST] Testing Manual Skills & Interests Entry...")
    analyzer = ResumeProfileAnalyzer(SAMPLE_RESUME_TEXT)
    
    # Add manual skills (including aliases and duplicates)
    analyzer.add_manual_skills(["FastAPI", "docker", "py", "AWS"])
    analyzer.add_manual_interests(["Generative AI", "Distributed Systems"])

    summary = analyzer.get_summary()
    detailed = analyzer.get_detailed_profile()

    print(f"  Updated Skills: {summary['skills']}")
    print(f"  Updated Interests: {detailed['interests']}")

    assert "FastAPI" in summary["skills"], "FastAPI not added"
    assert "Docker" in summary["skills"], "Docker not normalized/added"
    assert "AWS" in summary["skills"], "AWS not added"
    # Ensure "Python" wasn't duplicated by "py"
    assert summary["skills"].count("Python") == 1, "Duplicate Python skill found"
    assert "Generative AI" in detailed["interests"], "Interest not added"
    print("  [OK] Manual entry and normalization PASSED!\n")


def test_text_cleaning():
    print("[TEST] Testing OCR & PDF Text Cleaning...")
    from document_extractor import clean_extracted_text

    raw_noisy_ocr = (
        "|  EDUCATION \xa0\xa0\n"
        "Bachelor of Tech-\n nology in Computer Science\n"
        "▪ Machine Learning \n"
        "▪ Deep Learning\n"
        "| EXPERIENCE |\n"
        "Soft- \n ware Engineer\n"
    )

    cleaned = clean_extracted_text(raw_noisy_ocr)
    print("  Cleaned OCR Output:\n" + "\n".join("    " + l for l in cleaned.split("\n")))

    assert "Technology" in cleaned, "Hyphenated word unwrapping failed"
    assert "Software" in cleaned, "Hyphenated word unwrapping failed for Software"
    assert "- Machine Learning" in cleaned, "Bullet normalization failed"
    assert "\xa0" not in cleaned, "Non-breaking space was not cleaned"
    print("  [OK] OCR & PDF Text Cleaning PASSED!\n")


if __name__ == "__main__":
    print("=" * 60)
    print("RUNNING PERSON 1 (CAREER GUIDANCE RESUME ANALYZER) TEST SUITE")
    print("=" * 60)
    test_text_cleaning()
    test_standardization()
    test_profile_extraction()
    test_manual_entry()
    print("=" * 60)
    print("ALL TESTS PASSED SUCCESSFULLY! (100% READY FOR INTEGRATION)")
    print("=" * 60)
