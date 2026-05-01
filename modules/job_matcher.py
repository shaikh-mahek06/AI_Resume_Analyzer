import csv
from pathlib import Path
from typing import Dict, List


MAX_JOB_MATCH_SCORE = 90


def _build_match_explanation(matched_skills: List[str], total_job_skills: int) -> str:
    """
    Build a short explanation for the job match score.
    """
    return f"Your resume matches {len(matched_skills)} out of {total_job_skills} required skills."


def load_jobs_from_csv(csv_path: str) -> List[Dict[str, object]]:
    """
    Load jobs from CSV file.
    Expected columns: role, skills
    """
    jobs: List[Dict[str, object]] = []
    path = Path(csv_path)

    if not path.exists():
        return jobs

    with path.open("r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)
        for row in reader:
            role = (row.get("role") or "").strip()
            skills_text = row.get("skills") or ""
            skills = [skill.strip().lower() for skill in skills_text.split(",") if skill.strip()]

            if role and skills:
                jobs.append({"role": role, "skills": skills})

    return jobs


def get_top_job_matches(user_skills: List[str], jobs_csv_path: str, top_n: int = 3) -> List[Dict[str, object]]:
    """
    Return top matching jobs with match score.

    Match score formula:
    matched_job_skills / total_job_skills * 100,
    capped at a realistic maximum score.
    """
    user_skill_set = {skill.strip().lower() for skill in user_skills if skill and skill.strip()}
    jobs = load_jobs_from_csv(jobs_csv_path)
    results: List[Dict[str, object]] = []

    for job in jobs:
        job_skills = job["skills"]
        matched = [skill for skill in job_skills if skill in user_skill_set]
        raw_score = int((len(matched) / len(job_skills)) * 100) if job_skills else 0
        score = min(raw_score, MAX_JOB_MATCH_SCORE)

        results.append(
            {
                "role": job["role"],
                "score": score,
                "explanation": _build_match_explanation(matched, len(job_skills)),
                "matched_skills": matched,
            }
        )

    results.sort(key=lambda item: item["score"], reverse=True)
    return results[:top_n]
