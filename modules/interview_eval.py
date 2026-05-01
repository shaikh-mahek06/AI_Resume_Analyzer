import re
from typing import Dict

from utils.llm_client import LLMClient


INTERVIEW_EVALUATION_PROMPT = """
Evaluate the interview answer.

Requirements:
- Score the answer out of 10.
- Identify strengths in the answer.
- Suggest improvements.
- Keep response short and structured.

Output format:
Score: X/10
Strengths: <short strengths>
Improvement: <short improvement suggestion>
""".strip()


def _build_evaluation_prompt(question: str, answer: str) -> str:
    """
    Build the prompt used for interview answer evaluation.
    """
    return (
        f"{INTERVIEW_EVALUATION_PROMPT}\n\n"
        f"Question: {question.strip()}\n"
        f"Answer: {answer.strip()}"
    )


def _parse_evaluation(response_text: str) -> Dict[str, str | int]:
    """
    Parse Gemini output into score and feedback fields.
    """
    score_match = re.search(r"score\s*:\s*(\d+)\s*/\s*10", response_text, flags=re.IGNORECASE)
    strengths_match = re.search(r"strengths\s*:\s*(.+)", response_text, flags=re.IGNORECASE)
    improvement_match = re.search(r"improvement\s*:\s*(.+)", response_text, flags=re.IGNORECASE)

    if not score_match:
        raise ValueError("Gemini did not return a valid answer score.")

    score = max(0, min(10, int(score_match.group(1))))
    feedback = strengths_match.group(1).strip() if strengths_match else "No strengths identified."
    improvement = improvement_match.group(1).strip() if improvement_match else "No improvement suggestion provided."

    return {
        "score": score,
        "feedback": feedback,
        "improvement": improvement,
    }


def evaluate_interview_answer(
    question: str,
    answer: str,
    llm_client: LLMClient | None = None,
) -> Dict[str, str | int]:
    """
    Evaluate an interview answer using the Gemini API.
    """
    cleaned_question = question.strip()
    cleaned_answer = answer.strip()

    if not cleaned_question:
        raise ValueError("Question cannot be empty.")
    if not cleaned_answer:
        raise ValueError("Answer cannot be empty.")

    client = llm_client or LLMClient()
    prompt = _build_evaluation_prompt(cleaned_question, cleaned_answer)

    try:
        response_text = client.generate_text(prompt).strip()
    except ValueError:
        raise
    except Exception as error:
        raise RuntimeError(
            "Gemini API request failed while evaluating the interview answer."
        ) from error

    if not response_text:
        raise ValueError("Gemini returned an empty interview evaluation response.")

    return _parse_evaluation(response_text)
