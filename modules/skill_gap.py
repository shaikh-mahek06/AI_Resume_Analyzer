from typing import Dict, List


SKILL_EXPLANATIONS = {
    "airflow": "Learn Airflow for workflow orchestration and data pipeline scheduling.",
    "aws": "Learn AWS for cloud-based data and machine learning deployments.",
    "azure": "Learn Azure for cloud services, analytics workflows, and enterprise deployments.",
    "docker": "Learn Docker for packaging applications and creating consistent deployment environments.",
    "excel": "Learn Excel for data analysis, reporting, and business decision support.",
    "gcp": "Learn GCP for scalable data platforms and machine learning services.",
    "hadoop": "Learn Hadoop for big data processing.",
    "mysql": "Learn MySQL for database management.",
    "postgresql": "Learn PostgreSQL for relational database design and querying.",
    "power bi": "Learn Power BI for interactive dashboards and business reporting.",
    "python": "Learn Python for data analysis, automation, and machine learning development.",
    "pytorch": "Learn PyTorch for building and training deep learning models.",
    "spark": "Learn Spark for distributed computing.",
    "sql": "Learn SQL for querying, managing, and analyzing structured data.",
    "tableau": "Learn Tableau for data visualization and dashboard creation.",
    "tensorflow": "Learn TensorFlow for building production-ready machine learning models.",
}

ADVANCED_SKILL_SUGGESTIONS = [
    {
        "label": "AWS",
        "aliases": {"aws"},
        "recommendation": "Consider learning AWS to improve your profile.",
    },
    {
        "label": "System Design",
        "aliases": {"system design"},
        "recommendation": "Add system design or cloud skills to strengthen your resume.",
    },
    {
        "label": "Cloud Architecture",
        "aliases": {"aws", "azure", "gcp", "cloud architecture"},
        "recommendation": "Build stronger cloud architecture skills to improve your fit for broader roles.",
    },
]

LEARNING_PATH_STAGES = ("Beginner", "Intermediate", "Advanced")
SKILL_LEVELS = {
    "sql": "Beginner",
    "excel": "Beginner",
    "mysql": "Beginner",
    "postgresql": "Beginner",
    "power bi": "Beginner",
    "tableau": "Beginner",
    "python": "Intermediate",
    "ml": "Intermediate",
    "tensorflow": "Intermediate",
    "pytorch": "Intermediate",
    "docker": "Intermediate",
    "airflow": "Intermediate",
    "spark": "Advanced",
    "aws": "Advanced",
    "azure": "Advanced",
    "gcp": "Advanced",
    "hadoop": "Advanced",
    "system design": "Advanced",
    "cloud architecture": "Advanced",
}
DEFAULT_LEARNING_PATH = {
    "Beginner": ["SQL", "Excel"],
    "Intermediate": ["Python", "ML"],
    "Advanced": ["Spark", "Cloud"],
}


def _format_skill_name(skill: str) -> str:
    """
    Format skill names for readable suggestions.
    """
    upper_map = {
        "aws": "AWS",
        "css": "CSS",
        "gcp": "GCP",
        "html": "HTML",
        "ml": "ML",
        "nlp": "NLP",
        "power bi": "Power BI",
        "sql": "SQL",
    }
    skill_key = skill.strip().lower()
    if skill_key in upper_map:
        return upper_map[skill_key]
    return " ".join(word.capitalize() for word in skill_key.split())


def _build_recommendation(skill: str) -> str:
    """
    Build a meaningful learning suggestion for a missing skill.
    """
    skill_key = skill.strip().lower()
    if skill_key in SKILL_EXPLANATIONS:
        return SKILL_EXPLANATIONS[skill_key]

    formatted_skill = _format_skill_name(skill)
    return f"Learn {formatted_skill} to strengthen your profile for this role."


def _build_learning_path(skills: List[str]) -> Dict[str, List[str]]:
    """
    Organize skills into a simple staged roadmap.
    """
    learning_path = {stage: [] for stage in LEARNING_PATH_STAGES}

    for skill in skills:
        skill_key = skill.strip().lower()
        if not skill_key:
            continue

        stage = SKILL_LEVELS.get(skill_key, "Intermediate")
        formatted_skill = _format_skill_name(skill)
        if formatted_skill not in learning_path[stage]:
            learning_path[stage].append(formatted_skill)

    if not any(learning_path.values()):
        return DEFAULT_LEARNING_PATH

    for stage in LEARNING_PATH_STAGES:
        if not learning_path[stage]:
            learning_path[stage] = DEFAULT_LEARNING_PATH[stage]

    return learning_path


def get_advanced_skill_suggestions(resume_skills: List[str], limit: int = 2) -> Dict[str, List[str]]:
    """
    Suggest a small set of advanced skills when there are no direct skill gaps.
    """
    resume_set = {skill.strip().lower() for skill in resume_skills if skill and skill.strip()}
    suggested_skills: List[str] = []
    recommendations: List[str] = []

    for suggestion in ADVANCED_SKILL_SUGGESTIONS:
        if resume_set.intersection(suggestion["aliases"]):
            continue

        suggested_skills.append(suggestion["label"])
        recommendations.append(suggestion["recommendation"])

        if len(suggested_skills) >= limit:
            break

    if suggested_skills:
        return {
            "skills": suggested_skills,
            "recommendations": recommendations,
        }

    fallback = ADVANCED_SKILL_SUGGESTIONS[:limit]
    return {
        "skills": [item["label"] for item in fallback],
        "recommendations": [item["recommendation"] for item in fallback],
    }


def analyze_skill_gap(resume_skills: List[str], job_skills: List[str]) -> Dict[str, object]:
    """
    Compare resume skills with job skills.
    Returns matched skills, missing skills, simple recommendations, and a learning roadmap.
    """
    resume_set = {skill.strip().lower() for skill in resume_skills if skill and skill.strip()}
    job_clean = [skill.strip() for skill in job_skills if skill and skill.strip()]

    matched_skills: List[str] = []
    missing_skills: List[str] = []
    recommendations: List[str] = []
    suggested_skills: List[str] = []

    seen_matched = set()
    seen_missing = set()

    for job_skill in job_clean:
        job_key = job_skill.lower()
        if job_key in resume_set:
            if job_key not in seen_matched:
                matched_skills.append(job_skill)
                seen_matched.add(job_key)
        else:
            if job_key not in seen_missing:
                missing_skills.append(job_skill)
                recommendations.append(_build_recommendation(job_skill))
                seen_missing.add(job_key)

    if not missing_skills:
        advanced_suggestions = get_advanced_skill_suggestions(resume_skills)
        suggested_skills = advanced_suggestions["skills"]
        recommendations.extend(advanced_suggestions["recommendations"])

    roadmap_source = missing_skills or suggested_skills

    return {
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "suggested_skills": suggested_skills,
        "recommendations": recommendations,
        "learning_path": _build_learning_path(roadmap_source),
    }
