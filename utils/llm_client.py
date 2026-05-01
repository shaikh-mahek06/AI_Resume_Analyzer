import os
from pathlib import Path

from dotenv import load_dotenv
import google.generativeai as genai


DEFAULT_GEMINI_MODEL = "gemini-1.5-flash"
ENV_PATH = Path(__file__).resolve().parents[1] / ".env"


load_dotenv(dotenv_path=ENV_PATH)


class LLMClient:
    """
    Small wrapper around the Gemini API.
    """

    def __init__(self, api_key: str | None = None, model: str | None = None) -> None:
        resolved_api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not resolved_api_key:
            raise ValueError("GEMINI_API_KEY is not set. Add it to your .env file.")

        self.model = model or os.getenv("GEMINI_MODEL", DEFAULT_GEMINI_MODEL)
        try:
            genai.configure(api_key=resolved_api_key)
            self._client = genai.GenerativeModel(self.model)
        except Exception as error:
            raise RuntimeError(
                "Unable to initialize the Gemini client. Check your API key and model configuration."
            ) from error

    def generate_text(self, prompt: str) -> str:
        """
        Send a prompt to the LLM and return the generated text.
        """
        try:
            response = self._client.generate_content(prompt)
        except Exception as error:
            raise RuntimeError(
                "Gemini API request failed. Please verify your API key, model, and network access."
            ) from error

        response_text = (getattr(response, "text", "") or "").strip()
        if not response_text:
            raise ValueError("LLM returned an empty response.")

        return response_text
