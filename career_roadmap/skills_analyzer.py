import re


def normalize_skill(skill):
    return re.sub(r"\s+", " ", skill.strip().lower())


def extract_skills(resume_text, skill_keywords):
    if not resume_text or not skill_keywords:
        return []

    text = resume_text.lower()
    found_skills = set()

    for skill in skill_keywords:
        normalized = normalize_skill(skill)
        pattern = r"(?<!\w)" + re.escape(normalized) + r"(?!\w)"
        if re.search(pattern, text):
            found_skills.add(normalized)

    return sorted(found_skills)


def analyze_skill_gap(resume_text, target_role_skills):
    target_skills = sorted({normalize_skill(skill) for skill in target_role_skills if skill})
    matching_skills = extract_skills(resume_text, target_skills)
    missing_skills = sorted(set(target_skills) - set(matching_skills))

    match_percentage = 0
    if target_skills:
        match_percentage = round((len(matching_skills) / len(target_skills)) * 100, 2)

    return {
        "matching_skills": matching_skills,
        "missing_skills": missing_skills,
        "match_percentage": match_percentage,
    }
