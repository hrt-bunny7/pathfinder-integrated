"""
Skill Dictionary & Standardization Module for Person 1 (Resume & Profile Analysis)
Provides canonical skill sets, synonym/alias mapping, and normalization logic.
"""

import re
from typing import Dict, List, Set

# Canonical Skill Database mapped to category
CANONICAL_SKILLS: Dict[str, str] = {
    # Programming Languages
    "python": "Python",
    "c": "C",
    "c++": "C++",
    "cpp": "C++",
    "c#": "C#",
    "csharp": "C#",
    "java": "Java",
    "javascript": "JavaScript",
    "typescript": "TypeScript",
    "go": "Go",
    "golang": "Go",
    "rust": "Rust",
    "ruby": "Ruby",
    "php": "PHP",
    "swift": "Swift",
    "kotlin": "Kotlin",
    "r": "R",
    "matlab": "MATLAB",
    "scala": "Scala",
    "sql": "SQL",
    "html": "HTML",
    "html5": "HTML",
    "css": "CSS",
    "css3": "CSS",
    "bash": "Bash",
    "shell": "Shell",

    # Data Science & Machine Learning
    "machine learning": "Machine Learning",
    "ml": "Machine Learning",
    "deep learning": "Deep Learning",
    "dl": "Deep Learning",
    "natural language processing": "Natural Language Processing",
    "nlp": "Natural Language Processing",
    "computer vision": "Computer Vision",
    "cv": "Computer Vision",
    "generative ai": "Generative AI",
    "genai": "Generative AI",
    "pandas": "Pandas",
    "numpy": "NumPy",
    "scipy": "SciPy",
    "scikit-learn": "Scikit-Learn",
    "scikit learn": "Scikit-Learn",
    "sklearn": "Scikit-Learn",
    "tensorflow": "TensorFlow",
    "tf": "TensorFlow",
    "pytorch": "PyTorch",
    "keras": "Keras",
    "opencv": "OpenCV",
    "spacy": "spaCy",
    "nltk": "NLTK",
    "matplotlib": "Matplotlib",
    "seaborn": "Seaborn",
    "data analysis": "Data Analysis",
    "data science": "Data Science",
    "data visualization": "Data Visualization",
    "tableau": "Tableau",
    "power bi": "Power BI",
    "powerbi": "Power BI",
    "hadoop": "Hadoop",
    "spark": "Apache Spark",
    "apache spark": "Apache Spark",
    "bigquery": "BigQuery",

    # Web & Frameworks
    "react": "React",
    "reactjs": "React",
    "react.js": "React",
    "angular": "Angular",
    "angularjs": "Angular",
    "vue": "Vue.js",
    "vuejs": "Vue.js",
    "vue.js": "Vue.js",
    "node": "Node.js",
    "nodejs": "Node.js",
    "node.js": "Node.js",
    "express": "Express.js",
    "expressjs": "Express.js",
    "nextjs": "Next.js",
    "next.js": "Next.js",
    "django": "Django",
    "flask": "Flask",
    "fastapi": "FastAPI",
    "spring": "Spring",
    "spring boot": "Spring Boot",
    "springboot": "Spring Boot",
    "asp.net": "ASP.NET",
    ".net": ".NET",
    "bootstrap": "Bootstrap",
    "tailwind": "Tailwind CSS",
    "tailwind css": "Tailwind CSS",

    # Databases
    "mysql": "MySQL",
    "postgresql": "PostgreSQL",
    "postgres": "PostgreSQL",
    "sqlite": "SQLite",
    "mongodb": "MongoDB",
    "mongo": "MongoDB",
    "redis": "Redis",
    "cassandra": "Cassandra",
    "oracle": "Oracle DB",
    "firebase": "Firebase",
    "dynamodb": "DynamoDB",

    # Cloud & DevOps
    "aws": "AWS",
    "amazon web services": "AWS",
    "azure": "Azure",
    "microsoft azure": "Azure",
    "gcp": "Google Cloud",
    "google cloud": "Google Cloud",
    "google cloud platform": "Google Cloud",
    "docker": "Docker",
    "kubernetes": "Kubernetes",
    "k8s": "Kubernetes",
    "git": "Git",
    "github": "GitHub",
    "gitlab": "GitLab",
    "ci/cd": "CI/CD",
    "jenkins": "Jenkins",
    "linux": "Linux",
    "terraform": "Terraform",

    # Core Computer Science
    "data structures": "Data Structures",
    "algorithms": "Algorithms",
    "data structures and algorithms": "Data Structures & Algorithms",
    "dsa": "Data Structures & Algorithms",
    "object-oriented programming": "Object-Oriented Programming",
    "oop": "Object-Oriented Programming",
    "oops": "Object-Oriented Programming",
    "operating systems": "Operating Systems",
    "os": "Operating Systems",
    "computer networks": "Computer Networks",
    "cn": "Computer Networks",
    "database management systems": "DBMS",
    "dbms": "DBMS",
    "rest api": "REST APIs",
    "restful api": "REST APIs",
    "graphql": "GraphQL"
}

# Aliases and acronym lookup
SKILL_ALIASES: Dict[str, str] = {
    "py": "Python",
    "js": "JavaScript",
    "ts": "TypeScript",
    "ml": "Machine Learning",
    "dl": "Deep Learning",
    "nlp": "Natural Language Processing",
    "cv": "Computer Vision",
    "tf": "TensorFlow",
    "sklearn": "Scikit-Learn",
    "k8s": "Kubernetes",
    "postgres": "PostgreSQL",
    "mongo": "MongoDB",
    "reactjs": "React",
    "nodejs": "Node.js",
    "vuejs": "Vue.js",
    "gcp": "Google Cloud",
    "dsa": "Data Structures & Algorithms",
    "oops": "Object-Oriented Programming",
    "oop": "Object-Oriented Programming",
    "dbms": "DBMS",
}


def clean_skill_string(text: str) -> str:
    """Cleans punctuation, whitespace, and lowercases text for matching."""
    if not text:
        return ""
    text = text.strip()
    # Normalize multiple whitespace
    text = re.sub(r"\s+", " ", text)
    return text


def standardize_skill_name(raw_skill: str) -> str:
    """
    Standardize a single skill name into its canonical format.
    E.g.: 'pandas ' -> 'Pandas', 'py' -> 'Python', 'machine learning' -> 'Machine Learning'
    """
    clean_raw = clean_skill_string(raw_skill)
    lookup_key = clean_raw.lower()

    # 1. Direct alias check
    if lookup_key in SKILL_ALIASES:
        return SKILL_ALIASES[lookup_key]

    # 2. Canonical skills check
    if lookup_key in CANONICAL_SKILLS:
        return CANONICAL_SKILLS[lookup_key]

    # 3. Handle acronyms like AWS, SQL, HTML, CSS, PHP, API
    if lookup_key in {"aws", "sql", "html", "css", "php", "api", "rest", "dsa", "dbms", "os", "cn", "r"}:
        return clean_raw.upper()

    # 4. Fallback: Title case if words are alphabetical
    return clean_raw.title()


def clean_and_standardize_skills(skills: List[str]) -> List[str]:
    """
    Standardizes a list of skills, removes duplicates while preserving original order.
    """
    standardized_list: List[str] = []
    seen: Set[str] = set()

    for skill in skills:
        if not skill:
            continue
        cleaned = standardize_skill_name(skill)
        lowered = cleaned.lower()
        if lowered and lowered not in seen:
            seen.add(lowered)
            standardized_list.append(cleaned)

    return standardized_list
