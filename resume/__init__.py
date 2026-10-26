"""
Resume & Profile Analysis Package (Career Guidance Project - Person 1)
"""

from .skill_dictionary import (
    CANONICAL_SKILLS,
    SKILL_ALIASES,
    standardize_skill_name,
    clean_and_standardize_skills
)
from .document_extractor import (
    extract_resume_text,
    extract_text_from_pdf,
    extract_text_from_image,
    clean_extracted_text
)
from .profile_analyzer import ResumeProfileAnalyzer

__all__ = [
    "ResumeProfileAnalyzer",
    "extract_resume_text",
    "extract_text_from_pdf",
    "extract_text_from_image",
    "clean_extracted_text",
    "standardize_skill_name",
    "clean_and_standardize_skills",
    "CANONICAL_SKILLS",
    "SKILL_ALIASES"
]
