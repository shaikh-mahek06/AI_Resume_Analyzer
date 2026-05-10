import re
import ast
from typing import List

from utils.llm_client import LLMClient


INTERVIEW_QUESTION_PROMPT = """
Generate exactly 8 interview questions for a {role} position.
The questions must include a mix of:
- Technical questions (related to tools, concepts, problem-solving)
- Behavioral questions (past experiences, teamwork, challenges)
- Situational questions (hypothetical scenarios, decision-making)

Return ONLY a Python list of exactly 8 questions.
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


def _normalize_to_8(questions: List[str]) -> List[str]:
    """
    Normalize the questions list to exactly 8 items.
    Never raises error - pads with defaults or truncates as needed.
    """
    cleaned = [q.strip() for q in questions if q and isinstance(q, str) and q.strip()]
    
    # Default questions if none generated
    default_questions = [
        "Explain the difference between supervised and unsupervised learning.",
        "Describe a challenging project you worked on and how you overcame obstacles.",
        "How would you handle a situation where a project deadline is approaching and you're behind schedule?",
        "What is overfitting and how can you prevent it?",
        "Tell me about a time when you had to learn a new technology quickly.",
        "How would you approach debugging a complex issue in production?",
        "Describe the bias-variance tradeoff.",
        "Give an example of how you've collaborated with a team to solve a problem."
    ]
    
    if not cleaned:
        return default_questions
    
    # Pad with default questions if less than 8
    while len(cleaned) < 8:
        idx = len(cleaned) % len(default_questions)
        cleaned.append(default_questions[idx])
    
    # Truncate to exactly 8
    return cleaned[:8]


def generate_interview_questions(
    job_role: str,
    user_skills: List[str],
    llm_client: LLMClient | None = None,
) -> List[str]:
    """
    Generate exactly 8 interview questions using the LLM API.
    Never raises error for count mismatch - normalizes to 8 questions.
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
        return _normalize_to_8([])

    if not response_text:
        return _normalize_to_8([])

    questions = _parse_questions(response_text)
    
    # Normalize to exactly 8 - never raises error
    return _normalize_to_8(questions)