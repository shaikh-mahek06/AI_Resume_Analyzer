from typing import Dict, List

from utils.skill_extractor import extract_skills


MIN_REQUIRED_SKILLS = 5
MAX_ATS_SCORE = 90
LOW_SKILL_COUNT_PENALTY = 5


def calculate_ats_score(resume_text: str, job_description: str) -> Dict[str, object]:
    """
    Compare resume skills against job description skills.
    Returns ATS score, matched skills, and missing skills.
    """
    jd_skills = extract_skills(job_description)
    resume_skills = set(extract_skills(resume_text))

    if not jd_skills:
        return {
            "score": 0,
            "matched_skills": [],
            "missing_skills": [],
        }

    matched_skills = [skill for skill in jd_skills if skill in resume_skills]
    missing_skills = [skill for skill in jd_skills if skill not in resume_skills]

    total_job_skills = len(jd_skills)
    score = int((len(matched_skills) / total_job_skills) * 100)

    if len(matched_skills) == total_job_skills:
        score = min(score, MAX_ATS_SCORE)

    if total_job_skills < MIN_REQUIRED_SKILLS:
        score = max(0, score - LOW_SKILL_COUNT_PENALTY)

    return {
        "score": score,
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
    }
