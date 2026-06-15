def _clean_skills(skills):
    return sorted({skill.strip().lower() for skill in skills if isinstance(skill, str) and skill.strip()})


def _build_stage(skills, focus, action):
    return [
        {
            "skill": skill,
            "focus": focus,
            "action": action.format(skill=skill),
        }
        for skill in skills
    ]


def _build_monthly_timeline(skills):
    if not skills:
        return []

    return [
        {
            "month": index + 1,
            "focus_skill": skill,
            "goal": f"Learn, practice, and build a small project using {skill}.",
        }
        for index, skill in enumerate(skills)
    ]


def generate_roadmap(missing_skills, target_role):
    skills = _clean_skills(missing_skills)
    role = target_role.strip() if isinstance(target_role, str) and target_role.strip() else "Target Role"

    return {
        "target_role": role,
        "missing_skills": skills,
        "roadmap": {
            "beginner": _build_stage(
                skills,
                "fundamentals",
                "Understand core concepts and basic syntax for {skill}.",
            ),
            "intermediate": _build_stage(
                skills,
                "applied practice",
                "Solve practical problems and integrate {skill} into projects.",
            ),
            "advanced": _build_stage(
                skills,
                "production readiness",
                "Build, optimize, and document production-ready work with {skill}.",
            ),
        },
        "monthly_timeline": _build_monthly_timeline(skills),
    }
