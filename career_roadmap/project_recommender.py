ROLE_PROJECTS = {
    "ai engineer": [
        "AI Chatbot with RAG",
        "Resume Intelligence Assistant",
        "Document QA System",
    ],
    "data scientist": [
        "Customer Churn Prediction",
        "Sales Forecasting Dashboard",
        "Recommendation System",
    ],
    "ml engineer": [
        "Model Serving API",
        "ML Pipeline with Monitoring",
        "Feature Store Prototype",
    ],
    "data analyst": [
        "Business KPI Dashboard",
        "SQL Sales Analysis",
        "Marketing Funnel Report",
    ],
    "backend developer": [
        "REST API Service",
        "Authentication System",
        "Task Queue Backend",
    ],
}


def _clean_items(items):
    return [item.strip().lower() for item in items if isinstance(item, str) and item.strip()]


def _project_description(title, role, skills):
    skill_text = ", ".join(skills[:3]) if skills else "core role skills"
    return f"Build a {title.lower()} for a {role} role using {skill_text}."


def recommend_projects(target_role, missing_skills):
    role = target_role.strip() if isinstance(target_role, str) and target_role.strip() else "Target Role"
    role_key = role.lower()
    skills = _clean_items(missing_skills)
    titles = ROLE_PROJECTS.get(role_key, ["Portfolio Project", "Capstone Project", "Production Demo"])
    difficulties = ["Beginner", "Intermediate", "Advanced"]

    return [
        {
            "title": title,
            "difficulty": difficulties[index],
            "tech_stack": skills[:4] or ["python", "sql"],
            "short_description": _project_description(title, role, skills),
        }
        for index, title in enumerate(titles[:3])
    ]
