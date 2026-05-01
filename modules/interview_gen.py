import re
import ast
from typing import List

from utils.llm_client import LLMClient


INTERVIEW_QUESTION_PROMPT = """
Generate exactly 10 technical interview questions for a {role}.
The questions must:
- Be strictly technical
- Be relevant to real job scenarios
- Cover tools, concepts, and problem-solving
- Avoid behavioral or generic questions
Return ONLY a Python list of 10 questions.
""".strip()


def _build_interview_prompt(job_role: str, user_skills: List[str]) -> str:
    """
    Build the prompt used for interview question generation.
    """
    cleaned_role = job_role.strip()

    prompt_template = INTERVIEW_QUESTION_PROMPT.replace("{role}", cleaned_role)
    
    return prompt_template


def _parse_questions(response_text: str) -> List[str]:
    """
    Parse LLM output into a clean list of technical questions.
    Handles multiple formats: Python list, numbered list, bullet points.
    """
    questions = []
    text = response_text.strip()
    
    # Method 1: Try to parse as Python list
    try:
        # Handle markdown code blocks
        text = re.sub(r'^```python\s*', '', text)
        text = re.sub(r'^```\s*', '', text)
        text = re.sub(r'```$', '', text)
        
        # Try ast.literal_eval for safe parsing
        parsed = ast.literal_eval(text)
        if isinstance(parsed, list):
            questions = [str(q).strip() for q in parsed if q]
    except (ValueError, SyntaxError):
        pass
    
    # Method 2: Parse line by line if list parsing failed
    if not questions:
        for line in text.splitlines():
            cleaned_line = line.strip()
            if not cleaned_line:
                continue

            # Remove bullet points, numbering, quotes
            cleaned_line = re.sub(r"^[-*•]\s*", "", cleaned_line)
            cleaned_line = re.sub(r"^\d+[).\s-]*", "", cleaned_line)
            cleaned_line = cleaned_line.strip().strip('"').strip("'")

            if not cleaned_line:
                continue

            # Skip any section headers or non-question lines
            if cleaned_line.lower() in ["technical questions", "behavioral questions", "role-specific questions", "questions:"]:
                continue

            if cleaned_line not in questions:
                questions.append(cleaned_line)
    
    return questions


def _normalize_to_10(questions: List[str]) -> List[str]:
    """
    Normalize the questions list to exactly 10 items.
    Never raises error - pads with defaults or truncates as needed.
    """
    cleaned = [q.strip() for q in questions if q and isinstance(q, str) and q.strip()]
    
    # Default questions if none generated
    default_questions = [
        "Explain the difference between supervised and unsupervised learning.",
        "What is overfitting and how can you prevent it?",
        "Describe the bias-variance tradeoff.",
        "What are the key differences between SQL and NoSQL databases?",
        "Explain the concept of RESTful APIs.",
        "What is the purpose of version control systems?",
        "Describe the machine learning pipeline steps.",
        "What is data normalization and why is it important?",
        "Explain the difference between classification and regression.",
        "What are the best practices for data preprocessing?"
    ]
    
    if not cleaned:
        return default_questions
    
    # Pad with default questions if less than 10
    while len(cleaned) < 10:
        idx = len(cleaned) % len(default_questions)
        cleaned.append(default_questions[idx])
    
    # Truncate to exactly 10
    return cleaned[:10]


def generate_interview_questions(
    job_role: str,
    user_skills: List[str],
    llm_client: LLMClient | None = None,
) -> List[str]:
    """
    Generate exactly 10 technical interview questions using the LLM API.
    Never raises error for count mismatch - normalizes to 10 questions.
    """
    cleaned_role = job_role.strip()
    if not cleaned_role:
        cleaned_role = "General Technical Role"

    client = llm_client or LLMClient()
    prompt = _build_interview_prompt(cleaned_role, user_skills)

    try:
        response_text = client.generate_text(prompt).strip()
    except Exception:
        # Return defaults on any LLM error
        return _normalize_to_10([])

    if not response_text:
        return _normalize_to_10([])

    questions = _parse_questions(response_text)
    
    # Normalize to exactly 10 - never raises error
    return _normalize_to_10(questions)