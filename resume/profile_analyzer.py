"""
Profile Analyzer Module for Person 1 (Resume & Profile Analysis)
Extracts structured profile data (Education, Skills, Experience, Projects, Certifications)
from raw resume text, standardizes skills, and merges manual entries.
"""

import re
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple

try:
    import pandas as pd
    HAS_PANDAS = True
except ImportError:
    pd = None
    HAS_PANDAS = False

try:  # works both as a package (backend) and when run from its own folder
    from .skill_dictionary import (
        CANONICAL_SKILLS,
        SKILL_ALIASES,
        clean_and_standardize_skills,
        standardize_skill_name
    )
except ImportError:
    from skill_dictionary import (
        CANONICAL_SKILLS,
        SKILL_ALIASES,
        clean_and_standardize_skills,
        standardize_skill_name
    )


class ResumeProfileAnalyzer:
    """
    Analyzes raw resume text and constructs a structured student profile.
    """

    def __init__(self, raw_text: str = ""):
        self.raw_text: str = raw_text
        self.education: str = "Not Specified"
        self.skills: List[str] = []
        self.experience_years: int = 0
        self.projects_count: int = 0
        self.projects_details: List[str] = []
        self.certifications: List[str] = []
        self.interests: List[str] = []

        if raw_text:
            self.analyze()

    def set_text(self, text: str) -> None:
        """Sets new resume text and triggers re-analysis."""
        self.raw_text = text
        self.analyze()

    def analyze(self) -> None:
        """Runs all extraction tasks on the loaded resume text."""
        self.education = self._extract_education()
        self.skills = self._extract_skills()
        self.experience_years = self._extract_experience()
        self.projects_count, self.projects_details = self._extract_projects()
        self.certifications = self._extract_certifications()

    # -------------------------------------------------------------------------
    # 1. Skill Extraction & Standardization
    # -------------------------------------------------------------------------
    def _extract_skills(self) -> List[str]:
        """
        Extracts technical skills from text using boundary-aware regex matching
        against canonical skills and standardizes them.
        """
        found_skills: List[str] = []
        text_lower = self.raw_text.lower()

        # Isolate skills section if present to boost precision
        skills_section = self._get_section_text(["skills", "technical skills", "core competencies", "technologies"])
        search_corpus = skills_section if skills_section else self.raw_text
        corpus_lower = search_corpus.lower()

        # Sort canonical skills by length descending to match multi-word phrases first
        # e.g., 'machine learning' before 'learning'
        sorted_skills = sorted(CANONICAL_SKILLS.keys(), key=lambda x: len(x), reverse=True)

        matched_keys = set()
        for skill_key in sorted_skills:
            # Special handling for single-letter or short skills (e.g. 'c', 'r')
            if len(skill_key) <= 1:
                # Only match 'C' if it's explicitly written as uppercase C or near programming words
                pattern = r"(?:\b(?:programming in|languages?:?|skills?:?)\s*[^.\n]*\b)C\b|\bC(?:\s*,\s*|\s*\/\s*)(?:C\+\+|Java|Python)\b"
                if re.search(pattern, search_corpus):
                    found_skills.append("C")
                    matched_keys.add(skill_key)
                continue

            # Word boundary regex matching
            escaped_key = re.escape(skill_key)
            # Handle special characters in keys like C++, C#, .NET
            if not skill_key[0].isalnum():
                pattern = r"(?:^|\s)" + escaped_key + r"(?=\s|[,\.;:\)]|$)"
            elif not skill_key[-1].isalnum():
                pattern = r"\b" + escaped_key + r"(?=\s|[,\.;:\)]|$)"
            else:
                pattern = r"\b" + escaped_key + r"\b"

            if re.search(pattern, corpus_lower):
                canonical_name = CANONICAL_SKILLS[skill_key]
                found_skills.append(canonical_name)
                matched_keys.add(skill_key)

        # Standardize and deduplicate
        return clean_and_standardize_skills(found_skills)

    # -------------------------------------------------------------------------
    # 2. Education Extraction
    # -------------------------------------------------------------------------
    def _extract_education(self) -> str:
        """
        Identifies degree and branch/major and formats standard string (e.g., 'B.Tech CSE').
        """
        edu_section = self._get_section_text(["education", "academic background", "academics", "qualifications"])
        search_text = edu_section if edu_section else self.raw_text

        # 1. Degree Patterns
        degree_patterns = [
            (r"\b(?:b\.?tech(?:nology)?|bachelor of technology)\b", "B.Tech"),
            (r"\b(?:b\.?e\.?|bachelor of engineering)\b", "B.E."),
            (r"\b(?:m\.?tech(?:nology)?|master of technology)\b", "M.Tech"),
            (r"\b(?:m\.?e\.?|master of engineering)\b", "M.E."),
            (r"\b(?:b\.?s\.?c?|bachelor of science)\b", "B.S."),
            (r"\b(?:m\.?s\.?c?|master of science)\b", "M.S."),
            (r"\bbca\b", "BCA"),
            (r"\bmca\b", "MCA"),
            (r"\bmba\b", "MBA"),
            (r"\b(?:ph\.?d\.?|doctorate)\b", "Ph.D"),
        ]

        # 2. Major / Branch Patterns
        major_patterns = [
            (r"\b(?:cse|computer science and engineering|computer science & engineering|computer science)\b", "CSE"),
            (r"\b(?:it|information technology)\b", "IT"),
            (r"\b(?:data science|ai & ml|artificial intelligence)\b", "Data Science"),
            (r"\b(?:ece|electronics and communication|electronics & communication)\b", "ECE"),
            (r"\b(?:eee|electrical and electronics)\b", "EEE"),
            (r"\b(?:mechanical engineering|mech)\b", "Mechanical"),
            (r"\b(?:civil engineering)\b", "Civil"),
        ]

        found_degree = None
        for pattern, degree_name in degree_patterns:
            if re.search(pattern, search_text, re.IGNORECASE):
                found_degree = degree_name
                break

        found_major = None
        for pattern, major_name in major_patterns:
            if re.search(pattern, search_text, re.IGNORECASE):
                found_major = major_name
                break

        if found_degree and found_major:
            return f"{found_degree} {found_major}"
        elif found_degree:
            return found_degree
        elif found_major:
            return f"Degree in {found_major}"

        return "B.Tech CSE" if "computer" in search_text.lower() else "Bachelor's Degree"

    # -------------------------------------------------------------------------
    # 3. Experience Extraction
    # -------------------------------------------------------------------------
    def _extract_experience(self) -> int:
        """
        Extracts total years of experience as an integer.
        Checks for explicit duration statements, calculates year differences from date ranges,
        or counts distinct employment/internship roles.
        """
        exp_section = self._get_section_text(["experience", "work experience", "employment", "internships"])
        search_text = exp_section if exp_section else self.raw_text

        # A. Look for direct statements like "2 years of experience", "1+ year experience"
        direct_match = re.search(r"(\d+(?:\.\d+)?)\+?\s*(?:years?|yrs?)(?:\s+of)?\s+experience", search_text, re.IGNORECASE)
        if direct_match:
            try:
                years = float(direct_match.group(1))
                return max(1, round(years))
            except ValueError:
                pass

        # B. Calculate total span from year ranges (e.g., 2022 - 2023, 2021 - Present)
        current_year = datetime.now().year
        year_ranges = re.findall(r"\b(20\d\d)\s*(?:-|to|–)\s*(20\d\d|present|current)\b", search_text, re.IGNORECASE)

        total_span = 0
        if year_ranges:
            for start, end in year_ranges:
                start_yr = int(start)
                end_yr = current_year if end.lower() in ["present", "current"] else int(end)
                span = max(0, end_yr - start_yr)
                total_span += span
            if total_span > 0:
                return total_span

        # C. Count distinct company / internship mentions in experience section
        internship_count = len(re.findall(r"\b(?:intern|internship|developer|engineer|analyst)\b", search_text, re.IGNORECASE))
        if exp_section and internship_count > 0:
            return max(1, min(internship_count, 2))

        return 0

    # -------------------------------------------------------------------------
    # 4. Projects Extraction
    # -------------------------------------------------------------------------
    def _extract_projects(self) -> Tuple[int, List[str]]:
        """
        Extracts project titles/items and returns the integer count and detail list.
        """
        proj_section = self._get_section_text(["projects", "academic projects", "personal projects", "key projects"])
        if not proj_section:
            # Check if there are explicit project lines with github links
            direct_matches = re.findall(r"(?i)(?:^|\n)\s*(?:[•\*\-–]|\d+\.)?\s*([A-Za-z0-9\s]{4,40})\s*[-–:]\s*(?:https?:\/\/|github\.com)", self.raw_text)
            if direct_matches:
                return len(direct_matches), direct_matches
            return 0, []

        # 1. Numbered projects: e.g. "1. AI Resume Scanner", "2. Smart Recommendation Engine"
        numbered_projects = re.findall(
            r"(?:^|\n)\s*(?:\d+[\.\)]|Project\s+\d+[:\-]|\b(?:I|II|III|IV|V)[\.\)])\s*([^\n]+)",
            proj_section,
            re.IGNORECASE
        )
        if numbered_projects:
            titles = [p.strip() for p in numbered_projects if len(p.strip()) > 3]
            if titles:
                return len(titles), titles

        # 2. Check for distinct project title lines vs sub-bullet detail descriptions
        lines = [line.strip() for line in proj_section.split("\n") if line.strip()]
        action_verb_prefix = re.compile(
            r"^([•\*\-–]\s*)?(developed|built|designed|created|implemented|extracted|engineered|"
            r"maintained|led|analyzed|optimized|trained|deployed|integrated|worked|utilized|used|"
            r"collaborated|formulated|evaluated|researched)\b",
            re.IGNORECASE
        )

        detected_titles = []
        for line in lines:
            # Skip bullet descriptions starting with action verbs
            if action_verb_prefix.search(line):
                continue
            # Skip pure URL / GitHub links or tech tags lines
            if re.match(r"^(github\.com|http|tools?:|technologies?:|tech\s+stack:)", line, re.IGNORECASE):
                continue
            # Candidate project title line
            cleaned_line = re.sub(r"^([•\*\-–\d+\.]\s*)+", "", line).strip()
            # Filter out date-only or short lines
            if 5 < len(cleaned_line) < 80 and not cleaned_line.endswith("."):
                if not re.match(r"^(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec|\d{4})", cleaned_line, re.IGNORECASE):
                    detected_titles.append(cleaned_line)

        if detected_titles:
            return len(detected_titles), detected_titles

        # Fallback count within projects section
        keyword_matches = re.findall(r"\b(?:project|system|application|platform|tracker|portal|analyzer)\b", proj_section, re.IGNORECASE)
        fallback_count = max(len(keyword_matches) // 2, 1 if "project" in proj_section.lower() else 0)
        return min(max(fallback_count, 1), 6), []

    # -------------------------------------------------------------------------
    # 5. Certifications Extraction
    # -------------------------------------------------------------------------
    def _extract_certifications(self) -> List[str]:
        """
        Extracts recognized certificates and licenses.
        """
        cert_section = self._get_section_text(["certifications", "certificates", "licenses & certifications"])
        search_text = cert_section if cert_section else self.raw_text

        known_cert_keywords = [
            "AWS Certified", "Azure Fundamentals", "Google Cloud Certified",
            "Coursera", "DeepLearning.AI", "HackerRank", "Udemy", "Oracle Certified",
            "Certified Kubernetes", "TensorFlow Developer Certificate"
        ]

        found_certs = []
        for kw in known_cert_keywords:
            if re.search(r"\b" + re.escape(kw) + r"\b", search_text, re.IGNORECASE):
                found_certs.append(kw)

        # Also capture bulleted lines from certification section
        if cert_section:
            for line in cert_section.split("\n"):
                line = line.strip(" •*-")
                if len(line) > 5 and line not in found_certs:
                    found_certs.append(line)

        return list(dict.fromkeys(found_certs))[:5]

    # -------------------------------------------------------------------------
    # 6. Manual Entry Features (Skills & Interests)
    # -------------------------------------------------------------------------
    def add_manual_skills(self, manual_skills: List[str]) -> List[str]:
        """
        Allows manual entry of skills, standardizes them, and merges them into profile.
        """
        cleaned = clean_and_standardize_skills(manual_skills)
        for s in cleaned:
            if s.lower() not in [existing.lower() for existing in self.skills]:
                self.skills.append(s)
        return self.skills

    def add_manual_interests(self, manual_interests: List[str]) -> List[str]:
        """
        Allows manual entry of interests or career preferences with proper acronym preservation.
        """
        for item in manual_interests:
            clean_item = item.strip()
            lookup = clean_item.lower()
            if lookup in CANONICAL_SKILLS:
                standardized = CANONICAL_SKILLS[lookup]
            elif lookup in SKILL_ALIASES:
                standardized = SKILL_ALIASES[lookup]
            else:
                words = clean_item.split()
                standardized_words = []
                for w in words:
                    if w.upper() in {"AI", "ML", "NLP", "DL", "CV", "UI", "UX", "API", "REST", "CI/CD", "AWS", "GCP", "SQL", "IOT"}:
                        standardized_words.append(w.upper())
                    else:
                        standardized_words.append(w.capitalize())
                standardized = " ".join(standardized_words)

            if standardized and standardized.lower() not in [i.lower() for i in self.interests]:
                self.interests.append(standardized)
        return self.interests

    # -------------------------------------------------------------------------
    # Helper: Section Extractor
    # -------------------------------------------------------------------------
    def _get_section_text(self, section_names: List[str]) -> str:
        """
        Extracts the chunk of text corresponding to specific section titles.
        """
        pattern = r"(?i)(?:^|\n)\s*(?:[#\-*]*\s*)?(" + "|".join(re.escape(s) for s in section_names) + r")\s*[:\n]"
        matches = list(re.finditer(pattern, self.raw_text))
        if not matches:
            return ""

        first_match = matches[0]
        start_pos = first_match.end()

        # Find next section start
        next_section_pattern = r"(?i)\n\s*(?:[#\-*]*\s*)?(?:education|skills|experience|projects|certifications|interests|publications|achievements|contact)\s*[:\n]"
        next_match = re.search(next_section_pattern, self.raw_text[start_pos:])

        if next_match:
            end_pos = start_pos + next_match.start()
            return self.raw_text[start_pos:end_pos].strip()

        return self.raw_text[start_pos:].strip()

    # -------------------------------------------------------------------------
    # Output Formatters
    # -------------------------------------------------------------------------
    def get_summary(self) -> Dict[str, Any]:
        """
        Returns exact requested output schema:
        {
            "education": "B.Tech CSE",
            "skills": [
                "Python",
                "SQL",
                "Pandas",
                "Machine Learning"
            ],
            "experience": 1,
            "projects": 2
        }
        """
        return {
            "education": self.education,
            "skills": self.skills,
            "experience": self.experience_years,
            "projects": self.projects_count
        }

    def get_detailed_profile(self) -> Dict[str, Any]:
        """
        Provides rich structured profile for downstream team members.
        """
        return {
            "education": self.education,
            "skills": self.skills,
            "experience_years": self.experience_years,
            "projects_count": self.projects_count,
            "projects_details": self.projects_details,
            "certifications": self.certifications,
            "interests": self.interests
        }

    def to_dataframe(self) -> Any:
        """
        Exports the profile summary into a Pandas DataFrame for downstream analytics.
        """
        if not HAS_PANDAS:
            raise ImportError(
                "Pandas is not installed. Run 'pip install pandas' to use to_dataframe()."
            )
        summary = self.get_summary()
        return pd.DataFrame([{
            "education": summary["education"],
            "skills_count": len(summary["skills"]),
            "skills": ", ".join(summary["skills"]),
            "experience": summary["experience"],
            "projects": summary["projects"]
        }])
