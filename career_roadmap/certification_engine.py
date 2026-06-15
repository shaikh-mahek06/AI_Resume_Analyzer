CERTIFICATIONS_BY_ROLE = {
    "ai engineer": [
        {
            "provider": "DeepLearning.AI",
            "course_name": "Generative AI for Everyone",
            "free_or_paid": "Free audit / Paid certificate",
            "link": "https://www.coursera.org/learn/generative-ai-for-everyone",
        },
        {
            "provider": "AWS",
            "course_name": "AWS Certified AI Practitioner",
            "free_or_paid": "Paid",
            "link": "https://aws.amazon.com/certification/certified-ai-practitioner/",
        },
        {
            "provider": "Microsoft",
            "course_name": "Azure AI Engineer Associate",
            "free_or_paid": "Paid",
            "link": "https://learn.microsoft.com/en-us/credentials/certifications/azure-ai-engineer/",
        },
    ],
    "data scientist": [
        {
            "provider": "IBM",
            "course_name": "IBM Data Science Professional Certificate",
            "free_or_paid": "Free audit / Paid certificate",
            "link": "https://www.coursera.org/professional-certificates/ibm-data-science",
        },
        {
            "provider": "Google",
            "course_name": "Google Advanced Data Analytics Certificate",
            "free_or_paid": "Paid",
            "link": "https://www.coursera.org/professional-certificates/google-advanced-data-analytics",
        },
        {
            "provider": "DeepLearning.AI",
            "course_name": "Machine Learning Specialization",
            "free_or_paid": "Free audit / Paid certificate",
            "link": "https://www.coursera.org/specializations/machine-learning-introduction",
        },
    ],
    "ml engineer": [
        {
            "provider": "Google",
            "course_name": "Professional Machine Learning Engineer",
            "free_or_paid": "Paid",
            "link": "https://cloud.google.com/learn/certification/machine-learning-engineer",
        },
        {
            "provider": "AWS",
            "course_name": "AWS Certified Machine Learning - Specialty",
            "free_or_paid": "Paid",
            "link": "https://aws.amazon.com/certification/certified-machine-learning-specialty/",
        },
        {
            "provider": "DeepLearning.AI",
            "course_name": "Machine Learning Engineering for Production",
            "free_or_paid": "Free audit / Paid certificate",
            "link": "https://www.coursera.org/specializations/machine-learning-engineering-for-production-mlops",
        },
    ],
    "data analyst": [
        {
            "provider": "Google",
            "course_name": "Google Data Analytics Certificate",
            "free_or_paid": "Paid",
            "link": "https://www.coursera.org/professional-certificates/google-data-analytics",
        },
        {
            "provider": "IBM",
            "course_name": "IBM Data Analyst Professional Certificate",
            "free_or_paid": "Free audit / Paid certificate",
            "link": "https://www.coursera.org/professional-certificates/ibm-data-analyst",
        },
        {
            "provider": "Microsoft",
            "course_name": "Power BI Data Analyst Associate",
            "free_or_paid": "Paid",
            "link": "https://learn.microsoft.com/en-us/credentials/certifications/power-bi-data-analyst-associate/",
        },
    ],
    "backend developer": [
        {
            "provider": "AWS",
            "course_name": "AWS Certified Developer - Associate",
            "free_or_paid": "Paid",
            "link": "https://aws.amazon.com/certification/certified-developer-associate/",
        },
        {
            "provider": "Microsoft",
            "course_name": "Azure Developer Associate",
            "free_or_paid": "Paid",
            "link": "https://learn.microsoft.com/en-us/credentials/certifications/azure-developer/",
        },
        {
            "provider": "IBM",
            "course_name": "Back-End Development Professional Certificate",
            "free_or_paid": "Free audit / Paid certificate",
            "link": "https://www.coursera.org/professional-certificates/ibm-backend-development",
        },
    ],
}


def recommend_certifications(target_role):
    role = target_role.strip().lower() if isinstance(target_role, str) else ""
    return CERTIFICATIONS_BY_ROLE.get(role, [])
