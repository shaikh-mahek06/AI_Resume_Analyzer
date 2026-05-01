import re
from typing import Dict

from utils.llm_client import LLMClient


ANSWER_EVALUATION_PROMPT = """
Evaluate the interview answer.

Focus on:
- clarity
- technical correctness
- communication

Keep the response short and structured.

Output format:
Score: X/10
Feedback: <short feedback>
""".strip()


def _build_evaluation_prompt(question: str, user_answer: str) -> str:
    """
    Build the prompt used for answer evaluation.
    """
    return (
        f"{ANSWER_EVALUATION_PROMPT}\n\n"
        f"Question: {question.strip()}\n"
        f"Answer: {user_answer.strip()}"
    )


def _parse_evaluation(response_text: str) -> Dict[str, int | str]:
    """
    Parse Gemini output into score and feedback.
    """
    score_match = re.search(r"score\s*:\s*(\d+)\s*/\s*10", response_text, flags=re.IGNORECASE)
    feedback_match = re.search(r"feedback\s*:\s*(.+)", response_text, flags=re.IGNORECASE)

    if not score_match:
        raise ValueError("Gemini did not return a valid score.")

    score = max(0, min(10, int(score_match.group(1))))
    feedback = feedback_match.group(1).strip() if feedback_match else "No feedback provided."

    return {
        "score": score,
        "feedback": feedback,
    }


def evaluate_answer(
    question: str,
    user_answer: str,
    llm_client: LLMClient | None = None,
) -> Dict[str, int | str]:
    """
    Evaluate an interview answer using the Gemini API.
    """
    cleaned_question = question.strip()
    cleaned_answer = user_answer.strip()

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
            "Gemini API request failed while evaluating the answer."
        ) from error

    if not response_text:
        raise ValueError("Gemini returned an empty evaluation response.")

    return _parse_evaluation(response_text)
